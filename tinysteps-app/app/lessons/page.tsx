import Link from "next/link";
import { getLevels, getVocab } from "@/lib/content/vocabulary-loader";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import { getCompletedCountByLevel } from "@/lib/progress/lesson-progress-queries";
import { labels } from "@/lib/i18n/labels";

export default async function LessonsPage() {
  const levels = getLevels();
  const completedCounts = await getCompletedCountByLevel();

  return (
    <main>
      <h1 className="text-2xl font-bold text-slate-800">{labels.BAI_HOC}</h1>
      <p className="mt-2 text-slate-600">
        Chọn một cấp độ và luyện tiếng Anh trong ngữ cảnh thực tế.
      </p>
      
      <div className="mt-6 space-y-4">
        {levels.map((level) => {
          const totalLessons = getLessonsByLevel(level).length;
          const vocabCount = getVocab(level).length;
          const completed = completedCounts[level] || 0;
          const percent = totalLessons > 0 ? Math.round((completed / totalLessons) * 100) : 0;

          return (
            <Link
              className="block rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-teal-300 hover:shadow-md"
              href={`/lessons/${level}`}
              key={level}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold capitalize text-slate-900">
                    {level}
                  </h2>
                  <p className="mt-1 text-sm font-medium text-slate-500">
                    {totalLessons} {labels.BAI_HOC.toLowerCase()} · {vocabCount} từ vựng
                  </p>
                </div>
                {completed > 0 && (
                  <div className="text-right">
                    <span className="inline-block rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">
                      {completed}/{totalLessons} {labels.HOAN_THANH}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Simple progress bar */}
              <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full bg-teal-500 transition-all duration-500"
                  style={{ width: `${percent}%` }}
                />
              </div>
            </Link>
          );
        })}
      </div>
    </main>
  );
}