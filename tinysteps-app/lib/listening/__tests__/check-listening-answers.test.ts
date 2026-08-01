import { describe, expect, it } from "vitest";
import type { ListeningExercise } from "@/lib/types/content-types";
import {
  checkListeningAnswers,
  isAcceptedListeningAnswer,
  LISTENING_COMPLETION_SCORE,
} from "../check-listening-answers";

const exercise: ListeningExercise = {
  id: "starters_listening_001",
  level: "starters",
  order: 1,
  title: "Test",
  scenario: "Test",
  estimated_minutes: 4,
  grammar_ids: ["starters_grammar_003"],
  instruction: "Listen and complete.",
  audio_text: "I am seven years old. My cat is grey. I live at 12 Main Street. I have three books.",
  passage: "I am {{b1}} years old. My cat is {{b2}}. I live at {{b3}} Main Street. I have {{b4}} books.",
  transcript: "I am seven years old. My cat is grey. I live at 12 Main Street. I have three books.",
  blanks: [
    { id: "b1", cue: "age", category: "age", accepted_answers: ["seven", "7"] },
    { id: "b2", cue: "colour", category: "color", accepted_answers: ["grey", "gray"] },
    { id: "b3", cue: "house number", category: "address", accepted_answers: ["12"] },
    { id: "b4", cue: "number of books", category: "number", accepted_answers: ["three", "3"] },
  ],
};

describe("listening answer checking", () => {
  it("accepts number/word and British/American spelling variants", () => {
    expect(isAcceptedListeningAnswer("7", ["seven", "7"])).toBe(true);
    expect(isAcceptedListeningAnswer("GRAY", ["grey", "gray"])).toBe(true);
  });

  it("marks 80 percent as completed and returns per-blank feedback", () => {
    const result = checkListeningAnswers(exercise, [
      { blankId: "b1", value: "seven" },
      { blankId: "b2", value: "grey" },
      { blankId: "b3", value: "12" },
      { blankId: "b4", value: "two" },
    ]);
    expect(LISTENING_COMPLETION_SCORE).toBe(80);
    expect(result).toMatchObject({ score: 75, correctCount: 3, totalItems: 4, completed: false });
    expect(result.results.at(-1)).toEqual({ blankId: "b4", isCorrect: false, correctAnswer: "three" });
  });

  it("rejects missing, duplicate, unknown, empty and overlong answers", () => {
    const valid = exercise.blanks.map((blank) => ({ blankId: blank.id, value: blank.accepted_answers[0] }));
    expect(() => checkListeningAnswers(exercise, valid.slice(1))).toThrow("Invalid listening answers");
    expect(() => checkListeningAnswers(exercise, [...valid.slice(0, 3), valid[0]])).toThrow("Invalid listening answers");
    expect(() => checkListeningAnswers(exercise, [...valid.slice(0, 3), { blankId: "b9", value: "x" }])).toThrow(
      "Invalid listening answers",
    );
    expect(() =>
      checkListeningAnswers(exercise, valid.map((answer, index) => (index === 0 ? { ...answer, value: " " } : answer))),
    ).toThrow("Invalid listening answers");
    expect(() =>
      checkListeningAnswers(
        exercise,
        valid.map((answer, index) => (index === 0 ? { ...answer, value: "x".repeat(101) } : answer)),
      ),
    ).toThrow("Invalid listening answers");
  });
});
