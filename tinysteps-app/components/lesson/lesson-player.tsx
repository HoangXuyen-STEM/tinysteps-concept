"use client";

import React, { useState, useEffect } from "react";
import type { Lesson } from "@/lib/types/content-types";
import { DialogueView } from "./dialogue-view";
import { ExerciseRunner } from "../exercises/exercise-runner";
import { AudioProvider } from "../audio/audio-provider";
import { startLesson, submitLessonAnswers } from "@/app/actions/lesson-progress-actions";
import type { ExerciseAnswer } from "@/lib/exercises/check-answer";
import { labels } from "@/lib/i18n/labels";
import Link from "next/link";

type Props = {
  lesson: Lesson;
  audioUrls: Record<string, string | null>;
  initialProgress: { status: string; score: number | null; completed_at: string | null } | null;
};

type PlayerState = "dialogue" | "exercises" | "submitting" | "result";

export function LessonPlayer({ lesson, audioUrls, initialProgress }: Props) {
  const [playerState, setPlayerState] = useState<PlayerState>("dialogue");
  const [result, setResult] = useState<{
    score: number;
    correctCount: number;
    totalItems: number;
  } | null>(null);

  // On mount, call startLesson (fire and forget)
  useEffect(() => {
    startLesson(lesson.id).catch(console.error);
  }, [lesson.id]);

  const handleStartExercises = () => {
    setPlayerState("exercises");
  };

  const handleExercisesComplete = async (answers: ExerciseAnswer[]) => {
    setPlayerState("submitting");
    try {
      const res = await submitLessonAnswers(lesson.id, answers);
      setResult(res);
      setPlayerState("result");
    } catch (error) {
      console.error(error);
      // Fallback/error state: for MVP just show an alert and go back to exercises or let them retry
      alert("Đã xảy ra lỗi khi lưu kết quả. Vui lòng thử lại.");
      setPlayerState("exercises");
    }
  };

  const handleReplay = () => {
    setResult(null);
    setPlayerState("dialogue");
  };

  return (
    <AudioProvider>
      <div className="pb-10">
        {/* Header (Progress badge & level) */}
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm font-semibold capitalize text-teal-700">
            {lesson.level} · {lesson.estimated_minutes} min
          </p>
          {initialProgress?.status === "completed" && playerState !== "result" && (
            <span className="inline-flex rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-800">
              {labels.DA_HOAN_THANH} · {initialProgress.score}%
            </span>
          )}
        </div>

        <h1 className="mb-2 text-2xl font-bold">{lesson.title}</h1>
        <p className="mb-8 text-slate-600">{lesson.scenario}</p>

        {playerState === "dialogue" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <DialogueView dialogue={lesson.dialogue} audioUrls={audioUrls} />
            <div className="mt-8 flex justify-center">
              <button
                onClick={handleStartExercises}
                className="w-full rounded-2xl bg-teal-600 px-8 py-4 font-bold text-white shadow-sm transition-colors hover:bg-teal-700 sm:w-auto"
              >
                {labels.BAT_DAU}
              </button>
            </div>
          </div>
        )}

        {playerState === "exercises" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ExerciseRunner
              lessonId={lesson.id}
              exercises={lesson.exercises}
              audioUrls={audioUrls}
              onComplete={handleExercisesComplete}
            />
          </div>
        )}

        {playerState === "submitting" && (
          <div className="flex flex-col items-center justify-center py-20 text-teal-700 animate-pulse">
            <div className="size-10 rounded-full border-4 border-teal-200 border-t-teal-600 animate-spin mb-4" />
            <p className="font-semibold">Đang tính điểm...</p>
          </div>
        )}

        {playerState === "result" && result && (
          <div className="animate-in zoom-in-95 duration-500 mx-auto max-w-sm rounded-3xl bg-white p-8 text-center shadow-lg border border-slate-100">
            <div className="mb-4 text-6xl">
              {result.score >= 80 ? "🏆" : result.score >= 50 ? "👍" : "💪"}
            </div>
            <h2 className="mb-2 text-2xl font-bold text-slate-800">
              {result.score >= 80
                ? labels.XUAT_SAC
                : result.score >= 50
                ? labels.TOT_LAM
                : labels.CO_GANG_THEM}
            </h2>
            <div className="my-6">
              <span className="text-5xl font-extrabold text-teal-600">
                {result.score}%
              </span>
              <p className="mt-2 text-sm font-medium text-slate-500">
                {result.correctCount} / {result.totalItems} {labels.CAU_DUNG}
              </p>
            </div>
            
            <div className="flex flex-col gap-3">
              <Link
                href={`/lessons/${lesson.level}`}
                className="rounded-xl bg-teal-600 px-6 py-3 font-bold text-white hover:bg-teal-700 transition-colors"
              >
                {labels.VE_DANH_SACH}
              </Link>
              <button
                onClick={handleReplay}
                className="rounded-xl bg-slate-100 px-6 py-3 font-bold text-slate-600 hover:bg-slate-200 transition-colors"
              >
                {labels.LAM_LAI}
              </button>
            </div>
          </div>
        )}
      </div>
    </AudioProvider>
  );
}
