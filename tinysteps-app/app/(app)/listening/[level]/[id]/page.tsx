import { notFound } from "next/navigation";
import { getListeningExercise } from "@/lib/content/listening-loader";
import { toPublicListeningExercise } from "@/lib/listening/public-listening";
import { getListeningProgress } from "@/lib/progress/listening-progress-queries";
import { listeningAudioUrl } from "@/lib/content/audio-manifest";
import { canOpenListening, FREE_LISTENING_IDS } from "@/lib/access/paid-access";
import { levels, type Level } from "@/lib/types/content-types";
import { ListeningPlayer } from "@/components/listening/listening-player";
import { PaywallNotice } from "@/components/paywall/paywall-notice";

const isLevel = (value: string): value is Level => levels.includes(value as Level);

export default async function ListeningExercisePage({ params }: { params: Promise<{ level: string; id: string }> }) {
  const { level, id } = await params;
  const exercise = getListeningExercise(id);
  if (!isLevel(level) || exercise?.level !== level) notFound();

  if (!(await canOpenListening(id))) {
    return (
      <main>
        <PaywallNotice
          backHref={`/listening/${level}`}
          backLabel="Quay lại danh sách Listening"
          freeCount={FREE_LISTENING_IDS.length}
          lessonTitle={exercise.title}
        />
      </main>
    );
  }

  const progress = await getListeningProgress(id);
  const audioUrl = listeningAudioUrl(id);
  return (
    <main>
      <ListeningPlayer
        audioUrl={audioUrl}
        exercise={toPublicListeningExercise(exercise)}
        initialProgress={progress}
      />
    </main>
  );
}
