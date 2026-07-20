import Link from "next/link";
import { notFound } from "next/navigation";
import { getLessonsByLevel } from "@/lib/content/lesson-loader";
import { getTopics } from "@/lib/content/topics-loader";
import { getLevelProgress } from "@/lib/progress/lesson-progress-queries";
import { hasPaidAccess, isFreeLesson } from "@/lib/access/paid-access";
import { levels, type Level, type Lesson } from "@/lib/types/content-types";
import { labels } from "@/lib/i18n/labels";

const isLevel = (value: string): value is Level =>
  levels.includes(value as Level);

export default async function LevelLessonsPage({
  params,
}: {
  params: Promise<{ level: string }>;
}) {
  const { level } = await params;
  if (!isLevel(level)) notFound();

  const lessons = getLessonsByLevel(level);
  const topics = getTopics();
  const progressMap = await getLevelProgress(level);
  const isPaid = await hasPaidAccess();

  // Group lessons by topic
  const grouped = lessons.reduce<Record<string, Lesson[]>>((acc, lesson) => {
    if (!acc[lesson.topic_id]) acc[lesson.topic_id] = [];
    acc[lesson.topic_id].push(lesson);
    return acc;
  }, {});

  const topicMap = new Map(topics.map((t) => [t.id, t]));

  // Ensure consistent order based on the first lesson's order in each topic
  const sortedTopicIds = Object.keys(grouped).sort((a, b) => {
    const aFirst = grouped[a]?.[0]?.order ?? 0;
    const bFirst = grouped[b]?.[0]?.order ?? 0;
    return aFirst - bFirst;
  });

  return (
    <main className="space-y-8">
      <h1 className="text-2xl font-bold capitalize">
        {labels.BAI_HOC} · {level}
      </h1>

      {sortedTopicIds.map((topicId) => {
        const topic = topicMap.get(topicId);
        const groupLessons = grouped[topicId] || [];

        return (
          <section key={topicId}>
            <div className="mb-4">
              <h2 className="text-lg font-bold text-slate-800">
                {topic?.name || topicId}
              </h2>
              {topic?.description && (
                <p className="mt-1 text-sm text-slate-600">
                  {topic.description}
                </p>
              )}
            </div>

            <div className="space-y-3">
              {groupLessons.map((lesson) => {
                const progress = progressMap[lesson.id];
                const isCompleted = progress?.status === "completed";
                const isInProgress = progress?.status === "in_progress";
                const isLocked = !isPaid && !isFreeLesson(lesson.id);

                return (
                  <Link
                    className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:border-teal-300 hover:bg-slate-50"
                    href={`/lessons/${level}/${lesson.id}`}
                    key={lesson.id}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-slate-900">
                          {lesson.order}. {lesson.title}
                        </p>
                        <p className="mt-1 text-sm text-slate-600">
                          {lesson.scenario}
                        </p>
                      </div>

                      {/* Status Badge */}
                      {isCompleted ? (
                        <span className="shrink-0 rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-800">
                          {progress.score}%
                        </span>
                      ) : isInProgress ? (
                        <span className="shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">
                          {labels.DANG_HOC}
                        </span>
                      ) : isLocked ? (
                        <span
                          className="shrink-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500"
                          title={labels.CAN_GOI_TRON_BO}
                        >
                          🔒
                        </span>
                      ) : null}
                    </div>
                  </Link>
                );
              })}
            </div>
          </section>
        );
      })}
    </main>
  );
}