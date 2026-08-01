import { notFound } from "next/navigation";
import { getWritingExercise } from "@/lib/content/writing-loader";
import { toPublicWritingExercise } from "@/lib/writing/public-writing";
import { getWritingProgress } from "@/lib/progress/writing-progress-queries";
import { canOpenWriting, FREE_WRITING_IDS } from "@/lib/access/paid-access";
import { levels, type Level } from "@/lib/types/content-types";
import { WritingPlayer } from "@/components/writing/writing-player";
import { PaywallNotice } from "@/components/paywall/paywall-notice";

const isLevel = (value: string): value is Level => levels.includes(value as Level);

export default async function WritingExercisePage({ params }: { params: Promise<{ level: string; id: string }> }) {
  const { level, id } = await params;
  const exercise = getWritingExercise(id);
  if (!isLevel(level) || exercise?.level !== level) notFound();

  if (!(await canOpenWriting(id))) {
    return (
      <main>
        <PaywallNotice
          backHref={`/writing/${level}`}
          backLabel="Quay lại danh sách Writing"
          freeCount={FREE_WRITING_IDS.length}
          lessonTitle={exercise.title}
        />
      </main>
    );
  }

  const progress = await getWritingProgress(id);
  return (
    <main>
      <WritingPlayer exercise={toPublicWritingExercise(exercise)} initialProgress={progress} />
    </main>
  );
}
