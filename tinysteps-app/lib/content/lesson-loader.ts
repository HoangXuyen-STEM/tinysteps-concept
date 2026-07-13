import "server-only";
import { lessonDocuments } from "./generated-lessons-index";
import { parseLesson } from "./content-schemas";
import type { Lesson, Level } from "@/lib/types/content-types";

const lessons = lessonDocuments.map((document, index) => parseLesson(document, `lessons/import-${index + 1}.json`));
const lessonsById = new Map(lessons.map((lesson) => [lesson.id, lesson]));
const lessonsByLevel = lessons.reduce<Record<Level, Lesson[]>>(
  (grouped, lesson) => { grouped[lesson.level].push(lesson); return grouped; },
  { starters: [], movers: [], flyers: [], ket: [], pet: [] },
);
Object.values(lessonsByLevel).forEach((items) => items.sort((left, right) => left.order - right.order));

export const getLessonsByLevel = (level: Level): readonly Lesson[] => lessonsByLevel[level];
export const getLesson = (id: string): Lesson | undefined => lessonsById.get(id);