"use client";

import React from "react";
import type { Lesson } from "@/lib/types/content-types";
import { AudioButton } from "../audio/audio-button";
import { lineKey, DIALOGUE_FULL_KEY } from "@/lib/audio/audio-keys";
import { labels } from "@/lib/i18n/labels";

type DialogueViewProps = {
  dialogue: Lesson["dialogue"];
  audioUrls: Record<string, string | null>;
};

export function DialogueView({ dialogue, audioUrls }: DialogueViewProps) {
  // Map character_id to Character object for easy lookup
  const characterMap = new Map(dialogue.characters.map((c) => [c.id, c]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between rounded-2xl bg-white p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-slate-800">{dialogue.setting}</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {dialogue.characters.map((char) => (
              <span
                key={char.id}
                className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
              >
                {char.name} <span className="ml-1 font-normal opacity-75">({char.role})</span>
              </span>
            ))}
          </div>
        </div>
        <AudioButton
          src={audioUrls[DIALOGUE_FULL_KEY] ?? null}
          label={labels.NGHE_TAT_CA}
        />
      </div>

      <div className="space-y-4 rounded-2xl bg-white p-5 shadow-sm">
        {dialogue.lines.map((line, index) => {
          const char = characterMap.get(line.character_id);
          // Simple visual distinction: alternate left/right padding based on character index
          // Usually there are 2 characters, char_a and char_b.
          const isCharA = line.character_id === dialogue.characters[0]?.id;

          return (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                !isCharA ? "flex-row-reverse text-right" : ""
              }`}
            >
              <AudioButton src={audioUrls[lineKey(index)] ?? null} compact />
              
              <div
                className={`max-w-[85%] rounded-2xl p-3 ${
                  isCharA
                    ? "rounded-tl-none bg-teal-50 text-teal-900"
                    : "rounded-tr-none bg-slate-100 text-slate-800"
                }`}
              >
                <p className="mb-1 text-xs font-bold opacity-70">
                  {char?.name || line.character_id}
                </p>
                <p className="text-[15px] leading-relaxed">{line.text}</p>
                {line.note && (
                  <p className="mt-1 text-xs italic opacity-75">{line.note}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
