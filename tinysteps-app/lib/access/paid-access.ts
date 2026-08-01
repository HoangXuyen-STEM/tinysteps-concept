import "server-only";
import { createClient } from "@/utils/supabase/server";

/**
 * Lessons anyone can open without paying. Three real lessons is enough for a teacher
 * to judge the pace, the audio and the exercise style before transferring money to a
 * stranger — the main objection this trial exists to answer.
 */
export const FREE_LESSON_IDS: readonly string[] = [
  "starters_lesson_001",
  "starters_lesson_002",
  "starters_lesson_003",
];

export const isFreeLesson = (lessonId: string) => FREE_LESSON_IDS.includes(lessonId);

export const FREE_WRITING_IDS: readonly string[] = ["starters_writing_001"];
export const isFreeWriting = (writingId: string) => FREE_WRITING_IDS.includes(writingId);

/**
 * True when the signed-in user has an active paid grant. A row with `revoked_at` set
 * (refund) grants nothing. Returns false for signed-out callers rather than throwing,
 * so callers can treat "no access" uniformly.
 */
export async function hasPaidAccess(): Promise<boolean> {
  const supabase = await createClient();
  const { data: claims } = await supabase.auth.getClaims();
  const userId = claims?.claims?.sub;
  if (!userId) return false;

  const { data, error } = await supabase
    .from("paid_access")
    .select("user_id")
    .eq("user_id", userId)
    .is("revoked_at", null)
    .maybeSingle();

  // Fail closed: a lookup error must not hand out paid content.
  if (error) return false;
  return Boolean(data);
}

/** Whether this specific lesson is open to the current user. */
export async function canOpenLesson(lessonId: string): Promise<boolean> {
  if (isFreeLesson(lessonId)) return true;
  return hasPaidAccess();
}

/** Whether this specific writing exercise is open to the current user. */
export async function canOpenWriting(writingId: string): Promise<boolean> {
  if (isFreeWriting(writingId)) return true;
  return hasPaidAccess();
}
