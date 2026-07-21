"use client";

import React, { useState } from "react";
import type { MultipleChoiceExercise } from "@/lib/types/content-types";
import { isCorrect } from "@/lib/exercises/check-answer";
import { resolveMultipleChoiceIllustration } from "@/lib/content/illustration-manifest";
import { FeedbackBar } from "./feedback-bar";

type Props = {
  lessonId: string;
  exercise: MultipleChoiceExercise;
  exerciseIndex: number;
  onItemAnswer: (itemIndex: number, userAnswer: string) => void;
  onComplete: () => void;
};

export function MultipleChoiceExerciseComponent({
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

  const currentItem = exercise.items[currentItemIndex];

  // These prompts ask "What is this?" about a picture. The real image is generated
  // in batches; until one exists (or if it fails to load) we show the image_hint as
  // a text cue so the question stays answerable.
  const illustration = resolveMultipleChoiceIllustration(
    lessonId,
    exerciseIndex,
    currentItemIndex,
  );
  const showIllustration = illustration && failedImageKey !== illustration.assetKey;

  const handleSelect = (choice: string) => {
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

  if (!currentItem) return null;

  return (
    <div className="mx-auto max-w-xl">
      <h3 className="mb-6 text-xl font-bold text-slate-800">
        {exercise.instruction}
      </h3>

      {showIllustration ? (
        <div className="mb-6 flex justify-center">
          <div className="flex aspect-square w-full max-w-sm items-center justify-center overflow-hidden rounded-2xl border-2 border-slate-200 bg-white shadow-sm">
            {/* eslint-disable-next-line @next/next/no-img-element -- runtime CDN base is deployment-configured */}
            <img
              alt={illustration.alt}
              className="h-full w-full object-cover"
              height={512}
              key={illustration.assetKey}
              onError={() => setFailedImageKey(illustration.assetKey)}
              src={illustration.src}
              width={512}
            />
          </div>
        </div>
      ) : currentItem.image_hint ? (
        <div className="mb-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-center">
          <p className="text-base leading-relaxed text-slate-600">{currentItem.image_hint}</p>
        </div>
      ) : null}

      <div className="mb-8 rounded-2xl bg-white p-8 shadow-sm">
        <p className="text-xl font-medium leading-relaxed text-slate-800">
          {currentItem.prompt}
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {currentItem.options.map((option, i) => {
          const isSelected = feedback?.userAnswer === option;
          let btnClass =
            "rounded-xl border-2 px-6 py-4 text-left font-semibold transition-all ";

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
              onClick={() => handleSelect(option)}
              className={btnClass}
            >
              {option}
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
