import { describe, it, expect } from "vitest";
import { hcmDayRangeUtc, hcmDateString } from "../hcm-day";

describe("hcmDayRangeUtc", () => {
  it("maps a UTC instant to its HCM (UTC+7) calendar-day bounds", () => {
    // 2026-07-14T02:00:00Z = 09:00 same day in HCM → day is 2026-07-14 HCM,
    // which starts 2026-07-13T17:00Z and ends 2026-07-14T17:00Z.
    const { start, end } = hcmDayRangeUtc(new Date("2026-07-14T02:00:00Z"));
    expect(start.toISOString()).toBe("2026-07-13T17:00:00.000Z");
    expect(end.toISOString()).toBe("2026-07-14T17:00:00.000Z");
  });

  it("rolls to the next HCM day once past 17:00Z (midnight in HCM)", () => {
    // 2026-07-14T17:30:00Z = 00:30 on 2026-07-15 HCM.
    const { start, end } = hcmDayRangeUtc(new Date("2026-07-14T17:30:00Z"));
    expect(start.toISOString()).toBe("2026-07-14T17:00:00.000Z");
    expect(end.toISOString()).toBe("2026-07-15T17:00:00.000Z");
  });

  it("keeps a late-evening HCM time inside the same HCM day", () => {
    // 2026-07-14T16:59:00Z = 23:59 on 2026-07-14 HCM (still that day).
    const { start } = hcmDayRangeUtc(new Date("2026-07-14T16:59:00Z"));
    expect(start.toISOString()).toBe("2026-07-13T17:00:00.000Z");
  });

  it("produces a 24h window", () => {
    const { start, end } = hcmDayRangeUtc(new Date("2026-03-01T08:00:00Z"));
    expect(end.getTime() - start.getTime()).toBe(24 * 60 * 60 * 1000);
  });
});

describe("hcmDateString", () => {
  it("matches the start of hcmDayRangeUtc's own day", () => {
    // hcmDateString must describe exactly the day hcmDayRangeUtc bounds — the two are
    // used together (queue quota vs. streak) and must never disagree on "today".
    const now = new Date("2026-07-14T02:00:00Z");
    expect(hcmDateString(now)).toBe("2026-07-14");
  });

  it("rolls over at the same instant hcmDayRangeUtc does (17:00Z)", () => {
    expect(hcmDateString(new Date("2026-07-14T16:59:59Z"))).toBe("2026-07-14");
    expect(hcmDateString(new Date("2026-07-14T17:00:00Z"))).toBe("2026-07-15");
  });

  it("pads single-digit month and day", () => {
    expect(hcmDateString(new Date("2026-01-05T10:00:00Z"))).toBe("2026-01-05");
  });
});
