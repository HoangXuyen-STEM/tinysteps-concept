import Link from "next/link";
import { notFound } from "next/navigation";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import { levels, type Level } from "@/lib/types/content-types";

const isLevel = (value: string): value is Level => levels.includes(value as Level);

export default async function LevelLessonsPage({ params }: { params: Promise<{ level: string }> }) {
  const { level } = await params;
  if (!isLevel(level)) notFound();
  const lessons = getLessonsByLevel(level);
  return <main><h1 className="text-2xl font-bold capitalize">{level} lessons</h1><div className="mt-5 space-y-3">{lessons.map((lesson) => <Link className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm" href={`/lessons/${level}/${lesson.id}`} key={lesson.id}><p className="font-semibold">{lesson.order}. {lesson.title}</p><p className="mt-1 text-sm text-slate-600">{lesson.scenario}</p></Link>)}</div></main>;
}