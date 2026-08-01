import type { ListeningExercise, PublicListeningExercise } from "@/lib/types/content-types";

/**
 * Strip everything that would leak the answer before the client submits:
 * `accepted_answers` per blank, plus `audio_text` and `transcript` (both contain
 * the fully-filled passage). Only `passage` (gapped) and `cue`/`category` per
 * blank cross the server/client boundary pre-submit.
 */
export function toPublicListeningExercise(exercise: ListeningExercise): PublicListeningExercise {
  return {
    id: exercise.id,
    level: exercise.level,
    order: exercise.order,
    title: exercise.title,
    scenario: exercise.scenario,
    estimated_minutes: exercise.estimated_minutes,
    grammar_ids: exercise.grammar_ids,
    instruction: exercise.instruction,
    passage: exercise.passage,
    blanks: exercise.blanks.map(({ id, cue, category }) => ({ id, cue, category })),
  };
}
