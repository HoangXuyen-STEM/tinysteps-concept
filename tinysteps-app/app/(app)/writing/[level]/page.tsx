import Link from "next/link";
import { notFound } from "next/navigation";
import { getWritingByLevel } from "@/lib/content/writing-loader";
import { getWritingLevelProgress } from "@/lib/progress/writing-progress-queries";
import { hasPaidAccess, isFreeWriting } from "@/lib/access/paid-access";
import { levels, type Level } from "@/lib/types/content-types";
import { labels } from "@/lib/i18n/labels";

const isLevel = (value: string): value is Level => levels.includes(value as Level);

export default async function WritingLevelPage({ params }: { params: Promise<{ level: string }> }) {
  const { level } = await params;
  if (!isLevel(level)) notFound();
  const exercises = getWritingByLevel(level);
  const progress = await getWritingLevelProgress(level);
  const isPaid = await hasPaidAccess();

  return (
    <main>
      <h1 className="text-2xl font-bold capitalize text-slate-900">{labels.WRITING} · {level}</h1>
      <p className="mt-2 text-slate-600">Hoàn thành mỗi đoạn với ít nhất 80% câu đúng.</p>
      <div className="mt-6 space-y-3">
        {exercises.map((exercise) => {
          const itemProgress = progress[exercise.id];
          const isLocked = !isPaid && !isFreeWriting(exercise.id);
          return (
            <Link
              className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:border-teal-300 hover:bg-slate-50"
              href={`/writing/${level}/${exercise.id}`}
              key={exercise.id}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-900">{exercise.order}. {exercise.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{exercise.scenario}</p>
                  <p className="mt-2 text-xs font-medium text-slate-500">
                    {exercise.blanks.length} ô trống · {exercise.estimated_minutes} phút
                  </p>
                </div>
                {itemProgress?.status === "completed" ? (
                  <span className="shrink-0 rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-800">{itemProgress.best_score}%</span>
                ) : itemProgress ? (
                  <span className="shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">{itemProgress.best_score ?? 0}%</span>
                ) : isLocked ? (
                  <span className="shrink-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500" title={labels.CAN_GOI_TRON_BO}>🔒</span>
                ) : null}
              </div>
            </Link>
          );
        })}
      </div>
    </main>
  );
}
