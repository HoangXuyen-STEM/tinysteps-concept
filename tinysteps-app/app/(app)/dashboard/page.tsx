import {
  getDueTodayCount,
  getLevelProgressSummary,
  getNextLesson,
  getProfile,
  getStreak,
} from "@/lib/progress/dashboard-queries";
import { DashboardView } from "@/components/dashboard/dashboard-view";

export default async function DashboardPage() {
  // Middleware already guards this route.
  const profile = await getProfile();

  const [levelProgress, streak, dueToday, nextLesson] = await Promise.all([
    getLevelProgressSummary(),
    getStreak(),
    getDueTodayCount(),
    getNextLesson(profile.currentLevel),
  ]);

  return (
    <main>
      <DashboardView
        displayName={profile.displayName}
        levelProgress={levelProgress}
        streak={streak}
        dueToday={dueToday}
        nextLesson={nextLesson}
      />
    </main>
  );
}
