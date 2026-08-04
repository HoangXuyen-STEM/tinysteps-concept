// Which audio recordings belong to the free trial, shared by the upload script and the
// post-upload verifier so the two cannot disagree about what should be public.
//
// The app derives the same set in lib/content/audio-access.ts. Node scripts cannot
// import that TypeScript module, so the free id lists are mirrored here — and validated
// against the content below, which turns a rename in lib/access/paid-access.ts into a
// loud failure instead of a trial recording that quietly 403s for visitors.
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const dataRoot = join(appDirectory, "..", "tinysteps-data");
const audioRoot = join(dataRoot, "audio");

export const FREE_LESSON_IDS = [
  "starters_lesson_001",
  "starters_lesson_002",
  "starters_lesson_003",
];
export const FREE_LISTENING_IDS = ["starters_listening_001"];

export const readAudioManifest = () =>
  readFile(join(audioRoot, "manifest.json"), "utf8").then(JSON.parse);

/** Manifest paths are "audio/<key>"; inside a bucket the leading segment is dropped. */
export const toStorageKey = (manifestPath) => manifestPath.replace(/^audio\//, "");

/**
 * Storage keys (relative to tinysteps-data/audio) that belong in the public bucket: the
 * free lessons, the free listening exercise, and the vocabulary those lessons teach.
 */
export async function readFreeAudioKeys(manifest) {
  const audioManifest = manifest ?? (await readAudioManifest());
  const keys = new Set();

  for (const lessonId of FREE_LESSON_IDS) {
    const entry = audioManifest.lessons[lessonId];
    if (!entry) throw new Error(`Free lesson "${lessonId}" has no audio manifest entry.`);
    for (const path of Object.values(entry)) keys.add(toStorageKey(path));
  }

  for (const listeningId of FREE_LISTENING_IDS) {
    const path = audioManifest.listening[listeningId];
    if (!path) throw new Error(`Free listening "${listeningId}" has no audio manifest entry.`);
    keys.add(toStorageKey(path));
  }

  // Vocabulary is read off the free lessons themselves, so the word list and the lesson
  // list can never drift apart.
  for (const lessonId of FREE_LESSON_IDS) {
    const level = lessonId.split("_")[0];
    const order = lessonId.slice(lessonId.lastIndexOf("_") + 1);
    const lesson = JSON.parse(
      await readFile(join(dataRoot, "lessons", level, `lesson-${order}.json`), "utf8"),
    );
    for (const vocabId of lesson.vocabulary_ids) {
      for (const path of Object.values(audioManifest.vocabulary[vocabId] ?? {})) {
        keys.add(toStorageKey(path));
      }
    }
  }

  return keys;
}
