import { describe, it, expect } from "vitest";
import {
  normalize,
  isCorrect,
  computeScore,
  type ExerciseAnswer,
} from "../check-answer";
import type { Exercise } from "@/lib/types/content-types";

describe("normalize", () => {
  it("trims leading and trailing whitespace", () => {
    expect(normalize("  hello  ")).toBe("hello");
  });

  it("lowercases the string", () => {
    expect(normalize("Hello World")).toBe("hello world");
  });

  it("collapses multiple internal spaces to one", () => {
    expect(normalize("hello   world")).toBe("hello world");
  });

  it("handles tabs and newlines as whitespace", () => {
    expect(normalize("  hello\t\n  world  ")).toBe("hello world");
  });

  it("returns empty string for whitespace-only input", () => {
    expect(normalize("   ")).toBe("");
  });

  it("handles empty string", () => {
    expect(normalize("")).toBe("");
  });
});

describe("isCorrect", () => {
  it("matches identical strings", () => {
    expect(isCorrect("hello", "hello")).toBe(true);
  });

  it("matches case-insensitively", () => {
    expect(isCorrect("Hello", "hello")).toBe(true);
    expect(isCorrect("HELLO", "hello")).toBe(true);
  });

  it("matches with extra whitespace", () => {
    expect(isCorrect("  hello  world  ", "hello world")).toBe(true);
  });

  it("rejects wrong answer", () => {
    expect(isCorrect("goodbye", "hello")).toBe(false);
  });

  it("rejects partial match", () => {
    expect(isCorrect("hell", "hello")).toBe(false);
  });

  it("handles empty strings", () => {
    expect(isCorrect("", "")).toBe(true);
    expect(isCorrect("", "hello")).toBe(false);
  });
});

describe("computeScore", () => {
  const makeExercises = (
    ...itemCounts: { type: Exercise["type"]; answers: string[] }[]
  ): Exercise[] =>
    itemCounts.map(({ type, answers }) => {
      if (type === "multiple_choice") {
        return {
          type: "multiple_choice",
          instruction: "test",
          items: answers.map((a) => ({
            prompt: "q",
            options: [a, "wrong"],
            correct_answer: a,
          })),
        };
      }
      // Default to fill_blank for simplicity
      return {
        type: "fill_blank",
        instruction: "test",
        items: answers.map((a) => ({
          prompt: `___ ${a}`,
          correct_answer: a,
        })),
      };
    });

  it("scores all correct answers as 100", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["cat", "dog"],
    });
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "cat" },
      { exerciseIndex: 0, itemIndex: 1, userAnswer: "dog" },
    ];
    expect(computeScore(answers, exercises)).toEqual({
      score: 100,
      correctCount: 2,
      totalItems: 2,
    });
  });

  it("scores all wrong answers as 0", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["cat", "dog"],
    });
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "fish" },
      { exerciseIndex: 0, itemIndex: 1, userAnswer: "bird" },
    ];
    expect(computeScore(answers, exercises)).toEqual({
      score: 0,
      correctCount: 0,
      totalItems: 2,
    });
  });

  it("scores partial correctness and rounds", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["a", "b", "c"],
    });
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "a" },
      { exerciseIndex: 0, itemIndex: 1, userAnswer: "wrong" },
      { exerciseIndex: 0, itemIndex: 2, userAnswer: "c" },
    ];
    const result = computeScore(answers, exercises);
    expect(result.correctCount).toBe(2);
    expect(result.totalItems).toBe(3);
    expect(result.score).toBe(67); // Math.round(2/3 * 100) = 67
  });

  it("handles multiple exercises", () => {
    const exercises = makeExercises(
      { type: "fill_blank", answers: ["a"] },
      { type: "multiple_choice", answers: ["b", "c"] },
    );
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "a" },
      { exerciseIndex: 1, itemIndex: 0, userAnswer: "b" },
      { exerciseIndex: 1, itemIndex: 1, userAnswer: "wrong" },
    ];
    const result = computeScore(answers, exercises);
    expect(result.correctCount).toBe(2);
    expect(result.totalItems).toBe(3);
    expect(result.score).toBe(67);
  });

  it("handles empty exercises", () => {
    expect(computeScore([], [])).toEqual({
      score: 0,
      correctCount: 0,
      totalItems: 0,
    });
  });

  it("ignores answers with out-of-bounds indices", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["cat"],
    });
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "cat" },
      { exerciseIndex: 5, itemIndex: 0, userAnswer: "ghost" }, // invalid exercise
      { exerciseIndex: 0, itemIndex: 9, userAnswer: "ghost" }, // invalid item
    ];
    expect(computeScore(answers, exercises)).toEqual({
      score: 100,
      correctCount: 1,
      totalItems: 1,
    });
  });

  it("normalizes answers before comparison (case, whitespace)", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["hello world"],
    });
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "  Hello   World  " },
    ];
    expect(computeScore(answers, exercises)).toEqual({
      score: 100,
      correctCount: 1,
      totalItems: 1,
    });
  });

  it("counts totalItems from exercises, not from answers submitted", () => {
    const exercises = makeExercises({
      type: "fill_blank",
      answers: ["a", "b", "c"],
    });
    // Only submit 1 answer out of 3
    const answers: ExerciseAnswer[] = [
      { exerciseIndex: 0, itemIndex: 0, userAnswer: "a" },
    ];
    const result = computeScore(answers, exercises);
    expect(result.correctCount).toBe(1);
    expect(result.totalItems).toBe(3);
    expect(result.score).toBe(33); // 1/3
  });
});
