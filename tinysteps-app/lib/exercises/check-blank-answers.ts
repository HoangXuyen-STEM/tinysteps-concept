import { normalize } from "@/lib/exercises/check-answer";

export const BLANK_COMPLETION_SCORE = 80;

export type BlankLike = { id: string; accepted_answers: readonly string[] };
export type BlankAnswer = { blankId: string; value: string };
export type BlankResult = { blankId: string; isCorrect: boolean; correctAnswer: string };
export type BlankScoreResult = {
  score: number;
  correctCount: number;
  totalItems: number;
  completed: boolean;
  results: BlankResult[];
};

export function isAcceptedBlankAnswer(value: string, acceptedAnswers: readonly string[]): boolean {
  return acceptedAnswers.some((answer) => normalize(value) === normalize(answer));
}

/**
 * Shared submit-all-then-grade logic for exercise types made of fill-in blanks
 * (Writing, Listening, ...). Validates that the answer set exactly matches the
 * exercise's blanks (no missing/duplicate/unknown ids, no empty/overlong values),
 * then scores each blank and reports completion at BLANK_COMPLETION_SCORE%.
 */
export function checkBlankAnswers<TBlank extends BlankLike>(
  blanks: readonly TBlank[],
  answers: readonly BlankAnswer[],
  invalidMessage: string,
): BlankScoreResult {
  const knownIds = new Set(blanks.map((blank) => blank.id));
  const answerIds = answers.map((answer) => answer.blankId);
  const uniqueAnswerIds = new Set(answerIds);
  if (
    answers.length !== blanks.length ||
    uniqueAnswerIds.size !== answers.length ||
    answerIds.some((id) => !knownIds.has(id)) ||
    blanks.some((blank) => !uniqueAnswerIds.has(blank.id)) ||
    answers.some((answer) => typeof answer.value !== "string" || !answer.value.trim() || answer.value.length > 100)
  ) {
    throw new Error(invalidMessage);
  }

  const answerMap = new Map(answers.map((answer) => [answer.blankId, answer.value]));
  const results = blanks.map((blank) => ({
    blankId: blank.id,
    isCorrect: isAcceptedBlankAnswer(answerMap.get(blank.id) ?? "", blank.accepted_answers),
    correctAnswer: blank.accepted_answers[0] ?? "",
  }));
  const correctCount = results.filter((result) => result.isCorrect).length;
  const totalItems = results.length;
  const score = totalItems === 0 ? 0 : Math.round((correctCount / totalItems) * 100);

  return {
    score,
    correctCount,
    totalItems,
    completed: score >= BLANK_COMPLETION_SCORE,
    results,
  };
}
