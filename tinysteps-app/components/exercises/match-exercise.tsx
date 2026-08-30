"use client";

import React, { useState, useMemo } from "react";
import type { MatchExercise } from "@/lib/types/content-types";
import { isCorrect } from "@/lib/exercises/check-answer";
import { resolveMatchIllustration } from "@/lib/content/illustration-manifest";
import { FeedbackBar } from "./feedback-bar";

type Props = {
  lessonId: string;
  exercise: MatchExercise;
  exerciseIndex: number;
  onItemAnswer: (itemIndex: number, userAnswer: string) => void;
  onComplete: () => void;
};

export function MatchExerciseComponent({
  lessonId,
  exercise,
  exerciseIndex,
  onItemAnswer,
  onComplete,
}: Props) {
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [feedback, setFeedback] = useState<{
    userAnswer: string;
    isCorrect: boolean;
  } | null>(null);
  const [failedImageKey, setFailedImageKey] = useState<string | null>(null);

  // Derive unique choices from all correct answers in this exercise and shuffle them
  const choices = useMemo(() => {
    const allAnswers = exercise.items.map((item) => item.correct_answer);
    // Fisher-Yates shuffle
    const shuffled = [...allAnswers];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }, [exercise]);

  const currentItem = exercise.items[currentItemIndex];
  const illustration = resolveMatchIllustration(
    lessonId,
    exerciseIndex,
    currentItemIndex,
  );
  const showIllustration = illustration && failedImageKey !== illustration.assetKey;

  const handleSelect = (choice: string) => {
    if (feedback) return; // Prevent multiple selections

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

  if (!currentItem) return null;

  return (
    <div className="mx-auto max-w-xl">
      <h3 className="mb-6 text-xl font-bold text-slate-800">
        {exercise.instruction}
      </h3>

      {currentItem.prompt ? (
        <p className="mb-6 text-center text-lg font-semibold text-slate-800">{currentItem.prompt}</p>
      ) : null}

      <div className="mb-8 flex justify-center">
        <div className="flex aspect-square w-full max-w-sm items-center justify-center overflow-hidden rounded-2xl border-2 border-slate-200 bg-white shadow-sm">
          {showIllustration ? (
            // eslint-disable-next-line @next/next/no-img-element -- runtime CDN base is deployment-configured
            <img
              alt={illustration.alt}
              className="h-full w-full object-cover"
              height={512}
              key={illustration.assetKey}
              onError={() => setFailedImageKey(illustration.assetKey)}
              src={illustration.src}
              width={512}
            />
          ) : (
            <svg
              aria-label={illustration?.alt ?? currentItem.image_hint ?? currentItem.prompt ?? ""}
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
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {choices.map((choice, i) => {
          const isSelected = feedback?.userAnswer === choice;
          let btnClass =
            "rounded-xl border-2 px-4 py-4 text-center font-semibold transition-all ";
          
          if (!feedback) {
            btnClass += "border-slate-200 bg-white hover:border-teal-500 hover:bg-teal-50";
          } else if (isSelected) {
            btnClass += feedback.isCorrect
              ? "border-teal-500 bg-teal-100 text-teal-900"
              : "border-red-500 bg-red-100 text-red-900";
          } else {
            btnClass += "border-slate-200 bg-white opacity-50";
          }

          return (
            <button
              key={i}
              type="button"
              disabled={!!feedback}
              onClick={() => handleSelect(choice)}
              className={btnClass}
            >
              {choice}
            </button>
          );
        })}
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
