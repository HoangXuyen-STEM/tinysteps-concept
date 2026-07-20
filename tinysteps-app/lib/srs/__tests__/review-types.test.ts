import { describe, it, expect } from "vitest";
import { isReviewRating, REVIEW_RATINGS, REVIEW_BATCH_SIZE } from "../review-types";

describe("isReviewRating", () => {
  it("accepts 1..4", () => {
    for (const r of [1, 2, 3, 4]) expect(isReviewRating(r)).toBe(true);
  });

  it("rejects out-of-range, zero, and non-integers", () => {
    for (const r of [0, 5, -1, 1.5, NaN]) expect(isReviewRating(r)).toBe(false);
  });
});

describe("REVIEW_RATINGS", () => {
  it("covers Again/Hard/Good/Easy in order with Vietnamese labels", () => {
    expect(REVIEW_RATINGS.map((r) => r.value)).toEqual([1, 2, 3, 4]);
    expect(REVIEW_RATINGS.map((r) => r.vi)).toEqual(["Lại", "Khó", "Được", "Dễ"]);
  });
});

describe("REVIEW_BATCH_SIZE", () => {
  it("is 5 (decision 4)", () => {
    expect(REVIEW_BATCH_SIZE).toBe(5);
  });
});
