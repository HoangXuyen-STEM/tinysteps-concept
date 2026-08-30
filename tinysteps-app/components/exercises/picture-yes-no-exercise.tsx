"use client";

import React, { useState } from "react";
import type { PictureYesNoExercise } from "@/lib/types/content-types";
import { isCorrect } from "@/lib/exercises/check-answer";
import { FeedbackBar } from "./feedback-bar";

type Props = {
  lessonId: string;
  exercise: PictureYesNoExercise;
  exerciseIndex: number;
  onItemAnswer: (itemIndex: number, userAnswer: string) => void;
  onComplete: () => void;
};

export function PictureYesNoExerciseComponent({
  exercise,
  onItemAnswer,
  onComplete,
}: Props) {
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [feedback, setFeedback] = useState<{
    userAnswer: string;
    isCorrect: boolean;
  } | null>(null);

  const currentItem = exercise.items[currentItemIndex];
  if (!currentItem) return null;

  const handleSelect = (choice: "yes" | "no") => {
    if (feedback) return;
    const correct = isCorrect(choice, currentItem.correct_answer);
    onItemAnswer(currentItemIndex, choice);
    setFeedback({ userAnswer: choice, isCorrect: correct });
  };

  const handleContinue = () => {
    setFeedback(null);
    if (currentItemIndex < exercise.items.length - 1) {
      setCurrentItemIndex((prev) => prev + 1);
    } else {
      onComplete();
    }
  };

  return (
    <div className="mx-auto max-w-xl">
      <h3 className="mb-6 text-xl font-bold text-slate-800">{exercise.instruction}</h3>
      <div className="mb-6 flex justify-center">
        <div className="flex aspect-video w-full items-center justify-center overflow-hidden rounded-2xl border-2 border-slate-200 bg-white shadow-sm">
          <svg
            aria-label={exercise.image_hint}
            className="size-20 text-slate-300"
            fill="none"
            role="img"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
          >
            <path d="m3 16 5-5 4 4 2-2 7 7" />
            <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Z" />
            <circle cx="8.5" cy="7.5" r="1.5" />
          </svg>
        </div>
      </div>
      <p className="mb-6 text-center text-lg font-semibold text-slate-800">{currentItem.sentence}</p>
      <div className="grid grid-cols-2 gap-3">
        {(["yes", "no"] as const).map((choice) => (
          <button
            key={choice}
            type="button"
            disabled={!!feedback}
            onClick={() => handleSelect(choice)}
            className="rounded-xl border-2 border-slate-200 bg-white px-4 py-4 text-center font-semibold capitalize hover:border-teal-500 hover:bg-teal-50 disabled:opacity-50"
          >
            {choice}
          </button>
        ))}
      </div>
      {feedback && (
        <FeedbackBar
          isCorrect={feedback.isCorrect}
          correctAnswer={currentItem.correct_answer}
          onContinue={handleContinue}
        />
      )}
    </div>
  );
}
