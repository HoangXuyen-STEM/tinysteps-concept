import { describe, it, expect } from "vitest";
import {
  audioKey,
  lineKey,
  exerciseListenKey,
  listenIndexOffset,
  DIALOGUE_FULL_KEY,
} from "../audio-keys";
import type { Exercise } from "@/lib/types/content-types";

describe("audioKey", () => {
  it("zero-pads single digit index (0 → 01)", () => {
    expect(audioKey("line", 0)).toBe("line_01");
  });

  it("zero-pads single digit index (8 → 09)", () => {
    expect(audioKey("test", 8)).toBe("test_09");
  });

  it("does not zero-pad double digit index (9 → 10)", () => {
    expect(audioKey("line", 9)).toBe("line_10");
  });

  it("handles large index", () => {
    expect(audioKey("item", 98)).toBe("item_99");
  });
});

describe("lineKey", () => {
  it("generates correct key for first line", () => {
    expect(lineKey(0)).toBe("line_01");
  });

  it("generates correct key for fourth line", () => {
    expect(lineKey(3)).toBe("line_04");
  });

  it("generates correct key for eighth line (pet lessons)", () => {
    expect(lineKey(7)).toBe("line_08");
  });
});

describe("exerciseListenKey", () => {
  it("generates correct key for first listen item", () => {
    expect(exerciseListenKey(0)).toBe("exercise_listen_01");
  });

  it("generates correct key for third listen item", () => {
    expect(exerciseListenKey(2)).toBe("exercise_listen_03");
  });
});

describe("DIALOGUE_FULL_KEY", () => {
  it("is the expected constant", () => {
    expect(DIALOGUE_FULL_KEY).toBe("dialogue_full");
  });
});

describe("listenIndexOffset", () => {
  // Regression test: generate_audio.py numbers exercise_listen_NN with ONE counter
  // across the whole lesson, not reset per exercise. A lesson with two listen_choose
  // exercises (separated by an unrelated exercise) must have the second one's audio
  // keys continue where the first left off, not restart at exercise_listen_01.
  const twoListenChooseExercises: Exercise[] = [
    {
      type: "listen_choose",
      instruction: "Listen and choose",
      items: [
        { audio_text: "a", options: ["a", "b"], correct_answer: "a" },
        { audio_text: "b", options: ["a", "b"], correct_answer: "b" },
      ],
    },
    {
      type: "multiple_choice",
      instruction: "Pick one",
      items: [
        { prompt: "p1", options: ["x", "y"], correct_answer: "x" },
        { prompt: "p2", options: ["x", "y"], correct_answer: "y" },
        { prompt: "p3", options: ["x", "y"], correct_answer: "x" },
      ],
    },
    {
      type: "listen_choose",
      instruction: "Listen and choose again",
      items: [
        { audio_text: "c", options: ["a", "b"], correct_answer: "a" },
        { audio_text: "d", options: ["a", "b"], correct_answer: "b" },
      ],
    },
  ];

  it("is 0 for the first exercise in the lesson", () => {
    expect(listenIndexOffset(twoListenChooseExercises, 0)).toBe(0);
  });

  it("does not count items from a non-listen_choose exercise in between", () => {
    expect(listenIndexOffset(twoListenChooseExercises, 1)).toBe(2);
  });

  it("continues the second listen_choose exercise from where the first left off", () => {
    // First exercise had 2 items (exercise_listen_01, _02). The second listen_choose
    // exercise's own item 0 must resolve to exercise_listen_03, not restart at _01.
    const offset = listenIndexOffset(twoListenChooseExercises, 2);
    expect(offset).toBe(2);
    expect(exerciseListenKey(offset + 0)).toBe("exercise_listen_03");
    expect(exerciseListenKey(offset + 1)).toBe("exercise_listen_04");
  });
});
