// Pure streak math, separated from the Supabase query so it is unit-testable without
// a DB. Streak = consecutive HCM learning days ending today, or ending yesterday if
// today has no activity yet (shown with a nudge instead of resetting to 0).

export type StreakInfo = {
  count: number;
  /** Today (HCM) already qualifies as a learning day. */
  activeToday: boolean;
  /** Streak is alive from yesterday but today isn't logged yet — nudge the user. */
  nudge: boolean;
};

/**
 * @param learningDates "YYYY-MM-DD" HCM dates where learning_day = true.
 * @param todayStr HCM date string for "today".
 * @param yesterdayStr HCM date string for "today - 1".
 */
export function computeStreak(
  learningDates: ReadonlySet<string>,
  todayStr: string,
  yesterdayStr: string,
): StreakInfo {
  const activeToday = learningDates.has(todayStr);
  const anchor = activeToday ? todayStr : yesterdayStr;

  if (!learningDates.has(anchor)) {
    return { count: 0, activeToday: false, nudge: false };
  }

  // Walk back one HCM day at a time from the anchor, counting consecutive hits.
  let count = 0;
  let cursor = new Date(`${anchor}T00:00:00.000Z`);
  while (learningDates.has(toDateStr(cursor))) {
    count++;
    cursor = new Date(cursor.getTime() - 24 * 60 * 60 * 1000);
  }

  return { count, activeToday, nudge: !activeToday };
}

function toDateStr(d: Date): string {
  return d.toISOString().slice(0, 10);
}
