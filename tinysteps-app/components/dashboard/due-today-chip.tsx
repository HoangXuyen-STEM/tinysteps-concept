import Link from "next/link";
import { labels } from "@/lib/i18n/labels";

export function DueTodayChip({ count }: { count: number }) {
  return (
    <Link
      href="/review"
      className="flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:border-teal-300"
    >
      <div className="flex items-center gap-2">
        <span className="text-2xl">📚</span>
        <span className="text-2xl font-extrabold text-slate-900">{count}</span>
      </div>
      <p className="mt-1 text-xs font-medium text-slate-500">{labels.TU_CAN_ON}</p>
    </Link>
  );
}
