import { notFound } from "next/navigation";
import { getLesson } from "@/lib/content/lesson-loader";
import { audioUrl } from "@/lib/content/audio-manifest";
import { getLessonProgress } from "@/lib/progress/lesson-progress-queries";
import { canOpenLesson } from "@/lib/access/paid-access";
import { levels, type Level } from "@/lib/types/content-types";
import { LessonPlayer } from "@/components/lesson/lesson-player";
import { PaywallNotice } from "@/components/paywall/paywall-notice";
import {
  lineKey,
  exerciseListenKey,
  DIALOGUE_FULL_KEY,
} from "@/lib/audio/audio-keys";

const isLevel = (value: string): value is Level =>
  levels.includes(value as Level);

export default async function LessonPage({
  params,
}: {
  params: Promise<{ level: string; id: string }>;
}) {
  const { level, id } = await params;
  const lesson = getLesson(id);

  if (!isLevel(level) || lesson?.level !== level) {
    notFound();
  }

  // Gate before any lesson body is loaded, so locked content never reaches the client.
  if (!(await canOpenLesson(id))) {
    return (
      <main>
        <PaywallNotice lessonTitle={lesson.title} />
      </main>
    );
  }

  // Fetch progress
  const progress = await getLessonProgress(id);

  // Pre-resolve all audio URLs needed by the client player
  const audioUrls: Record<string, string | null> = {};
  
  const resolveUrl = (key: string) => {
    return audioUrl("lessons", id, key) ?? null;
  };

  audioUrls[DIALOGUE_FULL_KEY] = resolveUrl(DIALOGUE_FULL_KEY);

  lesson.dialogue.lines.forEach((_, index) => {
    const key = lineKey(index);
    audioUrls[key] = resolveUrl(key);
  });

  lesson.exercises.forEach((ex) => {
    if (ex.type === "listen_choose") {
      ex.items.forEach((_, index) => {
        const key = exerciseListenKey(index);
        audioUrls[key] = resolveUrl(key);
      });
    }
  });

  return (
    <main>
      <LessonPlayer
        lesson={lesson}
        audioUrls={audioUrls}
        initialProgress={progress}
      />
    </main>
  );
}