import { NextResponse } from "next/server";
import { getAudioManifest } from "@/lib/content/audio-manifest";
import { getIllustrationCount } from "@/lib/content/illustration-manifest";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import { getTopics } from "@/lib/content/topics-loader";
import { getLevels, getVocab } from "@/lib/content/vocabulary-loader";

export function GET() {
  const levels = getLevels();
  const vocabulary = Object.fromEntries(levels.map((level) => [level, getVocab(level).length]));
  const lessons = Object.fromEntries(levels.map((level) => [level, getLessonsByLevel(level).length]));
  const manifest = getAudioManifest();

  return NextResponse.json({
    vocabulary,
    vocabularyTotal: Object.values(vocabulary).reduce((total, count) => total + count, 0),
    lessons,
    lessonTotal: Object.values(lessons).reduce((total, count) => total + count, 0),
    topics: getTopics().length,
    audioManifest: { vocabulary: Object.keys(manifest.vocabulary).length, lessons: Object.keys(manifest.lessons).length },
    illustrationManifest: { assets: getIllustrationCount() },
  });
}
