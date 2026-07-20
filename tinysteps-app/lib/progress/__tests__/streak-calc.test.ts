import { describe, it, expect } from "vitest";
import { computeStreak } from "../streak-calc";

const TODAY = "2026-07-14";
const YESTERDAY = "2026-07-13";

describe("computeStreak", () => {
  it("is 0/0 when there is no activity at all", () => {
    const result = computeStreak(new Set(), TODAY, YESTERDAY);
    expect(result).toEqual({ count: 0, activeToday: false, nudge: false });
  });

  it("counts consecutive days ending today when today is active", () => {
    const dates = new Set(["2026-07-12", "2026-07-13", "2026-07-14"]);
    expect(computeStreak(dates, TODAY, YESTERDAY)).toEqual({
      count: 3,
      activeToday: true,
      nudge: false,
    });
  });

  it("shows the streak alive from yesterday, with a nudge, when today is not yet active", () => {
    const dates = new Set(["2026-07-11", "2026-07-12", "2026-07-13"]);
    expect(computeStreak(dates, TODAY, YESTERDAY)).toEqual({
      count: 3,
      activeToday: false,
      nudge: true,
    });
  });

  it("resets to 0 after a gap (today and yesterday both missing)", () => {
    // Active two days ago, but not yesterday or today — the streak is broken.
    const dates = new Set(["2026-07-12"]);
    expect(computeStreak(dates, TODAY, YESTERDAY)).toEqual({
      count: 0,
      activeToday: false,
      nudge: false,
    });
  });

  it("stops counting at the first gap when walking backward", () => {
    // 07-14 and 07-13 active, but 07-12 missing, then 07-11 active again — the
    // older isolated day must NOT be added to the current streak.
    const dates = new Set(["2026-07-11", "2026-07-13", "2026-07-14"]);
    expect(computeStreak(dates, TODAY, YESTERDAY).count).toBe(2);
  });

  it("a single active day today counts as a streak of 1", () => {
    const dates = new Set([TODAY]);
    expect(computeStreak(dates, TODAY, YESTERDAY)).toEqual({
      count: 1,
      activeToday: true,
      nudge: false,
    });
  });
});
