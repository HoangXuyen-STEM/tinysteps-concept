import Link from "next/link";
import { getLevels } from "@/lib/content/vocabulary-loader";

export default function Home() {
  const levels = getLevels();

  return (
    <main className="space-y-6">
      <section className="rounded-3xl bg-teal-700 p-6 text-white shadow-sm">
        <p className="text-sm font-medium text-teal-100">Learn one useful thing today</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight">Small English steps for real classrooms.</h1>
        <Link className="mt-5 inline-block rounded-full bg-white px-5 py-3 text-sm font-semibold text-teal-800" href="/lessons">
          Explore lessons
        </Link>
      </section>
      <section>
        <h2 className="text-lg font-bold">Your learning path</h2>
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {levels.map((level) => (
            <Link className="rounded-2xl border border-slate-200 bg-white p-4 font-semibold capitalize shadow-sm" href={`/lessons/${level}`} key={level}>
              {level}
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
