import "server-only";

import { writingDocuments } from "./generated-writing-index";
import { parseWritingDocument } from "./content-schemas";
import type { Level, WritingExercise } from "@/lib/types/content-types";

const documents = writingDocuments.map((document, index) =>
  parseWritingDocument(document, `writing/import-${index + 1}.json`),
);
const writingExercises = documents.flatMap((document) => document.exercises);
const exercisesById = new Map(writingExercises.map((exercise) => [exercise.id, exercise]));
const exercisesByLevel = writingExercises.reduce<Record<Level, WritingExercise[]>>(
  (grouped, exercise) => {
    grouped[exercise.level].push(exercise);
    return grouped;
  },
  { starters: [], movers: [], flyers: [], ket: [], pet: [] },
);
Object.values(exercisesByLevel).forEach((items) => items.sort((left, right) => left.order - right.order));

export const getWritingByLevel = (level: Level): readonly WritingExercise[] => exercisesByLevel[level];
export const getWritingExercise = (id: string): WritingExercise | undefined => exercisesById.get(id);
