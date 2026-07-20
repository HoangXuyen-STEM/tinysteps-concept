import "server-only";
import { createClient } from "@/utils/supabase/server";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import { levels, type Level } from "@/lib/types/content-types";
import { hcmDateString } from "@/lib/srs/hcm-day";
import { computeStreak, type StreakInfo } from "./streak-calc";
import { getCompletedCountByLevel } from "./lesson-progress-queries";

export type LevelProgressSummary = Record<Level, { completed: number; total: number }>;

export async function getLevelProgressSummary(): Promise<LevelProgressSummary> {
  const completed = await getCompletedCountByLevel();
  const summary = {} as LevelProgressSummary;
  for (const level of levels) {
    summary[level] = { completed: completed[level], total: getLessonsByLevel(level).length };
  }
  return summary;
}

export async function getDueTodayCount(): Promise<number> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return 0;

  const { count } = await supabase
    .from("srs_cards")
    .select("*", { count: "exact", head: true })
    .eq("user_id", user.id)
    .lte("due", new Date().toISOString());

  return count ?? 0;
}

export async function getStreak(): Promise<StreakInfo> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { count: 0, activeToday: false, nudge: false };

  const { data } = await supabase
    .from("daily_activity")
    .select("activity_date")
    .eq("user_id", user.id)
    .eq("learning_day", true)
    .order("activity_date", { ascending: false })
    .limit(400);

  const learningDates = new Set((data ?? []).map((row) => row.activity_date as string));
  const now = new Date();
  const todayStr = hcmDateString(now);
  const yesterdayStr = hcmDateString(new Date(now.getTime() - 24 * 60 * 60 * 1000));

  return computeStreak(learningDates, todayStr, yesterdayStr);
}

export type Profile = { displayName: string | null; currentLevel: Level | null };

/** One profile read shared by the greeting and the "continue learning" CTA, so the
 * dashboard doesn't issue two near-identical queries for the same row. */
export async function getProfile(): Promise<Profile> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { displayName: null, currentLevel: null };

  const { data } = await supabase
    .from("profiles")
    .select("display_name, current_level")
    .eq("id", user.id)
    .maybeSingle();

  return {
    displayName: (data?.display_name as string | null) ?? null,
    currentLevel: (data?.current_level as Level | null) ?? null,
  };
}

export type NextLesson = { level: Level; id: string; title: string };

/** First not-completed lesson (by order) in the given level, for the "Tiếp tục học"
 * CTA. Null when there's no level yet, or that level is fully completed (dashboard
 * falls back to a generic "browse lessons" link). */
export async function getNextLesson(level: Level | null): Promise<NextLesson | null> {
  if (!level) return null;

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;

  const lessons = getLessonsByLevel(level);
  if (lessons.length === 0) return null;

  const { data: completedRows } = await supabase
    .from("lesson_progress")
    .select("lesson_id")
    .eq("user_id", user.id)
    .eq("status", "completed")
    .in(
      "lesson_id",
      lessons.map((l) => l.id),
    );
  const completedIds = new Set((completedRows ?? []).map((r) => r.lesson_id as string));

  const next = lessons.find((lesson) => !completedIds.has(lesson.id));
  return next ? { level, id: next.id, title: next.title } : null;
}
