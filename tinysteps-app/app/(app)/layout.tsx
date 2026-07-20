import { AppNavigation } from "@/components/app-navigation";

// Chrome for the signed-in product: centered column, brand header, fixed bottom nav.
// pb-24 keeps the last card clear of the fixed nav.
export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <div className="mx-auto min-h-screen max-w-3xl px-4 pb-24 pt-6 sm:px-6">
        <header className="mb-8">
          <p className="text-sm font-semibold tracking-wide text-teal-700">TinySteps</p>
          <p className="mt-1 text-sm text-slate-600">Tiếng Anh cho công việc dạy học hằng ngày.</p>
        </header>
        {children}
      </div>
      <AppNavigation />
    </>
  );
}
