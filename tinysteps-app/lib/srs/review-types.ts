// Shared between the server (queue build, review action) and client (session, flashcard).
// No server-only import here so the client may import the types and rating constants.

/** One card to review, with content + pre-resolved audio URLs (resolved server-side). */
export type ReviewItem = {
  vocabId: string;
  word: string;
  ipa: string;
  exampleSentence: string;
  imageHint: string;
  wordAudioUrl: string | null;
  sentenceAudioUrl: string | null;
  /** No card row yet — this review will lazily create one. */
  isNew: boolean;
};

// Rating values mirror ts-fsrs Rating (1 Again … 4 Easy). The client sends these ints;
// the server maps them to the ts-fsrs enum. Kept here so the client never imports ts-fsrs.
export const REVIEW_RATINGS = [
  { value: 1, key: "again", vi: "Lại" },
  { value: 2, key: "hard", vi: "Khó" },
  { value: 3, key: "good", vi: "Được" },
  { value: 4, key: "easy", vi: "Dễ" },
] as const;

export type ReviewRating = (typeof REVIEW_RATINGS)[number]["value"];

export function isReviewRating(value: number): value is ReviewRating {
  return value === 1 || value === 2 || value === 3 || value === 4;
}

/** Cards are shown in batches of this size; finishing one batch is enough (decision 4). */
export const REVIEW_BATCH_SIZE = 5;
