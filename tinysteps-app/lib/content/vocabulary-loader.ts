import "server-only";
import starters from "@data/vocabulary/starters.json";
import movers from "@data/vocabulary/movers.json";
import flyers from "@data/vocabulary/flyers.json";
import ket from "@data/vocabulary/ket.json";
import pet from "@data/vocabulary/pet.json";
import { parseVocabulary } from "./content-schemas";
import { levels, type Level, type Vocab } from "@/lib/types/content-types";

const documents = [
  parseVocabulary(starters, "vocabulary/starters.json"), parseVocabulary(movers, "vocabulary/movers.json"),
  parseVocabulary(flyers, "vocabulary/flyers.json"), parseVocabulary(ket, "vocabulary/ket.json"), parseVocabulary(pet, "vocabulary/pet.json"),
];
const vocabularyByLevel = Object.fromEntries(documents.map((document) => [document.level, document.words])) as Record<Level, Vocab[]>;
const vocabularyById = new Map(documents.flatMap((document) => document.words.map((word) => [word.id, word])));

export const getLevels = (): readonly Level[] => levels;
export const getVocab = (level: Level): readonly Vocab[] => vocabularyByLevel[level];
export const getVocabById = (id: string): Vocab | undefined => vocabularyById.get(id);