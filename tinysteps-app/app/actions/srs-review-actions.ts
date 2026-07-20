"use server";

import { createEmptyCard, Rating } from "ts-fsrs";
import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";
import { getVocabById } from "@/lib/content/vocabulary-loader";
import { getScheduler } from "@/lib/srs/fsrs-scheduler";
import { rowToCard, cardToRow, type SrsCardRow } from "@/lib/srs/card-mapping";
import { isReviewRating } from "@/lib/srs/review-types";

const RATING_BY_VALUE = {
  1: Rating.Again,
  2: Rating.Hard,
  3: Rating.Good,
  4: Rating.Easy,
} as const;

const CARD_COLUMNS =
  "due, stability, difficulty, elapsed_days, scheduled_days, learning_steps, reps, lapses, state, last_review";

/**
 * Apply a rating to a vocab card. Lazily creates the card on first review, computes the
 * next schedule server-side via ts-fsrs, persists it, then records the day's activity.
 * `queueEmptied` = this was the last card in the session (feeds the streak rule).
 */
export async function submitReview(vocabId: string, rating: number, queueEmptied: boolean) {
  if (!isReviewRating(rating)) throw new Error("Invalid rating");
  if (!getVocabById(vocabId)) throw new Error("Unknown vocab");

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const now = new Date();

  const { data: existing, error: readError } = await supabase
    .from("srs_cards")
    .select(CARD_COLUMNS)
    .eq("user_id", user.id)
    .eq("vocab_id", vocabId)
    .maybeSingle();
  if (readError) throw new Error("Failed to read card");

  const card = existing ? rowToCard(existing as unknown as SrsCardRow) : createEmptyCard(now);
  const { card: next } = getScheduler().next(card, now, RATING_BY_VALUE[rating]);

  // Upsert without created_at: inserts keep the DB default (today = introduction day
  // for the new-card quota); updates leave the original created_at untouched.
  const { error: writeError } = await supabase
    .from("srs_cards")
    .upsert(
      { user_id: user.id, vocab_id: vocabId, ...cardToRow(next) },
      { onConflict: "user_id, vocab_id" },
    );
  if (writeError) throw new Error("Failed to save review");

  // Atomic per-day counter + streak flag. Runs after the card's due moved forward so
  // the RPC's "due cards remaining" check does not count the card just answered.
  const { error: activityError } = await supabase.rpc("record_review_activity", {
    p_queue_emptied: queueEmptied,
  });
  if (activityError) console.error("record_review_activity failed", activityError);

  // Refresh the dashboard's due-today count / streak on next visit.
  revalidatePath("/dashboard");

  return { ok: true as const };
}
