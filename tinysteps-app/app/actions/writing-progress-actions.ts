"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";
import { getWritingExercise } from "@/lib/content/writing-loader";
import { checkWritingAnswers, type WritingAnswer } from "@/lib/writing/check-writing-answers";
import { canOpenWriting } from "@/lib/access/paid-access";

export async function startWriting(writingId: string) {
  const exercise = getWritingExercise(writingId);
  if (!exercise) throw new Error("Writing exercise not found");
  if (!(await canOpenWriting(writingId))) throw new Error("Writing exercise is locked");

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  const { data: existing, error: readError } = await supabase
    .from("writing_progress")
    .select("status")
    .eq("user_id", user.id)
    .eq("writing_id", writingId)
    .maybeSingle();
  if (readError) {
    console.error("startWriting: failed to read progress", readError);
    return;
  }
  if (existing) return;

  const { error } = await supabase.from("writing_progress").insert({
    user_id: user.id,
    writing_id: writingId,
    status: "in_progress",
    updated_at: new Date().toISOString(),
  });
  if (error) console.error("startWriting: failed to create progress", error);
}

export async function submitWritingAnswers(writingId: string, answers: WritingAnswer[]) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const exercise = getWritingExercise(writingId);
  if (!exercise) throw new Error("Writing exercise not found");
  if (!(await canOpenWriting(writingId))) throw new Error("Writing exercise is locked");
  const checked = checkWritingAnswers(exercise, answers);

  const { error } = await supabase.rpc("record_writing_attempt", {
    p_writing_id: writingId,
    p_score: checked.score,
  });
  if (error) {
    console.error("Failed to save writing progress", error);
    throw new Error("Failed to save writing progress");
  }

  revalidatePath("/writing");
  revalidatePath(`/writing/${exercise.level}`);
  return checked;
}
