import Link from "next/link";
import { getLevels, getVocab } from "@/lib/content/vocabulary-loader";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";

export default function LessonsPage() {
  return <main><h1 className="text-2xl font-bold">Lessons</h1><p className="mt-2 text-slate-600">Choose a level and practise useful English in context.</p>
    <div className="mt-5 space-y-3">{getLevels().map((level) => <Link className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm" href={`/lessons/${level}`} key={level}><strong className="capitalize">{level}</strong><span className="ml-2 text-sm text-slate-500">{getLessonsByLevel(level).length} lessons · {getVocab(level).length} words</span></Link>)}</div>
  </main>;
}