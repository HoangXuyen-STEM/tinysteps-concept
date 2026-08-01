import { describe, expect, it } from "vitest";
import type { WritingExercise } from "@/lib/types/content-types";
import { toPublicWritingExercise } from "../public-writing";

describe("public writing projection", () => {
  it("removes accepted answers while preserving ids and cues", () => {
    const exercise = {
      id: "starters_writing_001",
      level: "starters",
      order: 1,
      title: "Test",
      scenario: "Test",
      estimated_minutes: 4,
      grammar_ids: ["starters_grammar_003"],
      instruction: "Complete.",
      passage: "It {{b1}} ready.",
      blanks: [{ id: "b1", cue: "be", accepted_answers: ["is"] }],
    } satisfies WritingExercise;

    const publicExercise = toPublicWritingExercise(exercise);
    expect(publicExercise.blanks).toEqual([{ id: "b1", cue: "be" }]);
    expect(JSON.stringify(publicExercise)).not.toContain("accepted_answers");
    expect(JSON.stringify(publicExercise)).not.toContain('"is"');
  });
});
