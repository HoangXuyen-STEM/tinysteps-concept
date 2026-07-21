/**
 * Shared answer-checking utilities for exercise components.
 * Used both client-side (immediate feedback) and server-side (score computation).
 */

import type { Exercise } from "@/lib/types/content-types";

// Expand English contractions to their full form so a learner who types the long
// form is graded the same as one who types the contraction ("I'm" and "I am" both
// become "i am"). Order matters: the irregular forms whose stem is not simply the
// text before the suffix (won't → will, can't → cannot) must run before the generic
// suffix rules. Applied symmetrically to both answers via normalize(), so the "'s"
// possessive/"is" ambiguity can never reject a genuinely correct answer — both sides
// canonicalize identically.
const CONTRACTIONS: readonly [RegExp, string][] = [
  [/\bwon't\b/g, "will not"],
  [/\bcan't\b/g, "cannot"],
  [/\bshan't\b/g, "shall not"],
  [/\blet's\b/g, "let us"],
  [/(\w+)n't\b/g, "$1 not"],
  [/(\w+)'re\b/g, "$1 are"],
  [/(\w+)'ve\b/g, "$1 have"],
  [/(\w+)'ll\b/g, "$1 will"],
  [/(\w+)'m\b/g, "$1 am"],
  [/(\w+)'d\b/g, "$1 would"],
  [/(\w+)'s\b/g, "$1 is"],
];

function expandContractions(s: string): string {
  return CONTRACTIONS.reduce((acc, [re, rep]) => acc.replace(re, rep), s);
}

/**
 * Lowercase, normalize apostrophes, expand contractions, collapse internal whitespace
 * to a single space, and remove any space immediately before punctuation. The last rule
 * matters because arrange-exercise data ships end punctuation as its own word chip
 * (e.g. `["...", "book", "."]`) — the UI joins tapped chips with spaces, producing
 * "book ." while correct_answer reads "book." Without stripping that space, a
 * correctly-ordered answer never matches.
 */
export function normalize(s: string): string {
  const expanded = expandContractions(s.toLowerCase().replace(/[’‘]/g, "'"));
  return expanded
    .trim()
    .replace(/\s+/g, " ")
    .replace(/\s+([.,!?;:])/g, "$1");
}

/** Compare user answer to correct answer after normalization. */
export function isCorrect(userAnswer: string, correctAnswer: string): boolean {
  return normalize(userAnswer) === normalize(correctAnswer);
}

export type ExerciseAnswer = {
  exerciseIndex: number;
  itemIndex: number;
  userAnswer: string;
};

/**
 * Compute score from submitted answers against the lesson's exercises.
 * Returns { score, correctCount, totalItems }.
 *
 * Server-side only: the lesson is loaded on the server, so correct answers
 * are never exposed to or trusted from the client.
 */
export function computeScore(
  answers: ExerciseAnswer[],
  exercises: Exercise[],
): { score: number; correctCount: number; totalItems: number } {
  const totalItems = exercises.reduce((sum, ex) => sum + ex.items.length, 0);
  if (totalItems === 0) return { score: 0, correctCount: 0, totalItems: 0 };

  let correctCount = 0;

  for (const answer of answers) {
    const exercise = exercises[answer.exerciseIndex];
    if (!exercise) continue;

    const item = exercise.items[answer.itemIndex];
    if (!item) continue;

    if (isCorrect(answer.userAnswer, item.correct_answer)) {
      correctCount++;
    }
  }

  const score = Math.round((correctCount / totalItems) * 100);
  return { score, correctCount, totalItems };
}
