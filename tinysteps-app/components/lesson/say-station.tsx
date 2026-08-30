"use client";

import React, { useState } from "react";
import type { Lesson } from "@/lib/types/content-types";
import { AudioButton } from "../audio/audio-button";
import { lineKey } from "@/lib/audio/audio-keys";
import { labels } from "@/lib/i18n/labels";

type Props = {
  dialogue: Lesson["dialogue"];
  audioUrls: Record<string, string | null>;
  onComplete: () => void;
};

export function SayStation({ dialogue, audioUrls, onComplete }: Props) {
  const [index, setIndex] = useState(0);
  const line = dialogue.lines[index];
  if (!line) return null;

  const character = dialogue.characters.find((c) => c.id === line.character_id);
  const isLast = index >= dialogue.lines.length - 1;

  const handleSaid = () => {
    if (isLast) onComplete();
    else setIndex((prev) => prev + 1);
  };

  return (
    <div className="animate-in fade-in duration-500">
      <p className="mb-4 text-sm font-semibold text-teal-700">{labels.NOI_THEO}</p>
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          {character?.name ?? line.character_id}
        </p>
        <p className="mb-4 text-2xl font-bold text-slate-900">{line.text}</p>
        <AudioButton src={audioUrls[lineKey(index)] ?? null} label={labels.NGHE} />
      </div>
      <div className="mt-8 flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={handleSaid}
          className="w-full rounded-2xl bg-teal-600 px-8 py-4 font-bold text-white shadow-sm transition-colors hover:bg-teal-700 sm:w-auto"
        >
          {labels.TOI_DA_NOI}
        </button>
        <button
          type="button"
          onClick={onComplete}
          className="text-sm font-medium text-slate-500 underline-offset-2 hover:underline"
        >
          {labels.BO_QUA_NOI}
        </button>
      </div>
    </div>
  );
}
