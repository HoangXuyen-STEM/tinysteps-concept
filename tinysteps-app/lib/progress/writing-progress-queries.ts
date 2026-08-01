import "server-only";

import { createClient } from "@/utils/supabase/server";
import { getWritingByLevel } from "@/lib/content/writing-loader";
import type { Level } from "@/lib/types/content-types";

export type WritingProgress = {
  writing_id: string;
  status: "in_progress" | "completed";
  best_score: number | null;
  completed_at: string | null;
};

export async function getWritingProgress(writingId: string): Promise<WritingProgress | null> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const { data } = await supabase
    .from("writing_progress")
    .select("writing_id, status, best_score, completed_at")
    .eq("user_id", user.id)
    .eq("writing_id", writingId)
    .maybeSingle();
  return data as WritingProgress | null;
}

export async function getWritingLevelProgress(level: Level): Promise<Record<string, WritingProgress>> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return {};

  const ids = getWritingByLevel(level).map((exercise) => exercise.id);
  const { data } = await supabase
    .from("writing_progress")
    .select("writing_id, status, best_score, completed_at")
    .eq("user_id", user.id)
    .in("writing_id", ids);

  return Object.fromEntries((data ?? []).map((row) => [row.writing_id, row as WritingProgress]));
}

export async function getWritingCompletedCounts(): Promise<Record<Level, number>> {
  const counts: Record<Level, number> = { starters: 0, movers: 0, flyers: 0, ket: 0, pet: 0 };
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return counts;

  const { data } = await supabase
    .from("writing_progress")
    .select("writing_id")
    .eq("user_id", user.id)
    .eq("status", "completed");
  const idToLevel = new Map<string, Level>();
  for (const level of Object.keys(counts) as Level[]) {
    for (const exercise of getWritingByLevel(level)) idToLevel.set(exercise.id, level);
  }
  for (const row of data ?? []) {
    const level = idToLevel.get(row.writing_id as string);
    if (level) counts[level]++;
  }
  return counts;
}
