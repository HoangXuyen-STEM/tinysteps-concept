import { describe, expect, it } from "vitest";
import type { WritingExercise } from "@/lib/types/content-types";
import {
  checkWritingAnswers,
  isAcceptedWritingAnswer,
  WRITING_COMPLETION_SCORE,
} from "../check-writing-answers";

const exercise: WritingExercise = {
  id: "starters_writing_001",
  level: "starters",
  order: 1,
  title: "Test",
  scenario: "Test",
  estimated_minutes: 4,
  grammar_ids: ["starters_grammar_003"],
  instruction: "Complete.",
  passage: "{{b1}} {{b2}} {{b3}} {{b4}} {{b5}}",
  blanks: [
    { id: "b1", cue: "be", accepted_answers: ["is"] },
    { id: "b2", cue: "not have", accepted_answers: ["has not"] },
    { id: "b3", cue: "teach", accepted_answers: ["teaches"] },
    { id: "b4", cue: "be", accepted_answers: ["are"] },
    { id: "b5", cue: "work", accepted_answers: ["works"] },
  ],
};

describe("writing answer checking", () => {
  it("accepts case, whitespace, apostrophe and contraction variants", () => {
    expect(isAcceptedWritingAnswer("  HASN’T ", ["has not"])).toBe(true);
  });

  it("marks 80 percent as completed and returns per-blank feedback", () => {
    const result = checkWritingAnswers(exercise, [
      { blankId: "b1", value: "is" },
      { blankId: "b2", value: "hasn't" },
      { blankId: "b3", value: "teaches" },
      { blankId: "b4", value: "are" },
      { blankId: "b5", value: "work" },
    ]);
    expect(WRITING_COMPLETION_SCORE).toBe(80);
    expect(result).toMatchObject({ score: 80, correctCount: 4, totalItems: 5, completed: true });
    expect(result.results.at(-1)).toEqual({ blankId: "b5", isCorrect: false, correctAnswer: "works" });
  });

  it("rejects missing, duplicate, unknown, empty and overlong answers", () => {
    const valid = exercise.blanks.map((blank) => ({ blankId: blank.id, value: blank.accepted_answers[0] }));
    expect(() => checkWritingAnswers(exercise, valid.slice(1))).toThrow("Invalid writing answers");
    expect(() => checkWritingAnswers(exercise, [...valid.slice(0, 4), valid[0]])).toThrow("Invalid writing answers");
    expect(() => checkWritingAnswers(exercise, [...valid.slice(0, 4), { blankId: "b9", value: "x" }])).toThrow("Invalid writing answers");
    expect(() => checkWritingAnswers(exercise, valid.map((answer, index) => index === 0 ? { ...answer, value: " " } : answer))).toThrow("Invalid writing answers");
    expect(() => checkWritingAnswers(exercise, valid.map((answer, index) => index === 0 ? { ...answer, value: "x".repeat(101) } : answer))).toThrow("Invalid writing answers");
  });
});
