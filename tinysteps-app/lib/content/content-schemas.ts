import { z } from "zod";
import type { AudioManifest, Lesson, Level, ListeningDocument, TopicsDocument, Vocab, WritingDocument } from "@/lib/types/content-types";

export const levelSchema = z.enum(["starters", "movers", "flyers", "ket", "pet"]);
const stringList = z.array(z.string());

const vocabSchema = z.object({
  id: z.string(), word: z.string(), ipa: z.string(), pos: z.string(), topic_ids: stringList,
  example_sentence: z.string(), image_hint: z.string(), related_words: stringList.default([]), frequency_rank: z.number(),
});
export const vocabularyDocumentSchema = z.object({ level: levelSchema, total_words: z.number().int(), words: z.array(vocabSchema) });

const exerciseBase = z.object({ instruction: z.string() });
const matchExercise = exerciseBase.extend({
  type: z.literal("match"),
  items: z.array(z.object({
    image_hint: z.string().optional(),
    prompt: z.string().optional(),
    correct_answer: z.string(),
  })),
});
const pictureYesNoExercise = exerciseBase.extend({
  type: z.literal("picture_yes_no"),
  image_hint: z.string(),
  items: z.array(z.object({
    sentence: z.string(),
    correct_answer: z.enum(["yes", "no"]),
  })),
});
const arrangeExercise = exerciseBase.extend({ type: z.literal("arrange"), items: z.array(z.object({ words: stringList, correct_answer: z.string() })) });
const listenExercise = exerciseBase.extend({ type: z.literal("listen_choose"), items: z.array(z.object({ audio_text: z.string(), options: stringList, correct_answer: z.string() })) });
const blankExercise = exerciseBase.extend({ type: z.literal("fill_blank"), items: z.array(z.object({ prompt: z.string(), correct_answer: z.string() })) });
const choiceExercise = exerciseBase.extend({ type: z.literal("multiple_choice"), items: z.array(z.object({ prompt: z.string(), options: stringList, correct_answer: z.string(), image_hint: z.string().optional() })) });

export const lessonSchema = z.object({
  id: z.string(), level: levelSchema, topic_id: z.string(), order: z.number().int(), title: z.string(), scenario: z.string(), estimated_minutes: z.number().int(),
  dialogue: z.object({ setting: z.string(), characters: z.array(z.object({ id: z.string(), name: z.string(), role: z.string() })), lines: z.array(z.object({ character_id: z.string(), text: z.string(), note: z.string().optional() })) }),
  vocabulary_ids: stringList, grammar_ids: stringList,
  exercises: z.array(z.discriminatedUnion("type", [matchExercise, arrangeExercise, listenExercise, blankExercise, choiceExercise, pictureYesNoExercise])).min(2).max(8),
  ai_conversation: z.object({ role: z.string(), scenario: z.string(), opening_line: z.string(), level_constraints: z.object({ max_sentence_length: z.number().int(), allowed_grammar: stringList, target_vocabulary: stringList }), success_criteria: z.string().optional() }),
  schema_version: z.union([z.literal(1), z.literal(2)]).optional(),
  stations: z.array(z.enum(["look", "say", "practice", "takeaway"])).optional(),
  takeaway_lines: stringList.optional(),
  scene_image_hint: z.string().optional(),
});

export const topicsDocumentSchema = z.object({
  total_topics: z.number().int(),
  topic_groups: z.array(z.object({ group_id: z.enum(["school", "daily_life"]), group_name: z.string(), topic_ids: stringList })),
  topics: z.array(z.object({ id: z.string(), name: z.string(), description: z.string(), group_id: z.enum(["school", "daily_life"]), spiral: z.array(z.object({ level: levelSchema, focus: z.string(), can_do_statement: z.string(), example_sentences: stringList, vocabulary_ids: stringList.optional(), grammar_ids: stringList.optional() })) })),
});

export const audioManifestSchema = z.object({
  generated_at: z.string(),
  voice_female: z.string(),
  voice_male: z.string(),
  vocabulary: z.record(z.string(), z.record(z.string(), z.string())),
  lessons: z.record(z.string(), z.record(z.string(), z.string())),
  listening: z.record(z.string(), z.string()).default({}),
});

const writingBlankSchema = z.object({
  id: z.string().regex(/^b\d+$/),
  cue: z.string().trim().min(1),
  accepted_answers: z.array(z.string().trim().min(1)).min(1),
});

const expectedWritingBlanks: Record<Level, number> = {
  starters: 5,
  movers: 6,
  flyers: 7,
  ket: 8,
  pet: 8,
};

const writingExerciseSchema = z.object({
  id: z.string(),
  level: levelSchema,
  order: z.number().int().min(1).max(5),
  title: z.string().trim().min(1),
  scenario: z.string().trim().min(1),
  estimated_minutes: z.number().int().min(3).max(15),
  grammar_ids: z.array(z.string()).min(1),
  instruction: z.string().trim().min(1),
  passage: z.string().trim().min(1),
  blanks: z.array(writingBlankSchema),
}).superRefine((exercise, context) => {
  const expectedId = `${exercise.level}_writing_${String(exercise.order).padStart(3, "0")}`;
  if (exercise.id !== expectedId) {
    context.addIssue({ code: "custom", path: ["id"], message: `Expected writing id ${expectedId}` });
  }
  if (exercise.blanks.length !== expectedWritingBlanks[exercise.level]) {
    context.addIssue({ code: "custom", path: ["blanks"], message: `Expected ${expectedWritingBlanks[exercise.level]} blanks` });
  }

  const blankIds = new Set(exercise.blanks.map((blank) => blank.id));
  if (blankIds.size !== exercise.blanks.length) {
    context.addIssue({ code: "custom", path: ["blanks"], message: "Blank ids must be unique" });
  }
  const placeholders = [...exercise.passage.matchAll(/\{\{(b\d+)\}\}/g)].map((match) => match[1]);
  if (placeholders.length !== exercise.blanks.length || new Set(placeholders).size !== placeholders.length) {
    context.addIssue({ code: "custom", path: ["passage"], message: "Each blank must have exactly one unique placeholder" });
  }
  if (placeholders.some((id) => !blankIds.has(id)) || exercise.blanks.some((blank) => !placeholders.includes(blank.id))) {
    context.addIssue({ code: "custom", path: ["passage"], message: "Placeholders and blank ids must match" });
  }
});

