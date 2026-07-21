import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  activateAccessSchema,
  revokeAccessSchema,
  searchUserSchema,
} from "../paid-access-admin-schemas";

// The RPC layer: a single spy stands in for supabase.rpc(name, params). Tests queue the
// result the DB function would return and assert the exact name + params sent.
const rpcSpy = vi.fn();

vi.mock("@/utils/supabase/server", () => ({
  createClient: () => Promise.resolve({ rpc: rpcSpy }),
}));

// Imported after the mock is registered.
import { activatePaidAccess, revokePaidAccess, getLearnerAccessState } from "../paid-access-admin";

beforeEach(() => {
  vi.clearAllMocks();
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
  it("calls the activate RPC with the mapped params and returns the row", async () => {
    rpcSpy.mockResolvedValue({
      data: { user_id: "u1", revoked_at: null, amount_vnd: 199000 },
      error: null,
    });

    const row = await activatePaidAccess({
      userId: "u1",
      amountVnd: 199000,
      transferRef: "R1",
      note: "early-bird",
    });

    expect(rpcSpy).toHaveBeenCalledWith("admin_activate_paid_access", {
      p_user_id: "u1",
      p_amount_vnd: 199000,
      p_transfer_ref: "R1",
      p_note: "early-bird",
    });
    expect(row).toMatchObject({ user_id: "u1", revoked_at: null });
  });

  it("throws when the RPC returns an error (forbidden / db failure)", async () => {
    rpcSpy.mockResolvedValue({ data: null, error: { message: "not authorized" } });
    await expect(
      activatePaidAccess({ userId: "u1", amountVnd: 1, transferRef: "R1", note: "" }),
    ).rejects.toBeTruthy();
  });
});

describe("revokePaidAccess", () => {
  it("returns ok with the updated row on success", async () => {
    rpcSpy.mockResolvedValue({
      data: { ok: true, access: { user_id: "u1", revoked_at: "2026-07-21T00:00:00Z" } },
      error: null,
    });

    const result = await revokePaidAccess({ userId: "u1", reason: "refund late" });

    expect(rpcSpy).toHaveBeenCalledWith("admin_revoke_paid_access", {
      p_user_id: "u1",
      p_reason: "refund late",
    });
    expect(result).toEqual({ ok: true, access: { user_id: "u1", revoked_at: "2026-07-21T00:00:00Z" } });
  });

  it("passes through not_found from the RPC", async () => {
    rpcSpy.mockResolvedValue({ data: { ok: false, reason: "not_found" }, error: null });
    const result = await revokePaidAccess({ userId: "u1", reason: "refund" });
    expect(result).toEqual({ ok: false, reason: "not_found" });
  });

  it("passes through already_revoked from the RPC", async () => {
    rpcSpy.mockResolvedValue({ data: { ok: false, reason: "already_revoked" }, error: null });
    const result = await revokePaidAccess({ userId: "u1", reason: "refund" });
    expect(result).toEqual({ ok: false, reason: "already_revoked" });
  });
});

describe("getLearnerAccessState", () => {
  it("returns found:false when the RPC yields no rows", async () => {
    rpcSpy.mockResolvedValue({ data: [], error: null });
    expect(await getLearnerAccessState("ghost@example.com")).toEqual({ found: false });
  });

  it("returns the learner with access:null when no grant exists", async () => {
    rpcSpy.mockResolvedValue({
      data: [{ user_id: "u1", email: "owner@example.com", access_exists: false }],
      error: null,
    });
    const state = await getLearnerAccessState("owner@example.com");
    expect(state).toEqual({ found: true, userId: "u1", email: "owner@example.com", access: null });
  });

  it("maps the joined columns into the access row when a grant exists", async () => {
    rpcSpy.mockResolvedValue({
      data: [
        {
          user_id: "u1",
          email: "owner@example.com",
          access_exists: true,
          granted_at: "2026-07-01T00:00:00Z",
          amount_vnd: 199000,
          transfer_ref: "R1",
          note: "early-bird",
          revoked_at: null,
        },
      ],
      error: null,
    });

    const state = await getLearnerAccessState("owner@example.com");
    expect(state).toMatchObject({
      found: true,
      userId: "u1",
      email: "owner@example.com",
      access: { user_id: "u1", amount_vnd: 199000, transfer_ref: "R1", revoked_at: null },
    });
  });

  it("throws when the RPC returns an error (non-admin caller is rejected by the DB)", async () => {
    rpcSpy.mockResolvedValue({ data: null, error: { message: "not authorized" } });
    await expect(getLearnerAccessState("owner@example.com")).rejects.toBeTruthy();
  });
});
