import type { PublicWritingExercise, WritingExercise } from "@/lib/types/content-types";

/** Remove answer keys before a writing exercise crosses the server/client boundary. */
export function toPublicWritingExercise(exercise: WritingExercise): PublicWritingExercise {
  return {
    ...exercise,
    blanks: exercise.blanks.map(({ id, cue }) => ({ id, cue })),
  };
}
