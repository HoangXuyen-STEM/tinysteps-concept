"use client";

import React, { useState } from "react";
import type { FillBlankExercise } from "@/lib/types/content-types";
import { isCorrect } from "@/lib/exercises/check-answer";
import { FeedbackBar } from "./feedback-bar";
import { labels } from "@/lib/i18n/labels";

type Props = {
  exercise: FillBlankExercise;
  exerciseIndex: number;
  onItemAnswer: (itemIndex: number, userAnswer: string) => void;
  onComplete: () => void;
};

export function FillBlankExerciseComponent({
  exercise,
  onItemAnswer,
  onComplete,
}: Props) {
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [inputValue, setInputValue] = useState("");
  const [feedback, setFeedback] = useState<{
    userAnswer: string;
    isCorrect: boolean;
  } | null>(null);

  const currentItem = exercise.items[currentItemIndex];

  const handleCheck = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (feedback || !inputValue.trim()) return;

    const correct = isCorrect(inputValue, currentItem.correct_answer);
    onItemAnswer(currentItemIndex, inputValue);
    setFeedback({ userAnswer: inputValue, isCorrect: correct });
  };

  const handleContinue = () => {
    setFeedback(null);
    setInputValue("");
    if (currentItemIndex < exercise.items.length - 1) {
      setCurrentItemIndex((prev) => prev + 1);
    } else {
      onComplete();
    }
  };

  if (!currentItem) return null;

  // Split prompt on ___
  const parts = currentItem.prompt.split("___");
  const prefix = parts[0] || "";
  const suffix = parts[1] || "";

  return (
    <div className="mx-auto max-w-xl">
      <h3 className="mb-6 text-xl font-bold text-slate-800">
        {exercise.instruction}
      </h3>

      <div className="mb-8 rounded-2xl bg-white p-8 shadow-sm">
        <form
          onSubmit={handleCheck}
          className="flex flex-wrap items-baseline gap-2 text-xl font-medium leading-loose"
        >
          {prefix && <span>{prefix}</span>}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={!!feedback}
            autoFocus
            className={`min-w-[120px] max-w-[200px] flex-1 border-b-2 bg-transparent px-2 py-1 text-center font-bold text-teal-700 outline-none transition-colors ${
              feedback
                ? feedback.isCorrect
                  ? "border-teal-500"
                  : "border-red-500 text-red-600"
                : "border-slate-300 focus:border-teal-500"
            }`}
          />
          {suffix && <span>{suffix}</span>}
          
          <button type="submit" className="hidden">Submit</button>
        </form>
      </div>

      {!feedback ? (
        <button
          onClick={() => handleCheck()}
          disabled={!inputValue.trim()}
          className="mt-6 w-full rounded-xl bg-teal-600 px-6 py-4 font-bold text-white transition-colors hover:bg-teal-700 disabled:bg-slate-300 sm:w-auto"
        >
          {labels.XAC_NHAN}
        </button>
      ) : (
        <FeedbackBar
          isCorrect={feedback.isCorrect}
          correctAnswer={currentItem.correct_answer}
          onContinue={handleContinue}
        />
      )}
    </div>
  );
}
