import { notFound } from "next/navigation";
import { getLesson } from "@/lib/content/lesson-loader";
import { levels, type Level } from "@/lib/types/content-types";

const isLevel = (value: string): value is Level => levels.includes(value as Level);

export default async function LessonPage({ params }: { params: Promise<{ level: string; id: string }> }) {
  const { level, id } = await params;
  const lesson = getLesson(id);
  if (!isLevel(level) || lesson?.level !== level) notFound();
  return <main><p className="text-sm font-semibold capitalize text-teal-700">{lesson.level} · {lesson.estimated_minutes} min</p><h1 className="mt-1 text-2xl font-bold">{lesson.title}</h1><p className="mt-3 text-slate-600">{lesson.scenario}</p><section className="mt-6 rounded-2xl bg-white p-5 shadow-sm"><h2 className="font-bold">{lesson.dialogue.setting}</h2><p className="mt-2 text-sm text-slate-600">Lesson player and exercises arrive in Phase 04.</p></section></main>;
}