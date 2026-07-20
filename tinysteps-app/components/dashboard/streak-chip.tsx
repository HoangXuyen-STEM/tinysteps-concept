import { labels } from "@/lib/i18n/labels";
import type { StreakInfo } from "@/lib/progress/streak-calc";

export function StreakChip({ streak }: { streak: StreakInfo }) {
  return (
    <div className="flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-2">
        <span className="text-2xl">🔥</span>
        <span className="text-2xl font-extrabold text-slate-900">{streak.count}</span>
      </div>
      <p className="mt-1 text-xs font-medium text-slate-500">
        {labels.CHUOI_NGAY} ({labels.NGAY})
      </p>
      {streak.nudge && streak.count > 0 && (
        <p className="mt-2 text-xs font-semibold text-amber-600">
          {labels.HOC_HOM_NAY_GIU_CHUOI}
        </p>
      )}
    </div>
  );
}
