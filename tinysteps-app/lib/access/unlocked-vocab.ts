import "server-only";
import { getLesson } from "@/lib/content/lesson-loader";
import { FREE_LESSON_IDS } from "./paid-access";

/**
 * The vocabulary a non-paying learner is entitled to study: the union of
 * `vocabulary_ids` across the free lessons.
 *
 * The SRS review queue is itself a free feature — the gate is on *which words* feed it,
 * not on the page. Without this set the queue drew new cards straight from the level's
 * whole word bank, so a free account collected paid vocabulary (word, IPA, example
 * sentence, audio) at the daily new-card quota just by opening the review tab.
 *
 * Paid learners are never filtered through this: every lesson is open to them, so every
 * word in the level is already theirs.
 *
 * Content is static, so the set is built once at module load.
 */
const freeVocabIds: ReadonlySet<string> = new Set(
  FREE_LESSON_IDS.flatMap((lessonId) => getLesson(lessonId)?.vocabulary_ids ?? []),
);

/** Whether this word belongs to a lesson that is open without paying. */
export const isFreeVocab = (vocabId: string): boolean => freeVocabIds.has(vocabId);

export const getFreeVocabIds = (): ReadonlySet<string> => freeVocabIds;
