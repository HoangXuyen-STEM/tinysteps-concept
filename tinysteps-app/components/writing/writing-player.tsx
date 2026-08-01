"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { PublicWritingExercise } from "@/lib/types/content-types";
import { startWriting, submitWritingAnswers } from "@/app/actions/writing-progress-actions";
import type { WritingScoreResult } from "@/lib/writing/check-writing-answers";
import { labels } from "@/lib/i18n/labels";

type Props = {
  exercise: PublicWritingExercise;
  initialProgress: { status: string; best_score: number | null } | null;
};

const PLACEHOLDER = /\{\{(b\d+)\}\}/g;

export function WritingPlayer({ exercise, initialProgress }: Props) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<WritingScoreResult | null>(null);
  const [lockedCorrectIds, setLockedCorrectIds] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    startWriting(exercise.id).catch(console.error);
  }, [exercise.id]);

  const blankMap = useMemo(
    () => new Map(exercise.blanks.map((blank) => [blank.id, blank])),
    [exercise.blanks],
  );
  const resultMap = useMemo(
    () => new Map((result?.results ?? []).map((item) => [item.blankId, item])),
    [result],
  );
  const passageParts = useMemo(() => exercise.passage.split(PLACEHOLDER), [exercise.passage]);
  const allFilled = exercise.blanks.every((blank) => values[blank.id]?.trim());

  const submit = async () => {
    if (!allFilled || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const checked = await submitWritingAnswers(
        exercise.id,
        exercise.blanks.map((blank) => ({ blankId: blank.id, value: values[blank.id] ?? "" })),
      );
      setResult(checked);
      setLockedCorrectIds((current) => {
        const next = new Set(current);
        checked.results.filter((item) => item.isCorrect).forEach((item) => next.add(item.blankId));
        return next;
      });
    } catch (submissionError) {
      console.error(submissionError);
      setError("Không thể chấm hoặc lưu bài lúc này. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  };

  const retryIncorrect = () => {
    if (!result) return;
    const incorrectIds = new Set(result.results.filter((item) => !item.isCorrect).map((item) => item.blankId));
    setValues((current) => Object.fromEntries(
      Object.entries(current).map(([id, value]) => [id, incorrectIds.has(id) ? "" : value]),
    ));
    setResult(null);
    setError(null);
  };

  const replay = () => {
    setValues({});
    setLockedCorrectIds(new Set());
    setResult(null);
    setError(null);
  };

  return (
    <div className="pb-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-semibold capitalize text-teal-700">
          {exercise.level} · {exercise.estimated_minutes} min
        </p>
        {initialProgress?.best_score !== null && initialProgress?.best_score !== undefined && (
          <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">
            {labels.DIEM_CAO_NHAT}: {initialProgress.best_score}%
          </span>
        )}
      </div>

      <h1 className="text-2xl font-bold text-slate-900">{exercise.title}</h1>
      <p className="mt-2 text-slate-600">{exercise.scenario}</p>
      <p className="mt-6 rounded-xl bg-teal-50 px-4 py-3 text-sm font-medium text-teal-900">
        {exercise.instruction} Điền toàn bộ đoạn văn rồi chấm bài.
      </p>

      <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
        <div className="text-lg leading-[3.75rem] text-slate-800">
          {passageParts.map((part, index) => {
            if (index % 2 === 0) return <span key={`text-${index}`}>{part}</span>;
            const blank = blankMap.get(part);
            if (!blank) return null;
            const itemResult = resultMap.get(blank.id);
            const isLocked = lockedCorrectIds.has(blank.id);
            const isWrong = itemResult?.isCorrect === false;
            return (
              <span className="mx-1 inline-flex min-w-28 flex-col align-middle leading-tight" key={blank.id}>
                <input
                  aria-label={`Ô trống ${blank.id}, gợi ý ${blank.cue}`}
                  autoCapitalize="none"
                  autoComplete="off"
                  className={`h-9 rounded-lg border px-2 text-center text-base font-bold outline-none transition-colors ${
                    isLocked
                      ? "border-teal-400 bg-teal-50 text-teal-800"
                      : isWrong
                        ? "border-red-400 bg-red-50 text-red-700"
                        : "border-slate-300 bg-white text-slate-800 focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                  }`}
                  disabled={isLocked || submitting || !!result}
                  onChange={(event) => setValues((current) => ({ ...current, [blank.id]: event.target.value }))}
                  value={values[blank.id] ?? ""}
                />
                <span className="mt-1 text-center text-xs text-slate-500">({blank.cue})</span>
                {isWrong && (
                  <span className="mt-1 text-center text-xs font-semibold text-red-600">
                    → {itemResult.correctAnswer}
                  </span>
                )}
              </span>
            );
          })}
        </div>
      </div>

      {error && <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-medium text-red-700">{error}</p>}

      {!result ? (
        <button
          className="mt-6 w-full rounded-xl bg-teal-600 px-6 py-4 font-bold text-white transition-colors hover:bg-teal-700 disabled:bg-slate-300 sm:w-auto"
          disabled={!allFilled || submitting}
          onClick={submit}
          type="button"
        >
          {submitting ? "Đang chấm bài…" : labels.CHAM_BAI}
        </button>
      ) : (
        <div className={`mt-6 rounded-2xl border p-5 ${result.completed ? "border-teal-200 bg-teal-50" : "border-amber-200 bg-amber-50"}`}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className={`font-bold ${result.completed ? "text-teal-800" : "text-amber-800"}`}>
                {result.completed ? `${labels.DAT_YEU_CAU} 🎉` : labels.CHUA_DAT}
              </p>
              <p className="mt-1 text-sm text-slate-600">
                {result.correctCount}/{result.totalItems} câu đúng · {result.score}%
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {result.correctCount < result.totalItems && (
                <button className="rounded-xl bg-amber-600 px-4 py-2 font-bold text-white hover:bg-amber-700" onClick={retryIncorrect} type="button">
                  {labels.SUA_LAI}
                </button>
              )}
              <button className="rounded-xl bg-white px-4 py-2 font-bold text-slate-700 shadow-sm hover:bg-slate-50" onClick={replay} type="button">
                {labels.LAM_LAI}
              </button>
              {result.completed && (
                <Link className="rounded-xl bg-teal-600 px-4 py-2 font-bold text-white hover:bg-teal-700" href={`/writing/${exercise.level}`}>
                  {labels.VE_DANH_SACH}
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
