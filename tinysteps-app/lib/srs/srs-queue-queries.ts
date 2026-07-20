import "server-only";
import { createClient } from "@/utils/supabase/server";
import { getVocab, getVocabById } from "@/lib/content/vocabulary-loader";
import { audioUrl } from "@/lib/content/audio-manifest";
import type { Level, Vocab } from "@/lib/types/content-types";
import { hcmDayRangeUtc } from "./hcm-day";
import { sortDueRows, type DueRow } from "./queue-ordering";
import type { ReviewItem } from "./review-types";

const NEW_CARD_DAILY_LIMIT = 20; // global per user, hard ceiling (decision 4)
const DUE_FETCH_LIMIT = 50;
const DEFAULT_LEVEL: Level = "starters";

export type ReviewQueue = {
  items: ReviewItem[];
  dueCount: number;
  newCount: number;
};

function toReviewItem(vocab: Vocab, isNew: boolean): ReviewItem {
  return {
    vocabId: vocab.id,
    word: vocab.word,
    ipa: vocab.ipa,
    exampleSentence: vocab.example_sentence,
    imageHint: vocab.image_hint,
    wordAudioUrl: audioUrl("vocabulary", vocab.id, "word") ?? null,
    sentenceAudioUrl: audioUrl("vocabulary", vocab.id, "sentence") ?? null,
    isNew,
  };
}

export async function getReviewQueue(): Promise<ReviewQueue> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { items: [], dueCount: 0, newCount: 0 };

  const [{ data: profile }, { data: dueRows }] = await Promise.all([
    supabase.from("profiles").select("current_level").eq("id", user.id).maybeSingle(),
    // order("due") matters beyond cosmetics: with more than DUE_FETCH_LIMIT cards due,
    // an unordered limit would hand the state-priority sort an arbitrary subset.
    // Ordered, the limit keeps the most overdue cards (uses idx_srs_cards_user_due).
    supabase
      .from("srs_cards")
      .select("vocab_id, state, due")
      .eq("user_id", user.id)
      .lte("due", new Date().toISOString())
      .order("due", { ascending: true })
      .limit(DUE_FETCH_LIMIT),
  ]);

  const level = (profile?.current_level as Level) ?? DEFAULT_LEVEL;

  // Due existing cards → review items (skip any whose vocab is missing from content).
  const dueSorted = sortDueRows((dueRows ?? []) as DueRow[]);
  const dueItems: ReviewItem[] = [];
  for (const row of dueSorted) {
    const vocab = getVocabById(row.vocab_id);
    if (vocab) dueItems.push(toReviewItem(vocab, false));
  }

  // New candidates: current level only, excluding vocab that already has a card,
  // capped by the remaining daily quota (20 minus cards introduced today, HCM).
  //
  // The exclusion query filters to the current level's ids (vocab ids are
  // "{level}_vocab_{nnn}") — new candidates only come from this level, and the filter
  // keeps the result (≤500 rows/level) under Supabase's max_rows=1000 response cap.
  // Unfiltered, a user with >1000 cards would get a truncated set and see
  // already-learned vocab re-offered as "new".
  const { start, end } = hcmDayRangeUtc();
  const [{ data: existingRows }, { count: usedToday }] = await Promise.all([
    supabase
      .from("srs_cards")
      .select("vocab_id")
      .eq("user_id", user.id)
      // LIKE's `_` wildcard is fine unescaped: every row is a validated vocab id
      // (submitReview rejects unknown ids), so only this level's ids can match.
      .like("vocab_id", `${level}_vocab_%`),
    supabase
      .from("srs_cards")
      .select("*", { count: "exact", head: true })
      .eq("user_id", user.id)
      .gte("created_at", start.toISOString())
      .lt("created_at", end.toISOString()),
  ]);

  const remainingNewQuota = Math.max(0, NEW_CARD_DAILY_LIMIT - (usedToday ?? 0));
  const existingIds = new Set((existingRows ?? []).map((r) => r.vocab_id));

  const newItems: ReviewItem[] = [];
  if (remainingNewQuota > 0) {
    for (const vocab of getVocab(level)) {
      if (newItems.length >= remainingNewQuota) break;
      if (!existingIds.has(vocab.id)) newItems.push(toReviewItem(vocab, true));
    }
  }

  return {
    items: [...dueItems, ...newItems],
    dueCount: dueItems.length,
    newCount: newItems.length,
  };
}