export const writingDocumentSchema = z.object({
  level: levelSchema,
  total_exercises: z.literal(5),
  exercises: z.array(writingExerciseSchema).length(5),
}).superRefine((document, context) => {
  document.exercises.forEach((exercise, index) => {
    if (exercise.level !== document.level || exercise.order !== index + 1) {
      context.addIssue({ code: "custom", path: ["exercises", index], message: "Writing exercises must match the document level and be ordered 1–5" });
    }
  });
});

const listeningBlankCategorySchema = z.enum(["number", "color", "address", "age"]);

const listeningBlankSchema = z.object({
  id: z.string().regex(/^b\d+$/),
  cue: z.string().trim().min(1),
  category: listeningBlankCategorySchema,
  accepted_answers: z.array(z.string().trim().min(1)).min(1),
});

const expectedListeningBlanks: Record<Level, number> = {
  starters: 5,
  movers: 6,
  flyers: 7,
  ket: 8,
  pet: 8,
};

const listeningExerciseSchema = z.object({
  id: z.string(),
  level: levelSchema,
  order: z.number().int().min(1).max(3),
  title: z.string().trim().min(1),
  scenario: z.string().trim().min(1),
  estimated_minutes: z.number().int().min(3).max(15),
  grammar_ids: z.array(z.string()).min(1),
  instruction: z.string().trim().min(1),
  audio_text: z.string().trim().min(1),
  passage: z.string().trim().min(1),
  transcript: z.string().trim().min(1),
  blanks: z.array(listeningBlankSchema),
}).superRefine((exercise, context) => {
  const expectedId = `${exercise.level}_listening_${String(exercise.order).padStart(3, "0")}`;
  if (exercise.id !== expectedId) {
    context.addIssue({ code: "custom", path: ["id"], message: `Expected listening id ${expectedId}` });
  }
  if (exercise.blanks.length !== expectedListeningBlanks[exercise.level]) {
    context.addIssue({ code: "custom", path: ["blanks"], message: `Expected ${expectedListeningBlanks[exercise.level]} blanks` });
  }

  const blankIds = new Set(exercise.blanks.map((blank) => blank.id));
  if (blankIds.size !== exercise.blanks.length) {
    context.addIssue({ code: "custom", path: ["blanks"], message: "Blank ids must be unique" });
  }
  const placeholders = [...exercise.passage.matchAll(/\{\{(b\d+)\}\}/g)].map((match) => match[1]);
  if (placeholders.length !== exercise.blanks.length || new Set(placeholders).size !== placeholders.length) {
    context.addIssue({ code: "custom", path: ["passage"], message: "Each blank must have exactly one unique placeholder" });
  }
  if (placeholders.some((id) => !blankIds.has(id)) || exercise.blanks.some((blank) => !placeholders.includes(blank.id))) {
    context.addIssue({ code: "custom", path: ["passage"], message: "Placeholders and blank ids must match" });
  }

  const categoriesUsed = new Set(exercise.blanks.map((blank) => blank.category));
  const allCategories: Array<z.infer<typeof listeningBlankCategorySchema>> = ["number", "color", "address", "age"];
  if (!allCategories.every((category) => categoriesUsed.has(category))) {
    context.addIssue({ code: "custom", path: ["blanks"], message: "Must cover all 4 categories: number, color, address, age" });
  }

  if (exercise.audio_text.includes("{{") || exercise.transcript.includes("{{")) {
    context.addIssue({ code: "custom", path: ["audio_text"], message: "audio_text/transcript must not contain unfilled placeholders" });
  }
});

export const listeningDocumentSchema = z.object({
  level: levelSchema,
  total_exercises: z.literal(3),
  exercises: z.array(listeningExerciseSchema).length(3),
}).superRefine((document, context) => {
  document.exercises.forEach((exercise, index) => {
    if (exercise.level !== document.level || exercise.order !== index + 1) {
      context.addIssue({ code: "custom", path: ["exercises", index], message: "Listening exercises must match the document level and be ordered 1–3" });
    }
  });
});

function parseWithSource<T>(schema: z.ZodType<T>, value: unknown, source: string): T {
  const result = schema.safeParse(value);
  if (result.success) return result.data;
  throw new Error(`Invalid content in ${source}: ${result.error.issues.map((issue) => issue.message).join(", ")}`);
}

export const parseVocabulary = (value: unknown, source: string) => parseWithSource(vocabularyDocumentSchema, value, source) as { level: Level; total_words: number; words: Vocab[] };
export const parseLesson = (value: unknown, source: string) => parseWithSource(lessonSchema, value, source) as Lesson;
export const parseTopics = (value: unknown) => topicsDocumentSchema.parse(value) as TopicsDocument;
export const parseAudioManifest = (value: unknown) => audioManifestSchema.parse(value) as AudioManifest;
export const parseWritingDocument = (value: unknown, source: string) => parseWithSource(writingDocumentSchema, value, source) as WritingDocument;
export const parseListeningDocument = (value: unknown, source: string) => parseWithSource(listeningDocumentSchema, value, source) as ListeningDocument;
