import { describe, it, expect } from "vitest";
import { getFreeVocabIds, isFreeVocab } from "../unlocked-vocab";
import { FREE_LESSON_IDS } from "../paid-access";
import { getLesson } from "@/lib/content/lesson-loader";
import { getVocab } from "@/lib/content/vocabulary-loader";

describe("free vocabulary boundary", () => {
  it("covers exactly the words taught by the free lessons", () => {
    const expected = new Set(
      FREE_LESSON_IDS.flatMap((lessonId) => getLesson(lessonId)?.vocabulary_ids ?? []),
    );

    expect(getFreeVocabIds()).toEqual(expected);
    expect(expected.size).toBeGreaterThan(0);
  });

  it("leaves the rest of the level locked", () => {
    // The review queue used to draw new cards from the whole level, which handed a free
    // account the paid word bank 20 words a day. Guard the gap it walked through.
    const levelVocab = getVocab("starters");
    const locked = levelVocab.filter((vocab) => !isFreeVocab(vocab.id));

    expect(locked.length).toBeGreaterThan(0);
    expect(locked.length).toBeLessThan(levelVocab.length);
  });

  it("does not leak words from a paid lesson", () => {
    const paidLesson = getLesson("starters_lesson_010");
    const paidOnly = (paidLesson?.vocabulary_ids ?? []).filter((id) => !isFreeVocab(id));

    expect(paidLesson).toBeDefined();
    expect(paidOnly.every((id) => !isFreeVocab(id))).toBe(true);
    expect(paidOnly.length).toBeGreaterThan(0);
  });
});
