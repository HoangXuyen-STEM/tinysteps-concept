import { notFound } from "next/navigation";
import { getLesson } from "@/lib/content/lesson-loader";
import { audioPath } from "@/lib/content/audio-manifest";
import { resolveAudioUrls } from "@/lib/content/audio-access";
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

  // Collect every audio key the client player needs, then resolve the whole set at once:
  // paid recordings are signed, and batching keeps that to a single Storage round trip.
  const audioKeys: string[] = [DIALOGUE_FULL_KEY];
  lesson.dialogue.lines.forEach((_, index) => audioKeys.push(lineKey(index)));
  lesson.exercises.forEach((ex) => {
    if (ex.type === "listen_choose") {
      ex.items.forEach((_, index) => audioKeys.push(exerciseListenKey(index)));
    }
  });

  const pathByKey = new Map(audioKeys.map((key) => [key, audioPath("lessons", id, key)]));
  const urlByPath = await resolveAudioUrls([...pathByKey.values()]);
  const audioUrls: Record<string, string | null> = Object.fromEntries(
    audioKeys.map((key) => {
      const path = pathByKey.get(key);
      return [key, (path && urlByPath.get(path)) ?? null];
    }),
  );

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