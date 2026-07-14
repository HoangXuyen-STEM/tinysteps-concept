/**
 * Audio manifest key helpers.
 * Generates the zero-padded keys that match the audio manifest format.
 *
 * Manifest uses 1-indexed, zero-padded two-digit suffixes:
 *   line_01, line_02, ..., exercise_listen_01, etc.
 */
import type { Exercise } from "@/lib/types/content-types";

/** Build a manifest key: `${prefix}_${(index+1).padStart(2,'0')}` */
export function audioKey(prefix: string, index: number): string {
  return `${prefix}_${String(index + 1).padStart(2, "0")}`;
}

/** Key for dialogue line at array index. e.g. index 0 → "line_01" */
export function lineKey(index: number): string {
  return audioKey("line", index);
}

/** Key for listen-choose exercise audio at array index. e.g. index 0 → "exercise_listen_01" */
export function exerciseListenKey(index: number): string {
  return audioKey("exercise_listen", index);
}

/** The fixed key for the full dialogue audio. */
export const DIALOGUE_FULL_KEY = "dialogue_full";

/**
 * generate_audio.py numbers listen_choose audio with ONE counter across the whole
 * lesson, not reset per exercise (see tinysteps-data/generate_audio.py). Given the
 * lesson's exercise list and the index of the exercise currently being played, this
 * returns how many listen_choose items appeared in EARLIER exercises — the offset a
 * listen_choose exercise must add to its own item index to hit the right manifest key.
 */
export function listenIndexOffset(exercises: Exercise[], exerciseIndex: number): number {
  return exercises
    .slice(0, exerciseIndex)
    .reduce((sum, ex) => (ex.type === "listen_choose" ? sum + ex.items.length : sum), 0);
}
