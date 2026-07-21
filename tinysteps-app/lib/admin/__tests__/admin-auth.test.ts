import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getAdminEmails, getAdminIdentity, isAdminAllowListConfigured } from "../admin-auth";

const mockGetClaims = vi.fn();

vi.mock("@/utils/supabase/server", () => ({
  createClient: vi.fn(() => ({ auth: { getClaims: mockGetClaims } })),
}));

const signedInAs = (sub: string, email: string) =>
  mockGetClaims.mockResolvedValue({ data: { claims: { sub, email } } });

const ORIGINAL = process.env.ADMIN_EMAILS;

beforeEach(() => {
  vi.clearAllMocks();
});
afterEach(() => {
  process.env.ADMIN_EMAILS = ORIGINAL;
});

describe("getAdminEmails", () => {
  it("parses, trims and lowercases a comma-separated list", () => {
    process.env.ADMIN_EMAILS = " Owner@Example.com , admin@example.com ,";
    expect(getAdminEmails()).toEqual(["owner@example.com", "admin@example.com"]);
  });

  it("is empty (nobody is admin) when unset", () => {
    delete process.env.ADMIN_EMAILS;
    expect(getAdminEmails()).toEqual([]);
    expect(isAdminAllowListConfigured()).toBe(false);
  });
});

describe("getAdminIdentity", () => {
  it("returns null for everyone when no allow-list is configured", async () => {
    delete process.env.ADMIN_EMAILS;
    signedInAs("user-1", "owner@example.com");
    expect(await getAdminIdentity()).toBeNull();
  });

  it("authorizes an allow-listed email regardless of casing", async () => {
    process.env.ADMIN_EMAILS = "owner@example.com";
    signedInAs("user-1", "Owner@Example.com");
    expect(await getAdminIdentity()).toEqual({ userId: "user-1", email: "owner@example.com" });
  });

  it("denies a signed-in non-admin", async () => {
    process.env.ADMIN_EMAILS = "owner@example.com";
    signedInAs("user-2", "learner@example.com");
    expect(await getAdminIdentity()).toBeNull();
  });

  it("denies a signed-out caller", async () => {
    process.env.ADMIN_EMAILS = "owner@example.com";
    mockGetClaims.mockResolvedValue({ data: null });
    expect(await getAdminIdentity()).toBeNull();
  });

  it("denies when the session carries no email claim", async () => {
    process.env.ADMIN_EMAILS = "owner@example.com";
    mockGetClaims.mockResolvedValue({ data: { claims: { sub: "user-1" } } });
    expect(await getAdminIdentity()).toBeNull();
  });
});
