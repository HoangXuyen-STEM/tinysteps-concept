import { normalize } from "@/lib/exercises/check-answer";
import type { WritingExercise } from "@/lib/types/content-types";

export const WRITING_COMPLETION_SCORE = 80;

export type WritingAnswer = { blankId: string; value: string };
export type WritingBlankResult = { blankId: string; isCorrect: boolean; correctAnswer: string };
export type WritingScoreResult = {
  score: number;
  correctCount: number;
  totalItems: number;
  completed: boolean;
  results: WritingBlankResult[];
};

export function isAcceptedWritingAnswer(value: string, acceptedAnswers: readonly string[]): boolean {
  return acceptedAnswers.some((answer) => normalize(value) === normalize(answer));
}

export function checkWritingAnswers(
  exercise: WritingExercise,
  answers: readonly WritingAnswer[],
): WritingScoreResult {
  const knownIds = new Set(exercise.blanks.map((blank) => blank.id));
  const answerIds = answers.map((answer) => answer.blankId);
  const uniqueAnswerIds = new Set(answerIds);
  if (
    answers.length !== exercise.blanks.length ||
    uniqueAnswerIds.size !== answers.length ||
    answerIds.some((id) => !knownIds.has(id)) ||
    exercise.blanks.some((blank) => !uniqueAnswerIds.has(blank.id)) ||
    answers.some((answer) => typeof answer.value !== "string" || !answer.value.trim() || answer.value.length > 100)
  ) {
    throw new Error("Invalid writing answers");
  }

  const answerMap = new Map(answers.map((answer) => [answer.blankId, answer.value]));
  const results = exercise.blanks.map((blank) => ({
    blankId: blank.id,
    isCorrect: isAcceptedWritingAnswer(answerMap.get(blank.id) ?? "", blank.accepted_answers),
    correctAnswer: blank.accepted_answers[0] ?? "",
  }));
  const correctCount = results.filter((result) => result.isCorrect).length;
  const totalItems = results.length;
  const score = totalItems === 0 ? 0 : Math.round((correctCount / totalItems) * 100);

  return {
    score,
    correctCount,
    totalItems,
    completed: score >= WRITING_COMPLETION_SCORE,
    results,
  };
}
