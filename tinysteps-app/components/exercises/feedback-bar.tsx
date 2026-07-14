import React from "react";
import { labels } from "@/lib/i18n/labels";

type FeedbackBarProps = {
  isCorrect: boolean;
  correctAnswer?: string; // Optional: show correct answer if wrong
  onContinue: () => void;
};

export function FeedbackBar({
  isCorrect,
  correctAnswer,
  onContinue,
}: FeedbackBarProps) {
  return (
    <div
      className={`mt-6 rounded-2xl p-4 sm:flex sm:items-center sm:justify-between ${
        isCorrect ? "bg-teal-50 text-teal-900" : "bg-red-50 text-red-900"
      }`}
    >
      <div>
        <p className="font-bold text-lg">{isCorrect ? labels.DUNG : labels.SAI}</p>
        {!isCorrect && correctAnswer && (
          <p className="mt-1 text-sm opacity-90">
            {labels.DAP_AN_DUNG}: <strong className="font-bold">{correctAnswer}</strong>
          </p>
        )}
      </div>
      <button
        type="button"
        onClick={onContinue}
        className={`mt-4 w-full rounded-xl px-6 py-3 font-bold text-white transition-colors sm:mt-0 sm:w-auto ${
          isCorrect
            ? "bg-teal-600 hover:bg-teal-700"
            : "bg-red-600 hover:bg-red-700"
        }`}
      >
        {labels.TIEP_TUC}
      </button>
    </div>
  );
}
