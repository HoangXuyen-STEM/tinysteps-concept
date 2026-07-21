import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  activateAccessSchema,
  revokeAccessSchema,
  searchUserSchema,
} from "../paid-access-admin-schemas";

// A shared queue drives the terminal query results in call order; the spies capture the
// mutation payloads so tests can assert the exact write semantics.
const dbResults: unknown[] = [];
const upsertSpy = vi.fn();
const updateSpy = vi.fn();
const listUsersSpy = vi.fn();

function builder() {
  const b: Record<string, unknown> = {};
  Object.assign(b, {
    select: vi.fn(() => b),
    eq: vi.fn(() => b),
    is: vi.fn(() => b),
    upsert: vi.fn((...args: unknown[]) => {
      upsertSpy(...args);
      return b;
    }),
    update: vi.fn((...args: unknown[]) => {
      updateSpy(...args);
      return b;
    }),
    maybeSingle: vi.fn(() => Promise.resolve(dbResults.shift())),
    single: vi.fn(() => Promise.resolve(dbResults.shift())),
  });
  return b;
}

vi.mock("@/utils/supabase/admin", () => ({
  AdminConfigError: class AdminConfigError extends Error {},
  createAdminClient: () => ({
    from: () => builder(),
    auth: { admin: { listUsers: listUsersSpy } },
  }),
}));

// Imported after the mock is registered.
import { activatePaidAccess, revokePaidAccess, getLearnerAccessState } from "../paid-access-admin";

beforeEach(() => {
  vi.clearAllMocks();
  dbResults.length = 0;
});

describe("input validation", () => {
  it("rejects a non-positive or non-integer amount", () => {
    const base = { userId: "11111111-1111-4111-8111-111111111111", transferRef: "R1", note: "" };
    expect(activateAccessSchema.safeParse({ ...base, amountVnd: 0 }).success).toBe(false);
    expect(activateAccessSchema.safeParse({ ...base, amountVnd: -5 }).success).toBe(false);
    expect(activateAccessSchema.safeParse({ ...base, amountVnd: 1.5 }).success).toBe(false);
    expect(activateAccessSchema.safeParse({ ...base, amountVnd: 199000 }).success).toBe(true);
  });

  it("requires a transfer ref and a valid uuid", () => {
    expect(
      activateAccessSchema.safeParse({ userId: "not-a-uuid", amountVnd: 1, transferRef: "R1" })
        .success,
    ).toBe(false);
    expect(
      activateAccessSchema.safeParse({
        userId: "11111111-1111-4111-8111-111111111111",
        amountVnd: 1,
        transferRef: "  ",
      }).success,
    ).toBe(false);
  });

  it("normalises email to lowercase and rejects malformed input", () => {
    expect(searchUserSchema.parse({ email: " Owner@Example.com " }).email).toBe("owner@example.com");
    expect(searchUserSchema.safeParse({ email: "nope" }).success).toBe(false);
  });

  it("requires a revoke reason", () => {
    const userId = "11111111-1111-4111-8111-111111111111";
    expect(revokeAccessSchema.safeParse({ userId, reason: "" }).success).toBe(false);
    expect(revokeAccessSchema.safeParse({ userId, reason: "refund" }).success).toBe(true);
  });
});

describe("activatePaidAccess", () => {
  it("upserts on the primary key, clearing revoked_at (re-activation updates, not duplicates)", async () => {
    dbResults.push({ data: { user_id: "u1", revoked_at: null }, error: null });

    await activatePaidAccess({ userId: "u1", amountVnd: 199000, transferRef: "R1", note: "early-bird" });

    const [row, options] = upsertSpy.mock.calls[0];
    expect(row).toMatchObject({
      user_id: "u1",
      amount_vnd: 199000,
      transfer_ref: "R1",
      note: "early-bird",
      revoked_at: null,
    });
    expect(options).toEqual({ onConflict: "user_id" });
  });
});

describe("revokePaidAccess", () => {
  it("updates an active grant with revoked_at and appends the reason to the note", async () => {
    dbResults.push({ data: { user_id: "u1", note: "early-bird", revoked_at: null }, error: null });
    dbResults.push({ data: { user_id: "u1", revoked_at: "2026-07-21T00:00:00Z" }, error: null });

    const result = await revokePaidAccess({ userId: "u1", reason: "refund late" });

    expect(result.ok).toBe(true);
    const [patch] = updateSpy.mock.calls[0];
    expect(patch.revoked_at).toBeTypeOf("string");
    expect(patch.note).toBe("early-bird | revoked: refund late");
  });

  it("returns not_found and writes nothing when there is no grant", async () => {
    dbResults.push({ data: null, error: null });
    const result = await revokePaidAccess({ userId: "u1", reason: "refund" });
    expect(result).toEqual({ ok: false, reason: "not_found" });
    expect(updateSpy).not.toHaveBeenCalled();
  });

  it("returns already_revoked and writes nothing when the grant is revoked", async () => {
    dbResults.push({ data: { user_id: "u1", revoked_at: "2026-07-01T00:00:00Z" }, error: null });
    const result = await revokePaidAccess({ userId: "u1", reason: "refund" });
    expect(result).toEqual({ ok: false, reason: "already_revoked" });
    expect(updateSpy).not.toHaveBeenCalled();
  });
});

describe("getLearnerAccessState", () => {
  it("returns found:false without querying paid_access when no user matches", async () => {
    listUsersSpy.mockResolvedValue({ data: { users: [] }, error: null });
    expect(await getLearnerAccessState("ghost@example.com")).toEqual({ found: false });
  });

  it("returns only the matched learner's access row", async () => {
    listUsersSpy.mockResolvedValue({
      data: { users: [{ id: "u1", email: "Owner@Example.com" }] },
      error: null,
    });
    dbResults.push({ data: { user_id: "u1", revoked_at: null }, error: null });

    const state = await getLearnerAccessState("owner@example.com");
    expect(state).toMatchObject({ found: true, userId: "u1", email: "Owner@Example.com" });
  });
});
