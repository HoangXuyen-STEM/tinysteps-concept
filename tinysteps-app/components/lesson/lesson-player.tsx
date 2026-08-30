"use client";

import React, { useState, useEffect, useMemo } from "react";
import type { Lesson } from "@/lib/types/content-types";
import { DialogueView } from "./dialogue-view";
import { ExerciseRunner } from "../exercises/exercise-runner";
import { AudioProvider } from "../audio/audio-provider";
import { startLesson, submitLessonAnswers } from "@/app/actions/lesson-progress-actions";
import type { ExerciseAnswer } from "@/lib/exercises/check-answer";
import { labels } from "@/lib/i18n/labels";
import { stationsFor, takeawayLines } from "@/lib/lesson/stations";
import { SayStation } from "./say-station";
import { TakeawayStation } from "./takeaway-station";

type Props = {
  lesson: Lesson;
  audioUrls: Record<string, string | null>;
  initialProgress: { status: string; score: number | null; completed_at: string | null } | null;
};

type PlayerState = "look" | "say" | "practice" | "submitting" | "takeaway";

export function LessonPlayer({ lesson, audioUrls, initialProgress }: Props) {
  const stations = useMemo(() => stationsFor(lesson), [lesson]);
  const firstStation: PlayerState = stations.includes("look")
    ? "look"
    : stations.includes("say")
      ? "say"
      : "practice";
  const [playerState, setPlayerState] = useState<PlayerState>(firstStation);
  const [submitError, setSubmitError] = useState(false);
  const [pendingAnswers, setPendingAnswers] = useState<ExerciseAnswer[] | null>(null);
  const [result, setResult] = useState<{
    score: number;
    correctCount: number;
    totalItems: number;
  } | null>(null);

  useEffect(() => {
    startLesson(lesson.id).catch(console.error);
  }, [lesson.id]);

  const goAfterLook = () => {
    if (stations.includes("say")) setPlayerState("say");
    else setPlayerState("practice");
  };

  const handleExercisesComplete = async (answers: ExerciseAnswer[]) => {
    setPendingAnswers(answers);
    setSubmitError(false);
    setPlayerState("submitting");
    try {
      const res = await submitLessonAnswers(lesson.id, answers);
      setResult(res);
      setPlayerState("takeaway");
    } catch (error) {
      console.error(error);
      setSubmitError(true);
    }
  };

  const retrySubmit = () => {
    if (pendingAnswers) void handleExercisesComplete(pendingAnswers);
  };

  const handleReplay = () => {
    setResult(null);
    setSubmitError(false);
    setPendingAnswers(null);
    setPlayerState(firstStation);
  };

  const lookCta = stations.includes("say") ? labels.TIEP_THEO_NOI : labels.TIEP_THEO_LUYEN;

  return (
    <AudioProvider>
      <div className="pb-10">
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm font-semibold capitalize text-teal-700">
            {lesson.level} · {lesson.estimated_minutes} min
          </p>
          {initialProgress?.status === "completed" && playerState !== "takeaway" && (
            <span className="inline-flex rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-800">
              {labels.DA_HOAN_THANH} · {initialProgress.score}%
            </span>
          )}
        </div>

        <h1 className="mb-2 text-2xl font-bold">{lesson.title}</h1>
        <p className="mb-8 text-slate-600">{lesson.scenario}</p>

        {playerState === "look" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <DialogueView dialogue={lesson.dialogue} audioUrls={audioUrls} />
            <div className="mt-8 flex justify-center">
              <button
                onClick={goAfterLook}
                className="w-full rounded-2xl bg-teal-600 px-8 py-4 font-bold text-white shadow-sm transition-colors hover:bg-teal-700 sm:w-auto"
              >
                {lookCta}
              </button>
            </div>
          </div>
        )}

        {playerState === "say" && (
          <SayStation
            dialogue={lesson.dialogue}
            audioUrls={audioUrls}
            onComplete={() => setPlayerState("practice")}
          />
        )}

        {playerState === "practice" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ExerciseRunner
              lessonId={lesson.id}
              exercises={lesson.exercises}
              audioUrls={audioUrls}
              onComplete={handleExercisesComplete}
            />
          </div>
        )}

        {(playerState === "submitting" || submitError) && (
          <div className="flex flex-col items-center justify-center py-20 text-teal-700">
            {!submitError ? (
              <>
                <div className="mb-4 size-10 animate-spin rounded-full border-4 border-teal-200 border-t-teal-600" />
                <p className="font-semibold">Đang tính điểm...</p>
              </>
            ) : (
              <div className="w-full max-w-sm rounded-2xl border border-red-200 bg-red-50 p-5 text-center text-red-800">
                <p className="font-semibold">{labels.LUU_LOI}</p>
                <button
                  type="button"
                  onClick={retrySubmit}
                  className="mt-4 rounded-xl bg-red-600 px-6 py-3 font-bold text-white hover:bg-red-700"
                >
                  {labels.TIEP_TUC}
                </button>
              </div>
            )}
          </div>
        )}

        {playerState === "takeaway" && result && (
          <TakeawayStation
            lines={takeawayLines(lesson)}
            dialogueLines={lesson.dialogue.lines}
            audioUrls={audioUrls}
            score={result.score}
            correctCount={result.correctCount}
            totalItems={result.totalItems}
            onReplay={handleReplay}
            listHref={`/lessons/${lesson.level}`}
          />
        )}
      </div>
    </AudioProvider>
  );
}
