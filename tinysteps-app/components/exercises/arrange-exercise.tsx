"use client";

import React, { useState, useMemo } from "react";
import type { ArrangeExercise } from "@/lib/types/content-types";
import { isCorrect } from "@/lib/exercises/check-answer";
import { FeedbackBar } from "./feedback-bar";
import { labels } from "@/lib/i18n/labels";

type Props = {
  exercise: ArrangeExercise;
  exerciseIndex: number;
  onItemAnswer: (itemIndex: number, userAnswer: string) => void;
  onComplete: () => void;
};

export function ArrangeExerciseComponent({
  exercise,
  onItemAnswer,
  onComplete,
}: Props) {
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<{
    userAnswer: string;
    isCorrect: boolean;
  } | null>(null);

  const currentItem = exercise.items[currentItemIndex];

  // Shuffle the initial words once per item
  const availableWords = useMemo(() => {
    if (!currentItem) return [];
    const shuffled = [...currentItem.words];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }, [currentItem]);

  const handleSelectWord = (word: string, index: number) => {
    if (feedback) return;
    setSelectedWords((prev) => [...prev, `${word}-${index}`]);
  };

  const handleRemoveWord = (wordId: string) => {
    if (feedback) return;
    setSelectedWords((prev) => prev.filter((w) => w !== wordId));
  };

  const handleCheck = () => {
    if (feedback || selectedWords.length === 0) return;

    // Remove the -index suffix to get the actual words
    const userAnswer = selectedWords.map((w) => w.split("-").slice(0, -1).join("-")).join(" ");
    const correct = isCorrect(userAnswer, currentItem.correct_answer);

    onItemAnswer(currentItemIndex, userAnswer);
    setFeedback({ userAnswer, isCorrect: correct });
  };

  const handleContinue = () => {
    setFeedback(null);
    setSelectedWords([]);
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

      <div className="mb-8 min-h-[120px] rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap gap-2 border-b-2 border-slate-100 pb-4 min-h-[50px]">
          {selectedWords.map((wordId) => {
            const word = wordId.split("-").slice(0, -1).join("-");
            return (
              <button
                key={wordId}
                onClick={() => handleRemoveWord(wordId)}
                disabled={!!feedback}
                className="rounded-xl border border-teal-200 bg-teal-50 px-4 py-2 font-semibold text-teal-900 transition-colors hover:bg-teal-100 disabled:opacity-100"
              >
                {word}
              </button>
            );
          })}
        </div>

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {availableWords.map((word, index) => {
            const wordId = `${word}-${index}`;
            const isUsed = selectedWords.includes(wordId);
            return (
              <button
                key={wordId}
                onClick={() => handleSelectWord(word, index)}
                disabled={isUsed || !!feedback}
                className={`rounded-xl border-2 border-slate-200 px-4 py-2 font-semibold transition-all ${
                  isUsed
                    ? "bg-slate-100 text-transparent border-slate-100" // Invisible but takes space
                    : "bg-white hover:border-slate-300"
                }`}
              >
                {word}
              </button>
            );
          })}
        </div>
      </div>

      {!feedback ? (
        <button
          onClick={handleCheck}
          disabled={selectedWords.length === 0}
          className="mt-6 w-full rounded-xl bg-teal-600 px-6 py-4 font-bold text-white transition-colors hover:bg-teal-700 disabled:bg-slate-300 sm:w-auto"
        >
          {labels.KIEM_TRA}
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
