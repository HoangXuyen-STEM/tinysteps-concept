import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  isFreeLesson,
  hasPaidAccess,
  canOpenLesson,
  FREE_LESSON_IDS,
  FREE_WRITING_IDS,
  isFreeWriting,
  canOpenWriting,
  FREE_LISTENING_IDS,
  isFreeListening,
  canOpenListening,
} from "../paid-access";

const mockGetClaims = vi.fn();
const mockMaybeSingle = vi.fn();

// Chainable builder matching the query in paid-access.ts:
// .from().select().eq().is().maybeSingle()
const mockFrom = vi.fn(() => ({
  select: vi.fn(() => ({
    eq: vi.fn(() => ({
      is: vi.fn(() => ({ maybeSingle: mockMaybeSingle })),
    })),
  })),
}));

vi.mock("@/utils/supabase/server", () => ({
  createClient: vi.fn(() => ({
    auth: { getClaims: mockGetClaims },
    from: mockFrom,
  })),
}));

const signedInAs = (userId: string) =>
  mockGetClaims.mockResolvedValue({ data: { claims: { sub: userId } } });

const signedOut = () => mockGetClaims.mockResolvedValue({ data: null });

const grantRow = { data: { user_id: "user-1" }, error: null };
const noGrant = { data: null, error: null };

beforeEach(() => {
  vi.clearAllMocks();
});

describe("isFreeLesson", () => {
  it("opens exactly the three trial lessons", () => {
    expect(FREE_LESSON_IDS).toHaveLength(3);
    for (const id of FREE_LESSON_IDS) {
      expect(isFreeLesson(id)).toBe(true);
    }
  });

  it("locks the lesson right after the trial", () => {
    expect(isFreeLesson("starters_lesson_004")).toBe(false);
  });

  it("locks other levels that share a lesson number with a free one", () => {
    // Lesson ids are level-scoped; a bare number would collide across all five levels.
    expect(isFreeLesson("movers_lesson_001")).toBe(false);
    expect(isFreeLesson("pet_lesson_001")).toBe(false);
  });
});

describe("hasPaidAccess", () => {
  it("is true when an unrevoked grant exists", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(grantRow);
    expect(await hasPaidAccess()).toBe(true);
  });

  it("is false when the user has no grant", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(noGrant);
    expect(await hasPaidAccess()).toBe(false);
  });

  it("is false for signed-out callers without querying", async () => {
    signedOut();
    expect(await hasPaidAccess()).toBe(false);
    expect(mockFrom).not.toHaveBeenCalled();
  });

  it("fails closed when the lookup errors", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue({ data: null, error: { message: "boom" } });
    expect(await hasPaidAccess()).toBe(false);
  });
});

describe("canOpenLesson", () => {
  it("opens a free lesson without checking payment", async () => {
    signedOut();
    expect(await canOpenLesson("starters_lesson_001")).toBe(true);
    expect(mockFrom).not.toHaveBeenCalled();
  });

  it("blocks a paid lesson for an unpaid user", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(noGrant);
    expect(await canOpenLesson("starters_lesson_004")).toBe(false);
  });

  it("opens a paid lesson for a paid user", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(grantRow);
    expect(await canOpenLesson("flyers_lesson_020")).toBe(true);
  });
});

describe("writing access", () => {
  it("opens exactly the first Starters writing exercise for free", () => {
    expect(FREE_WRITING_IDS).toEqual(["starters_writing_001"]);
    expect(isFreeWriting("starters_writing_001")).toBe(true);
    expect(isFreeWriting("starters_writing_002")).toBe(false);
    expect(isFreeWriting("movers_writing_001")).toBe(false);
  });

  it("does not query payment for the free writing exercise", async () => {
    signedOut();
    expect(await canOpenWriting("starters_writing_001")).toBe(true);
    expect(mockFrom).not.toHaveBeenCalled();
  });

  it("requires an active grant for a paid writing exercise", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(noGrant);
    expect(await canOpenWriting("pet_writing_005")).toBe(false);
  });
});

describe("listening access", () => {
  it("opens exactly the first Starters listening exercise for free", () => {
    expect(FREE_LISTENING_IDS).toEqual(["starters_listening_001"]);
    expect(isFreeListening("starters_listening_001")).toBe(true);
    expect(isFreeListening("starters_listening_002")).toBe(false);
    expect(isFreeListening("movers_listening_001")).toBe(false);
  });

  it("does not query payment for the free listening exercise", async () => {
    signedOut();
    expect(await canOpenListening("starters_listening_001")).toBe(true);
    expect(mockFrom).not.toHaveBeenCalled();
  });

  it("requires an active grant for a paid listening exercise", async () => {
    signedInAs("user-1");
    mockMaybeSingle.mockResolvedValue(noGrant);
    expect(await canOpenListening("pet_listening_003")).toBe(false);
  });
});
