export const levels = ["starters", "movers", "flyers", "ket", "pet"] as const;
export type Level = (typeof levels)[number];

export type Vocab = {
  id: string; word: string; ipa: string; pos: string; topic_ids: string[];
  example_sentence: string; image_hint: string; related_words: string[]; frequency_rank: number;
};

export type DialogueLine = { character_id: string; text: string; note?: string };
export type Character = { id: string; name: string; role: string };
export type MatchExercise = { type: "match"; instruction: string; items: { image_hint: string; correct_answer: string }[] };
export type ArrangeExercise = { type: "arrange"; instruction: string; items: { words: string[]; correct_answer: string }[] };
export type ListenChooseExercise = { type: "listen_choose"; instruction: string; items: { audio_text: string; options: string[]; correct_answer: string }[] };
export type FillBlankExercise = { type: "fill_blank"; instruction: string; items: { prompt: string; correct_answer: string }[] };
export type MultipleChoiceExercise = { type: "multiple_choice"; instruction: string; items: { prompt: string; options: string[]; correct_answer: string }[] };
export type Exercise = MatchExercise | ArrangeExercise | ListenChooseExercise | FillBlankExercise | MultipleChoiceExercise;

export type Lesson = {
  id: string; level: Level; topic_id: string; order: number; title: string; scenario: string; estimated_minutes: number;
  dialogue: { setting: string; characters: Character[]; lines: DialogueLine[] };
  vocabulary_ids: string[]; grammar_ids: string[]; exercises: Exercise[];
  ai_conversation: { role: string; scenario: string; opening_line: string; level_constraints: { max_sentence_length: number; allowed_grammar: string[]; target_vocabulary: string[] }; success_criteria?: string };
};

export type Topic = { id: string; name: string; description: string; group_id: "school" | "daily_life"; spiral: TopicSpiral[] };
export type TopicSpiral = { level: Level; focus: string; can_do_statement: string; example_sentences: string[]; vocabulary_ids?: string[]; grammar_ids?: string[] };
export type TopicGroup = { group_id: "school" | "daily_life"; group_name: string; topic_ids: string[] };
export type TopicsDocument = { total_topics: number; topic_groups: TopicGroup[]; topics: Topic[] };
export type AudioManifest = { generated_at: string; voice_female: string; voice_male: string; vocabulary: Record<string, Record<string, string>>; lessons: Record<string, Record<string, string>> };