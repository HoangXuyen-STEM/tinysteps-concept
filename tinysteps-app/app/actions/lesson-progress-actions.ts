"use server";

import { createClient } from "@/utils/supabase/server";
import { getLesson } from "@/lib/content/lesson-loader";
import { computeScore, type ExerciseAnswer } from "@/lib/exercises/check-answer";
import { revalidatePath } from "next/cache";

export async function startLesson(lessonId: string) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;

  // maybeSingle(): null+no-error for "no row yet" (a real, expected first-open case),
  // vs. an actual error for network/DB failures. single() conflates the two — a
  // transient read failure would fall through to the upsert below and downgrade an
  // already-completed lesson back to in_progress. Fail closed instead: on any real
  // read error, do nothing rather than risk clobbering existing progress.
  const { data: existing, error: readError } = await supabase
    .from("lesson_progress")
    .select("status")
    .eq("user_id", user.id)
    .eq("lesson_id", lessonId)
    .maybeSingle();

  if (readError) {
    console.error("startLesson: failed to read existing progress; not writing", readError);
    return;
  }

  // Already in_progress or completed — never downgrade a later/duplicate startLesson
  // call (e.g. a slow fire-and-forget request that resolves after the lesson finished).
  if (existing && existing.status !== "not_started") return;

  const { error: writeError } = await supabase
    .from("lesson_progress")
    .upsert(
      {
        user_id: user.id,
        lesson_id: lessonId,
        status: "in_progress",
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id, lesson_id" },
    );

  if (writeError) {
    console.error("startLesson: failed to upsert in_progress status", writeError);
  }
}

export async function submitLessonAnswers(lessonId: string, answers: ExerciseAnswer[]) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const lesson = getLesson(lessonId);
  if (!lesson) throw new Error("Lesson not found");

  const { score, correctCount, totalItems } = computeScore(answers, lesson.exercises);

  const { error } = await supabase.rpc("complete_lesson_rpc", {
    p_lesson_id: lessonId,
    p_score: score,
  });

  if (error) {
    console.error("Failed to submit lesson answers:", error);
    throw new Error("Failed to save progress");
  }

  // Refresh badges and completion counts across the app
  revalidatePath("/lessons");
  revalidatePath(`/lessons/${lesson.level}`);

  return { score, correctCount, totalItems };
}
