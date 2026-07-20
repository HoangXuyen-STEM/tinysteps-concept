"use client";

import { useState } from "react";
import { AudioButton } from "@/components/audio/audio-button";
import { labels } from "@/lib/i18n/labels";
import { REVIEW_RATINGS, type ReviewItem, type ReviewRating } from "@/lib/srs/review-types";

type Props = {
  item: ReviewItem;
  pending: boolean;
  onRate: (rating: ReviewRating) => void;
};

const RATING_STYLES: Record<ReviewRating, string> = {
  1: "border-red-300 text-red-700 hover:bg-red-50",
  2: "border-amber-300 text-amber-700 hover:bg-amber-50",
  3: "border-teal-300 text-teal-700 hover:bg-teal-50",
  4: "border-emerald-300 text-emerald-700 hover:bg-emerald-50",
};

export function Flashcard({ item, pending, onRate }: Props) {
  const [revealed, setRevealed] = useState(false);

  // Reset to the front whenever a new card is shown.
  // key on vocabId in the parent guarantees a fresh mount, so local state resets too.

  return (
    <div className="mx-auto max-w-md">
      <div className="rounded-3xl border border-slate-100 bg-white p-8 text-center shadow-sm">
        <p className="text-4xl font-bold text-slate-900">{item.word}</p>
        {item.ipa && <p className="mt-2 text-slate-500">/{item.ipa}/</p>}
        <div className="mt-4 flex justify-center">
          <AudioButton src={item.wordAudioUrl} label={labels.NGHE_TU} />
        </div>

        {revealed && (
          <div className="mt-6 border-t border-slate-100 pt-6 text-left animate-in fade-in slide-in-from-bottom-2 duration-300">
            <p className="text-lg leading-relaxed text-slate-800">{item.exampleSentence}</p>
            {item.imageHint && (
              <p className="mt-2 text-sm italic text-slate-500">{item.imageHint}</p>
            )}
            <div className="mt-3">
              <AudioButton src={item.sentenceAudioUrl} label={labels.NGHE_CAU} />
            </div>
          </div>
        )}
      </div>

      {!revealed ? (
        <button
          type="button"
          onClick={() => setRevealed(true)}
          className="mt-6 w-full rounded-2xl bg-teal-600 py-4 font-bold text-white transition-colors hover:bg-teal-700"
        >
          {labels.XEM_DAP_AN}
        </button>
      ) : (
        <div className="mt-6 grid grid-cols-4 gap-2">
          {REVIEW_RATINGS.map((r) => (
            <button
              key={r.value}
              type="button"
              disabled={pending}
              onClick={() => onRate(r.value)}
              className={`rounded-xl border-2 bg-white py-3 text-sm font-bold transition-colors disabled:opacity-50 ${RATING_STYLES[r.value]}`}
            >
              {r.vi}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
