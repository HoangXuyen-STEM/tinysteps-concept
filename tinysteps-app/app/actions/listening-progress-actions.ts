"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";
import { getListeningExercise } from "@/lib/content/listening-loader";
import { checkListeningAnswers, type ListeningAnswer } from "@/lib/listening/check-listening-answers";
import { canOpenListening } from "@/lib/access/paid-access";

export async function startListening(listeningId: string) {
  const exercise = getListeningExercise(listeningId);
  if (!exercise) throw new Error("Listening exercise not found");
  if (!(await canOpenListening(listeningId))) throw new Error("Listening exercise is locked");

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  const { data: existing, error: readError } = await supabase
    .from("listening_progress")
    .select("status")
    .eq("user_id", user.id)
    .eq("listening_id", listeningId)
    .maybeSingle();
  if (readError) {
    console.error("startListening: failed to read progress", readError);
    return;
  }
  if (existing) return;

  const { error } = await supabase.from("listening_progress").insert({
    user_id: user.id,
    listening_id: listeningId,
    status: "in_progress",
    updated_at: new Date().toISOString(),
  });
  if (error) console.error("startListening: failed to create progress", error);
}

/**
 * Submits answers AND grades them server-side (the client never has accepted_answers).
 * On completion (>=80%) also returns the transcript so the player can reveal it —
 * transcript stays out of every response before this point.
 */
export async function submitListeningAnswers(listeningId: string, answers: ListeningAnswer[]) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const exercise = getListeningExercise(listeningId);
  if (!exercise) throw new Error("Listening exercise not found");
  if (!(await canOpenListening(listeningId))) throw new Error("Listening exercise is locked");
  const checked = checkListeningAnswers(exercise, answers);

  const { error } = await supabase.rpc("record_listening_attempt", {
    p_listening_id: listeningId,
    p_score: checked.score,
  });
  if (error) {
    console.error("Failed to save listening progress", error);
    throw new Error("Failed to save listening progress");
  }

  revalidatePath("/listening");
  revalidatePath(`/listening/${exercise.level}`);
  return { ...checked, transcript: exercise.transcript };
}
