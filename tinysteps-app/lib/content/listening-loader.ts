import "server-only";

import { listeningDocuments } from "./generated-listening-index";
import { parseListeningDocument } from "./content-schemas";
import type { Level, ListeningExercise } from "@/lib/types/content-types";

const documents = listeningDocuments.map((document, index) =>
  parseListeningDocument(document, `listening/import-${index + 1}.json`),
);
const listeningExercises = documents.flatMap((document) => document.exercises);
const exercisesById = new Map(listeningExercises.map((exercise) => [exercise.id, exercise]));
const exercisesByLevel = listeningExercises.reduce<Record<Level, ListeningExercise[]>>(
  (grouped, exercise) => {
    grouped[exercise.level].push(exercise);
    return grouped;
  },
  { starters: [], movers: [], flyers: [], ket: [], pet: [] },
);
Object.values(exercisesByLevel).forEach((items) => items.sort((left, right) => left.order - right.order));

export const getListeningByLevel = (level: Level): readonly ListeningExercise[] => exercisesByLevel[level];
export const getListeningExercise = (id: string): ListeningExercise | undefined => exercisesById.get(id);
