// Asia/Ho_Chi_Minh day-boundary math. Vietnam is a fixed UTC+7 (no DST since 1975),
// so the offset is constant and we can compute day boundaries without a tz library.
// Kept pure (no server-only, no I/O) so it is unit-testable and shareable.

const HCM_OFFSET_MS = 7 * 60 * 60 * 1000;

/** The UTC instants bounding the HCM calendar day that `now` falls in: [start, end). */
export function hcmDayRangeUtc(now: Date = new Date()): { start: Date; end: Date } {
  const shifted = new Date(now.getTime() + HCM_OFFSET_MS);
  const startUtcMs =
    Date.UTC(shifted.getUTCFullYear(), shifted.getUTCMonth(), shifted.getUTCDate()) -
    HCM_OFFSET_MS;
  return {
    start: new Date(startUtcMs),
    end: new Date(startUtcMs + 24 * 60 * 60 * 1000),
  };
}

/** The HCM calendar date as "YYYY-MM-DD" — same textual form Postgres `date` columns
 * return over PostgREST, so this can be compared directly against `daily_activity.activity_date`. */
export function hcmDateString(date: Date = new Date()): string {
  const shifted = new Date(date.getTime() + HCM_OFFSET_MS);
  const y = shifted.getUTCFullYear();
  const m = String(shifted.getUTCMonth() + 1).padStart(2, "0");
  const d = String(shifted.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
