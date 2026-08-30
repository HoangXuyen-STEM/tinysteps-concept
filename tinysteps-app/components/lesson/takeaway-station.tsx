"use client";

import React from "react";
import Link from "next/link";
import { AudioButton } from "../audio/audio-button";
import { lineKey } from "@/lib/audio/audio-keys";
import { labels } from "@/lib/i18n/labels";

type Props = {
  lines: string[];
  dialogueLines: { text: string }[];
  audioUrls: Record<string, string | null>;
  score: number;
  correctCount: number;
  totalItems: number;
  onReplay: () => void;
  listHref: string;
};

export function TakeawayStation({
  lines,
  dialogueLines,
  audioUrls,
  score,
  correctCount,
  totalItems,
  onReplay,
  listHref,
}: Props) {
  return (
    <div className="animate-in fade-in duration-500">
      <h2 className="mb-4 text-2xl font-bold text-slate-900">{labels.CAU_MANG_DI}</h2>
      <ul className="space-y-3 rounded-2xl bg-white p-5 shadow-sm">
        {lines.map((text, i) => {
          const dialogueIndex = dialogueLines.findIndex((line) => {
            const a = line.text.trim().toLowerCase();
            const b = text.trim().toLowerCase();
            return a === b || a.includes(b) || b.includes(a);
          });
          const src =
            dialogueIndex >= 0 ? audioUrls[lineKey(dialogueIndex)] ?? null : null;
          return (
            <li key={`${text}-${i}`} className="flex items-center justify-between gap-3">
              <p className="font-semibold text-slate-800">{text}</p>
              {src ? <AudioButton src={src} label={labels.NGHE_LAI_CAU} /> : null}
            </li>
          );
        })}
      </ul>
      <p className="mt-4 text-sm text-slate-500">
        {score}% · {correctCount}/{totalItems} {labels.CAU_DUNG}
      </p>
      <div className="mt-8 flex flex-col gap-3">
        <Link
          href={listHref}
          className="rounded-xl bg-teal-600 px-6 py-3 text-center font-bold text-white hover:bg-teal-700"
        >
          {labels.VE_DANH_SACH}
        </Link>
        <button
          type="button"
          onClick={onReplay}
          className="rounded-xl bg-slate-100 px-6 py-3 font-bold text-slate-600 hover:bg-slate-200"
        >
          {labels.LAM_LAI}
        </button>
      </div>
    </div>
  );
}
