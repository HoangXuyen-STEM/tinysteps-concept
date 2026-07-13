import { z } from "zod";
import type { AudioManifest, Lesson, Level, TopicsDocument, Vocab } from "@/lib/types/content-types";

export const levelSchema = z.enum(["starters", "movers", "flyers", "ket", "pet"]);
const stringList = z.array(z.string());

const vocabSchema = z.object({
  id: z.string(), word: z.string(), ipa: z.string(), pos: z.string(), topic_ids: stringList,
  example_sentence: z.string(), image_hint: z.string(), related_words: stringList.default([]), frequency_rank: z.number(),
});
export const vocabularyDocumentSchema = z.object({ level: levelSchema, total_words: z.number().int(), words: z.array(vocabSchema) });

const exerciseBase = z.object({ instruction: z.string() });
const matchExercise = exerciseBase.extend({ type: z.literal("match"), items: z.array(z.object({ image_hint: z.string(), correct_answer: z.string() })) });
const arrangeExercise = exerciseBase.extend({ type: z.literal("arrange"), items: z.array(z.object({ words: stringList, correct_answer: z.string() })) });
const listenExercise = exerciseBase.extend({ type: z.literal("listen_choose"), items: z.array(z.object({ audio_text: z.string(), options: stringList, correct_answer: z.string() })) });
const blankExercise = exerciseBase.extend({ type: z.literal("fill_blank"), items: z.array(z.object({ prompt: z.string(), correct_answer: z.string() })) });
const choiceExercise = exerciseBase.extend({ type: z.literal("multiple_choice"), items: z.array(z.object({ prompt: z.string(), options: stringList, correct_answer: z.string() })) });

export const lessonSchema = z.object({
  id: z.string(), level: levelSchema, topic_id: z.string(), order: z.number().int(), title: z.string(), scenario: z.string(), estimated_minutes: z.number().int(),
  dialogue: z.object({ setting: z.string(), characters: z.array(z.object({ id: z.string(), name: z.string(), role: z.string() })), lines: z.array(z.object({ character_id: z.string(), text: z.string(), note: z.string().optional() })) }),
  vocabulary_ids: stringList, grammar_ids: stringList, exercises: z.array(z.discriminatedUnion("type", [matchExercise, arrangeExercise, listenExercise, blankExercise, choiceExercise])),
  ai_conversation: z.object({ role: z.string(), scenario: z.string(), opening_line: z.string(), level_constraints: z.object({ max_sentence_length: z.number().int(), allowed_grammar: stringList, target_vocabulary: stringList }), success_criteria: z.string().optional() }),
});

export const topicsDocumentSchema = z.object({
  total_topics: z.number().int(),
  topic_groups: z.array(z.object({ group_id: z.enum(["school", "daily_life"]), group_name: z.string(), topic_ids: stringList })),
  topics: z.array(z.object({ id: z.string(), name: z.string(), description: z.string(), group_id: z.enum(["school", "daily_life"]), spiral: z.array(z.object({ level: levelSchema, focus: z.string(), can_do_statement: z.string(), example_sentences: stringList, vocabulary_ids: stringList.optional(), grammar_ids: stringList.optional() })) })),
});

export const audioManifestSchema = z.object({ generated_at: z.string(), voice_female: z.string(), voice_male: z.string(), vocabulary: z.record(z.string(), z.record(z.string(), z.string())), lessons: z.record(z.string(), z.record(z.string(), z.string())) });
function parseWithSource<T>(schema: z.ZodType<T>, value: unknown, source: string): T {
  const result = schema.safeParse(value);
  if (result.success) return result.data;
  throw new Error(`Invalid content in ${source}: ${result.error.issues.map((issue) => issue.message).join(", ")}`);
}

export const parseVocabulary = (value: unknown, source: string) => parseWithSource(vocabularyDocumentSchema, value, source) as { level: Level; total_words: number; words: Vocab[] };
export const parseLesson = (value: unknown, source: string) => parseWithSource(lessonSchema, value, source) as Lesson;
export const parseTopics = (value: unknown) => topicsDocumentSchema.parse(value) as TopicsDocument;
export const parseAudioManifest = (value: unknown) => audioManifestSchema.parse(value) as AudioManifest;