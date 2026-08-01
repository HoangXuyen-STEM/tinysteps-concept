import "server-only";

import { createClient } from "@/utils/supabase/server";
import { getListeningByLevel } from "@/lib/content/listening-loader";
import type { Level } from "@/lib/types/content-types";

export type ListeningProgress = {
  listening_id: string;
  status: "in_progress" | "completed";
  best_score: number | null;
  completed_at: string | null;
};

export async function getListeningProgress(listeningId: string): Promise<ListeningProgress | null> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const { data } = await supabase
    .from("listening_progress")
    .select("listening_id, status, best_score, completed_at")
    .eq("user_id", user.id)
    .eq("listening_id", listeningId)
    .maybeSingle();
  return data as ListeningProgress | null;
}

export async function getListeningLevelProgress(level: Level): Promise<Record<string, ListeningProgress>> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return {};

  const ids = getListeningByLevel(level).map((exercise) => exercise.id);
  const { data } = await supabase
    .from("listening_progress")
    .select("listening_id, status, best_score, completed_at")
    .eq("user_id", user.id)
    .in("listening_id", ids);

  return Object.fromEntries((data ?? []).map((row) => [row.listening_id, row as ListeningProgress]));
}

export async function getListeningCompletedCounts(): Promise<Record<Level, number>> {
  const counts: Record<Level, number> = { starters: 0, movers: 0, flyers: 0, ket: 0, pet: 0 };
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return counts;

  const { data } = await supabase
    .from("listening_progress")
    .select("listening_id")
    .eq("user_id", user.id)
    .eq("status", "completed");
  const idToLevel = new Map<string, Level>();
  for (const level of Object.keys(counts) as Level[]) {
    for (const exercise of getListeningByLevel(level)) idToLevel.set(exercise.id, level);
  }
  for (const row of data ?? []) {
    const level = idToLevel.get(row.listening_id as string);
    if (level) counts[level]++;
  }
  return counts;
}
