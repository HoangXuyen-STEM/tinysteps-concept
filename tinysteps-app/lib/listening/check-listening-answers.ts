import {
  BLANK_COMPLETION_SCORE,
  checkBlankAnswers,
  isAcceptedBlankAnswer,
  type BlankAnswer,
  type BlankResult,
  type BlankScoreResult,
} from "@/lib/exercises/check-blank-answers";
import type { ListeningExercise } from "@/lib/types/content-types";

export const LISTENING_COMPLETION_SCORE = BLANK_COMPLETION_SCORE;

export type ListeningAnswer = BlankAnswer;
export type ListeningBlankResult = BlankResult;
export type ListeningScoreResult = BlankScoreResult;

export function isAcceptedListeningAnswer(value: string, acceptedAnswers: readonly string[]): boolean {
  return isAcceptedBlankAnswer(value, acceptedAnswers);
}

export function checkListeningAnswers(
  exercise: ListeningExercise,
  answers: readonly ListeningAnswer[],
): ListeningScoreResult {
  return checkBlankAnswers(exercise.blanks, answers, "Invalid listening answers");
}
