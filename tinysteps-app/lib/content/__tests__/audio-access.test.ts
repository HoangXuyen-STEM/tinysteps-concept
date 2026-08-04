import { describe, it, expect } from "vitest";
import { isFreeAudioPath } from "../audio-access";
import { audioPath, listeningAudioPath } from "../audio-manifest";
import { FREE_LESSON_IDS, FREE_LISTENING_IDS } from "@/lib/access/paid-access";
import { getFreeVocabIds } from "@/lib/access/unlocked-vocab";

describe("audio paywall boundary", () => {
  it("treats every recording of a free lesson as public", () => {
    for (const lessonId of FREE_LESSON_IDS) {
      const dialogue = audioPath("lessons", lessonId, "dialogue_full");
      expect(dialogue).toBeDefined();
      expect(isFreeAudioPath(dialogue!)).toBe(true);
    }
  });

  it("treats the free listening exercise as public", () => {
    for (const listeningId of FREE_LISTENING_IDS) {
      const path = listeningAudioPath(listeningId);
      expect(path).toBeDefined();
      expect(isFreeAudioPath(path!)).toBe(true);
    }
  });

  it("treats the words the free lessons teach as public", () => {
    for (const vocabId of getFreeVocabIds()) {
      for (const type of ["word", "sentence"]) {
        const path = audioPath("vocabulary", vocabId, type);
        if (path) expect(isFreeAudioPath(path)).toBe(true);
      }
    }
  });

  it("keeps paid recordings out of the public bucket", () => {
    // starters_listening_002 is the file that was reachable unauthenticated when every
    // recording shared one public bucket under sequential names.
    const paidListening = listeningAudioPath("starters_listening_002");
    const paidLesson = audioPath("lessons", "starters_lesson_010", "dialogue_full");

    expect(paidListening).toBeDefined();
    expect(paidLesson).toBeDefined();
    expect(isFreeAudioPath(paidListening!)).toBe(false);
    expect(isFreeAudioPath(paidLesson!)).toBe(false);
  });
});
