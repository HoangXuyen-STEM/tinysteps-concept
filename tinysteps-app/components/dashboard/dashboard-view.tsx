"use client";

import { useState } from "react";
import Link from "next/link";
import { labels } from "@/lib/i18n/labels";
import { levels, type Level } from "@/lib/types/content-types";
import type { LevelProgressSummary, NextLesson } from "@/lib/progress/dashboard-queries";
import type { StreakInfo } from "@/lib/progress/streak-calc";
import { LevelProgressBar } from "./level-progress-bar";
import { StreakChip } from "./streak-chip";
import { DueTodayChip } from "./due-today-chip";

type Props = {
  displayName: string | null;
  levelProgress: LevelProgressSummary;
  streak: StreakInfo;
  dueToday: number;
  nextLesson: NextLesson | null;
};

const totalCompleted = (summary: LevelProgressSummary) =>
  levels.reduce((sum, level) => sum + summary[level].completed, 0);

export function DashboardView({ displayName, levelProgress, streak, dueToday, nextLesson }: Props) {
  const hasAnyProgress = totalCompleted(levelProgress) > 0;
  const [showAllLevels, setShowAllLevels] = useState(false);
  const visibleLevels = levels.filter(
    (level) => level === "starters" || levelProgress[level].completed > 0 || showAllLevels,
  );

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-3">
        <h1 className="text-2xl font-bold text-slate-900">
          {labels.XIN_CHAO}
          {displayName ? `, ${displayName}` : ""}!
        </h1>
        <form action="/auth/signout" method="post">
          <button
            type="submit"
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-50"
          >
            {labels.DANG_XUAT}
          </button>
        </form>
      </div>

      <div className="flex gap-3">
        <StreakChip streak={streak} />
        <DueTodayChip count={dueToday} />
      </div>

      {hasAnyProgress ? (
        nextLesson ? (
          <Link
            href={`/lessons/${nextLesson.level}/${nextLesson.id}`}
            className="block rounded-2xl bg-teal-600 p-5 text-white shadow-sm transition-colors hover:bg-teal-700"
          >
            <p className="text-xs font-semibold uppercase tracking-wide text-teal-100">
              {labels.TIEP_TUC_HOC}
            </p>
            <p className="mt-1 text-lg font-bold">{nextLesson.title}</p>
          </Link>
        ) : (
          <Link
            href="/lessons"
            className="block rounded-2xl bg-teal-600 p-5 text-center font-bold text-white shadow-sm transition-colors hover:bg-teal-700"
          >
            {labels.XEM_TAT_CA_BAI_HOC}
          </Link>
        )
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <p className="text-slate-600">{labels.CHUA_CO_TIEN_DO}</p>
          <Link
            href="/lessons"
            className="mt-4 inline-block rounded-xl bg-teal-600 px-6 py-3 font-bold text-white transition-colors hover:bg-teal-700"
          >
            {labels.BAT_DAU_HOC}
          </Link>
        </div>
      )}

      <div>
        <h2 className="mb-3 text-lg font-bold text-slate-800">{labels.BAI_HOC}</h2>
        <div className="space-y-3">
          {visibleLevels.map((level: Level) => (
            <LevelProgressBar
              key={level}
              level={level}
              completed={levelProgress[level].completed}
              total={levelProgress[level].total}
            />
          ))}
        </div>
        <button
          type="button"
          onClick={() => setShowAllLevels((open) => !open)}
          className="mt-3 text-sm font-semibold text-teal-700 hover:underline"
        >
          {showAllLevels ? labels.AN_LO_TRINH : labels.XEM_LO_TRINH}
        </button>
      </div>
    </div>
  );
}
