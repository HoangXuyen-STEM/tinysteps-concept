import { afterEach, describe, expect, it } from "vitest";
import {
  getIllustrationCount,
  matchIllustrationKey,
  resolveMatchIllustration,
} from "../illustration-manifest";

const originalBaseUrl = process.env.NEXT_PUBLIC_ASSET_BASE_URL;

afterEach(() => {
  if (originalBaseUrl === undefined) {
    delete process.env.NEXT_PUBLIC_ASSET_BASE_URL;
  } else {
    process.env.NEXT_PUBLIC_ASSET_BASE_URL = originalBaseUrl;
  }
});

describe("matchIllustrationKey", () => {
  it("uses the lesson-wide exercise index contract", () => {
    expect(matchIllustrationKey("starters_lesson_001", 0, 1)).toBe(
      "match/starters_lesson_001/exercise-0/item-1",
    );
  });
});

describe("resolveMatchIllustration", () => {
  it("resolves an approved asset to its local public path by default", () => {
    delete process.env.NEXT_PUBLIC_ASSET_BASE_URL;
    expect(resolveMatchIllustration("starters_lesson_001", 0, 1)).toMatchObject({
      assetKey: "match/starters_lesson_001/exercise-0/item-1",
      src: "/illustrations/match/starters_lesson_001/exercise-0/item-1.webp",
    });
  });

  it("resolves against the Storage root without duplicating the bucket", () => {
    process.env.NEXT_PUBLIC_ASSET_BASE_URL = "https://example.supabase.co/storage/v1/object/public/";
    expect(resolveMatchIllustration("starters_lesson_001", 0, 1)?.src).toBe(
      "https://example.supabase.co/storage/v1/object/public/illustrations/match/starters_lesson_001/exercise-0/item-1.webp",
    );
  });

  it("returns null for an asset that is not QA-approved", () => {
    expect(resolveMatchIllustration("missing_lesson", 0, 0)).toBeNull();
  });

  it("contains every unique approved asset", () => {
    expect(getIllustrationCount()).toBe(525);
  });
});
