import { AppNavigation } from "@/components/app-navigation";
import { getCompletedCountByLevel } from "@/lib/progress/lesson-progress-queries";

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const completed = await getCompletedCountByLevel();
  const hasMoversProgress = completed.movers > 0;

  return (
    <>
      <div className="mx-auto min-h-screen max-w-3xl px-4 pb-24 pt-6 sm:px-6">
        <header className="mb-8">
          <p className="text-sm font-semibold tracking-wide text-teal-700">TinySteps</p>
          <p className="mt-1 text-sm text-slate-600">Tiếng Anh cho công việc dạy học hằng ngày.</p>
        </header>
        {children}
      </div>
      <AppNavigation hasMoversProgress={hasMoversProgress} />
    </>
  );
}
