import Link from "next/link";
import { levels } from "@/lib/types/content-types";
import { getListeningByLevel } from "@/lib/content/listening-loader";
import { getListeningCompletedCounts } from "@/lib/progress/listening-progress-queries";
import { labels } from "@/lib/i18n/labels";

export default async function ListeningPage() {
  const completedCounts = await getListeningCompletedCounts();

  return (
    <main>
      <h1 className="text-2xl font-bold text-slate-900">{labels.LUYEN_NGHE}</h1>
      <p className="mt-2 text-slate-600">
        Nghe đoạn audio và điền số đếm, tuổi, màu sắc hoặc địa chỉ còn thiếu.
      </p>

      <div className="mt-6 space-y-4">
        {levels.map((level) => {
          const total = getListeningByLevel(level).length;
          const completed = completedCounts[level];
          const percent = Math.round((completed / total) * 100);
          return (
            <Link
              className="block rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-teal-300 hover:shadow-md"
              href={`/listening/${level}`}
              key={level}
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold capitalize text-slate-900">{level}</h2>
                  <p className="mt-1 text-sm font-medium text-slate-500">{total} bài nghe điền từ</p>
                </div>
                <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">
                  {completed}/{total} {labels.HOAN_THANH}
                </span>
              </div>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full bg-teal-500 transition-all" style={{ width: `${percent}%` }} />
              </div>
            </Link>
          );
        })}
      </div>
    </main>
  );
}
