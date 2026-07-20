import Link from "next/link";
import type { Level } from "@/lib/types/content-types";

type Props = {
  level: Level;
  completed: number;
  total: number;
};

export function LevelProgressBar({ level, completed, total }: Props) {
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <Link
      href={`/lessons/${level}`}
      className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:border-teal-300"
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold capitalize text-slate-900">{level}</span>
        <span className="text-sm font-medium text-slate-500">
          {completed}/{total}
        </span>
      </div>
      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full bg-teal-500 transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </Link>
  );
}
