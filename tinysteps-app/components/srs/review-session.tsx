"use client";

import { useState, useTransition } from "react";
import { AudioProvider } from "@/components/audio/audio-provider";
import { submitReview } from "@/app/actions/srs-review-actions";
import { labels } from "@/lib/i18n/labels";
import {
  REVIEW_BATCH_SIZE,
  type ReviewItem,
  type ReviewRating,
} from "@/lib/srs/review-types";
import { Flashcard } from "./flashcard";

type Props = {
  items: ReviewItem[];
  dueCount: number;
  newCount: number;
};

type Phase = "reviewing" | "batch-break" | "done";

export function ReviewSession({ items, dueCount, newCount }: Props) {
  const [index, setIndex] = useState(0);
  const [reviewed, setReviewed] = useState(0);
  const [phase, setPhase] = useState<Phase>("reviewing");
  const [error, setError] = useState(false);
  const [pending, startTransition] = useTransition();

  const total = items.length;
  const current = items[index];

  const handleRate = (rating: ReviewRating) => {
    if (!current) return;
    const isLast = index === total - 1;
    setError(false);

    startTransition(async () => {
      try {
        await submitReview(current.vocabId, rating, isLast);
      } catch {
        setError(true);
        return; // stay on the card so the user can retry
      }

      const nextReviewed = reviewed + 1;
      setReviewed(nextReviewed);

      if (isLast) {
        setPhase("done");
      } else if (nextReviewed % REVIEW_BATCH_SIZE === 0) {
        setPhase("batch-break");
      } else {
        setIndex(index + 1);
      }
    });
  };

  const continueAfterBreak = () => {
    setIndex(index + 1);
    setPhase("reviewing");
  };

  if (phase === "done") {
    return (
      <div className="mx-auto max-w-md rounded-3xl border border-slate-100 bg-white p-8 text-center shadow-sm">
        <div className="mb-3 text-5xl">🎉</div>
        <h2 className="text-2xl font-bold text-slate-800">{labels.DA_XONG_HOM_NAY}</h2>
        <p className="mt-3 text-slate-600">
          {labels.DA_ON} {reviewed} {labels.TU}.
        </p>
      </div>
    );
  }

  if (phase === "batch-break") {
    return (
      <div className="mx-auto max-w-md rounded-3xl border border-slate-100 bg-white p-8 text-center shadow-sm">
        <div className="mb-3 text-4xl">✓</div>
        <h2 className="text-xl font-bold text-slate-800">{labels.HOAN_THANH_LUOT_ON}</h2>
        <p className="mt-2 text-sm text-slate-500">
          {labels.DA_ON} {reviewed} / {total} {labels.TU}.
        </p>
        <div className="mt-6 flex flex-col gap-3">
          <button
            type="button"
            onClick={continueAfterBreak}
            className="rounded-xl bg-teal-600 px-6 py-3 font-bold text-white transition-colors hover:bg-teal-700"
          >
            {labels.TIEP_TUC_ON}
          </button>
          <button
            type="button"
            onClick={() => setPhase("done")}
            className="rounded-xl bg-slate-100 px-6 py-3 font-bold text-slate-600 transition-colors hover:bg-slate-200"
          >
            {labels.DUNG_LAI}
          </button>
        </div>
      </div>
    );
  }

  if (!current) return null;

  return (
    <AudioProvider>
      <div className="pb-10">
        <div className="mb-6 flex items-center justify-between text-sm text-slate-500">
          <span className="font-semibold capitalize text-teal-700">{labels.ON_TAP_TU_VUNG}</span>
          <span>
            {index + 1} / {total}
          </span>
        </div>

        <Flashcard key={current.vocabId} item={current} pending={pending} onRate={handleRate} />

        {error && (
          <p className="mx-auto mt-4 max-w-md text-center text-sm text-red-600">
            Không lưu được kết quả. Vui lòng thử lại.
          </p>
        )}

        <p className="mx-auto mt-6 max-w-md text-center text-xs text-slate-400">
          {dueCount} {labels.CAN_ON} · {newCount} {labels.TU_MOI}
        </p>
      </div>
    </AudioProvider>
  );
}
