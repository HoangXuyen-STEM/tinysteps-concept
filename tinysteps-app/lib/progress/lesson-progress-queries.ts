import "server-only";
import { createClient } from "@/utils/supabase/server";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import type { Level } from "@/lib/types/content-types";

export type LessonProgress = {
  lesson_id: string;
  status: "not_started" | "in_progress" | "completed";
  score: number | null;
  completed_at: string | null;
};

export async function getLessonProgress(lessonId: string): Promise<LessonProgress | null> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;

  const { data } = await supabase
    .from("lesson_progress")
    .select("lesson_id, status, score, completed_at")
    .eq("user_id", user.id)
    .eq("lesson_id", lessonId)
    .single();

  return data as LessonProgress | null;
}

export async function getLevelProgress(level: Level): Promise<Record<string, LessonProgress>> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return {};

  const lessons = getLessonsByLevel(level);
  const lessonIds = lessons.map((l) => l.id);
  if (lessonIds.length === 0) return {};

  const { data } = await supabase
    .from("lesson_progress")
    .select("lesson_id, status, score, completed_at")
    .eq("user_id", user.id)
    .in("lesson_id", lessonIds);

  const result: Record<string, LessonProgress> = {};
  if (data) {
    for (const row of data) {
      result[row.lesson_id] = row as LessonProgress;
    }
  }
  return result;
}

export async function getCompletedCountByLevel(): Promise<Record<Level, number>> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  const counts: Record<Level, number> = { starters: 0, movers: 0, flyers: 0, ket: 0, pet: 0 };
  
  if (!user) return counts;

  const { data } = await supabase
    .from("lesson_progress")
    .select("lesson_id")
    .eq("user_id", user.id)
    .eq("status", "completed");

  if (!data) return counts;

  const levels: Level[] = ["starters", "movers", "flyers", "ket", "pet"];
  const lessonToLevel = new Map<string, Level>();
  for (const l of levels) {
    for (const lesson of getLessonsByLevel(l)) {
      lessonToLevel.set(lesson.id, l);
    }
  }

  for (const row of data) {
    const level = lessonToLevel.get(row.lesson_id);
    if (level) {
      counts[level]++;
    }
  }

  return counts;
}
