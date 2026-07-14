/**
 * Shared answer-checking utilities for exercise components.
 * Used both client-side (immediate feedback) and server-side (score computation).
 */

import type { Exercise } from "@/lib/types/content-types";

/** Trim, lowercase, and collapse internal whitespace to a single space. */
export function normalize(s: string): string {
  return s.trim().toLowerCase().replace(/\s+/g, " ");
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
