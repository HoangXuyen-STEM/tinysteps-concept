import { describe, it, expect, vi, beforeEach } from "vitest";

// vi.mock is hoisted above these declarations, so the mock fns must be hoisted too or the
// factory would close over uninitialised consts.
const {
  mockGetAdminIdentity,
  mockGetLearnerAccessState,
  mockActivatePaidAccess,
  mockRevokePaidAccess,
} = vi.hoisted(() => ({
  mockGetAdminIdentity: vi.fn(),
  mockGetLearnerAccessState: vi.fn(),
  mockActivatePaidAccess: vi.fn(),
  mockRevokePaidAccess: vi.fn(),
}));

vi.mock("@/lib/admin/admin-auth", () => ({
  getAdminIdentity: mockGetAdminIdentity,
}));

vi.mock("@/lib/admin/paid-access-admin", () => ({
  getLearnerAccessState: mockGetLearnerAccessState,
  activatePaidAccess: mockActivatePaidAccess,
  revokePaidAccess: mockRevokePaidAccess,
}));

vi.mock("@/utils/supabase/admin", () => ({
  AdminConfigError: class AdminConfigError extends Error {},
}));

import {
  searchUserAction,
  activateAccessAction,
  revokeAccessAction,
} from "../admin-actions";

const form = (entries: Record<string, string>) => {
  const fd = new FormData();
  for (const [k, v] of Object.entries(entries)) fd.set(k, v);
  return fd;
};

const UUID = "11111111-1111-4111-8111-111111111111";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("authorization is enforced on every operation", () => {
  it("search refuses a non-admin without touching the service", async () => {
    mockGetAdminIdentity.mockResolvedValue(null);
    const state = await searchUserAction({}, form({ email: "learner@example.com" }));
    expect(state.error).toBeTruthy();
    expect(mockGetLearnerAccessState).not.toHaveBeenCalled();
  });

  it("activate refuses a non-admin without writing", async () => {
    mockGetAdminIdentity.mockResolvedValue(null);
    const state = await activateAccessAction(
      {},
      form({ userId: UUID, email: "l@example.com", amountVnd: "199000", transferRef: "R1" }),
    );
    expect(state.error).toBeTruthy();
    expect(mockActivatePaidAccess).not.toHaveBeenCalled();
  });

  it("revoke refuses a non-admin without writing", async () => {
    mockGetAdminIdentity.mockResolvedValue(null);
    const state = await revokeAccessAction(
      {},
      form({ userId: UUID, email: "l@example.com", reason: "refund" }),
    );
    expect(state.error).toBeTruthy();
    expect(mockRevokePaidAccess).not.toHaveBeenCalled();
  });
});

describe("authorized admin flows", () => {
  beforeEach(() => {
    mockGetAdminIdentity.mockResolvedValue({ userId: "admin-1", email: "owner@example.com" });
  });

  it("rejects invalid activate input before writing", async () => {
    const state = await activateAccessAction(
      {},
      form({ userId: UUID, email: "l@example.com", amountVnd: "-1", transferRef: "R1" }),
    );
    expect(state.error).toBeTruthy();
    expect(mockActivatePaidAccess).not.toHaveBeenCalled();
  });

  it("activates and returns the refreshed learner state", async () => {
    mockActivatePaidAccess.mockResolvedValue({ user_id: "u1" });
    mockGetLearnerAccessState.mockResolvedValue({ found: true, userId: "u1", email: "l@example.com", access: null });

    const state = await activateAccessAction(
      {},
      form({ userId: UUID, email: "l@example.com", amountVnd: "199000", transferRef: "R1", note: "early-bird" }),
    );

    expect(mockActivatePaidAccess).toHaveBeenCalledWith(
      expect.objectContaining({ userId: UUID, amountVnd: 199000, transferRef: "R1", note: "early-bird" }),
    );
    expect(state.message).toBeTruthy();
    expect(state.learner).toBeTruthy();
  });

  it("surfaces a friendly message when revoke finds nothing to revoke", async () => {
    mockRevokePaidAccess.mockResolvedValue({ ok: false, reason: "not_found" });
    mockGetLearnerAccessState.mockResolvedValue({ found: true, userId: "u1", email: "l@example.com", access: null });

    const state = await revokeAccessAction(
      {},
      form({ userId: UUID, email: "l@example.com", reason: "refund" }),
    );
    expect(state.error).toContain("Không tìm thấy");
  });
});
