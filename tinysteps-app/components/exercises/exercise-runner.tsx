"use client";

import React, { useState, useRef } from "react";
import type { Exercise } from "@/lib/types/content-types";
import type { ExerciseAnswer } from "@/lib/exercises/check-answer";
import { listenIndexOffset } from "@/lib/audio/audio-keys";

import { MatchExerciseComponent } from "./match-exercise";
import { ArrangeExerciseComponent } from "./arrange-exercise";
import { ListenChooseExerciseComponent } from "./listen-choose-exercise";
import { FillBlankExerciseComponent } from "./fill-blank-exercise";
import { MultipleChoiceExerciseComponent } from "./multiple-choice-exercise";

type Props = {
  exercises: Exercise[];
  audioUrls: Record<string, string | null>;
  onComplete: (answers: ExerciseAnswer[]) => void;
};

export function ExerciseRunner({ exercises, audioUrls, onComplete }: Props) {
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);

  // We use a ref to accumulate answers instead of React state.
  // This avoids stale closure issues where onComplete might be called
  // with an outdated answers array during the final item's completion cycle.
  const answersRef = useRef<ExerciseAnswer[]>([]);

  const handleItemAnswer = (itemIndex: number, userAnswer: string) => {
    answersRef.current.push({
      exerciseIndex: currentExerciseIndex,
      itemIndex,
      userAnswer,
    });
  };

  const handleExerciseComplete = () => {
    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex((prev) => prev + 1);
    } else {
      // Pass the fully accumulated answers to the parent (LessonPlayer)
      onComplete([...answersRef.current]);
    }
  };

  if (exercises.length === 0) {
    onComplete([]);
    return null;
  }

  const exercise = exercises[currentExerciseIndex];
  if (!exercise) return null;

  // Render the appropriate component
  // Using key={currentExerciseIndex} ensures the component completely resets
  // if two exercises of the same type happen to be adjacent.
  switch (exercise.type) {
    case "match":
      return (
        <MatchExerciseComponent
          key={currentExerciseIndex}
          exercise={exercise}
          exerciseIndex={currentExerciseIndex}
          onItemAnswer={handleItemAnswer}
          onComplete={handleExerciseComplete}
        />
      );
    case "arrange":
      return (
        <ArrangeExerciseComponent
          key={currentExerciseIndex}
          exercise={exercise}
          exerciseIndex={currentExerciseIndex}
          onItemAnswer={handleItemAnswer}
          onComplete={handleExerciseComplete}
        />
      );
    case "listen_choose":
      return (
        <ListenChooseExerciseComponent
          key={currentExerciseIndex}
          exercise={exercise}
          exerciseIndex={currentExerciseIndex}
          audioUrls={audioUrls}
          listenIndexOffset={listenIndexOffset(exercises, currentExerciseIndex)}
          onItemAnswer={handleItemAnswer}
          onComplete={handleExerciseComplete}
        />
      );
    case "fill_blank":
      return (
        <FillBlankExerciseComponent
          key={currentExerciseIndex}
          exercise={exercise}
          exerciseIndex={currentExerciseIndex}
          onItemAnswer={handleItemAnswer}
          onComplete={handleExerciseComplete}
        />
      );
    case "multiple_choice":
      return (
        <MultipleChoiceExerciseComponent
          key={currentExerciseIndex}
          exercise={exercise}
          exerciseIndex={currentExerciseIndex}
          onItemAnswer={handleItemAnswer}
          onComplete={handleExerciseComplete}
        />
      );
    default:
      return null;
  }
}
