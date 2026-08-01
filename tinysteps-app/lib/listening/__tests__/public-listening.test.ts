import { describe, expect, it } from "vitest";
import type { ListeningExercise } from "@/lib/types/content-types";
import { toPublicListeningExercise } from "../public-listening";

const exercise = {
  id: "starters_listening_001",
  level: "starters",
  order: 1,
  title: "Test",
  scenario: "Test",
  estimated_minutes: 4,
  grammar_ids: ["starters_grammar_003"],
  instruction: "Listen and complete.",
  audio_text: "It is seven o'clock.",
  passage: "It {{b1}} {{b2}} o'clock.",
  transcript: "It is seven o'clock.",
  blanks: [
    { id: "b1", cue: "be", category: "number" as const, accepted_answers: ["is"] },
    { id: "b2", cue: "number", category: "number" as const, accepted_answers: ["seven", "7"] },
  ],
} satisfies ListeningExercise;

describe("public listening projection", () => {
  it("removes accepted answers, audio_text and transcript while preserving passage/cue/category", () => {
    const publicExercise = toPublicListeningExercise(exercise);
    expect(publicExercise.blanks).toEqual([
      { id: "b1", cue: "be", category: "number" },
      { id: "b2", cue: "number", category: "number" },
    ]);
    expect(publicExercise.passage).toBe(exercise.passage);
    expect("audio_text" in publicExercise).toBe(false);
    expect("transcript" in publicExercise).toBe(false);

    const serialized = JSON.stringify(publicExercise);
    expect(serialized).not.toContain("accepted_answers");
    expect(serialized).not.toContain("audio_text");
    expect(serialized).not.toContain("transcript");
    expect(serialized).not.toContain('"seven"');
  });
});
