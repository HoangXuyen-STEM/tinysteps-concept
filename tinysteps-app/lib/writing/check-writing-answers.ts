import {
  BLANK_COMPLETION_SCORE,
  checkBlankAnswers,
  isAcceptedBlankAnswer,
  type BlankAnswer,
  type BlankResult,
  type BlankScoreResult,
} from "@/lib/exercises/check-blank-answers";
import type { WritingExercise } from "@/lib/types/content-types";

export const WRITING_COMPLETION_SCORE = BLANK_COMPLETION_SCORE;

export type WritingAnswer = BlankAnswer;
export type WritingBlankResult = BlankResult;
export type WritingScoreResult = BlankScoreResult;

export function isAcceptedWritingAnswer(value: string, acceptedAnswers: readonly string[]): boolean {
  return isAcceptedBlankAnswer(value, acceptedAnswers);
}

export function checkWritingAnswers(
  exercise: WritingExercise,
  answers: readonly WritingAnswer[],
): WritingScoreResult {
  return checkBlankAnswers(exercise.blanks, answers, "Invalid writing answers");
}
