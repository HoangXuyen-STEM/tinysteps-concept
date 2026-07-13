import type { Metadata } from "next";
import { AppNavigation } from "@/components/app-navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "TinySteps",
  description: "English practice in small, practical steps.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>
        <div className="mx-auto min-h-screen max-w-3xl px-4 pb-24 pt-6 sm:px-6">
          <header className="mb-8">
            <p className="text-sm font-semibold tracking-wide text-teal-700">TinySteps</p>
            <p className="mt-1 text-sm text-slate-600">English for everyday teaching.</p>
          </header>
          {children}
        </div>
        <AppNavigation />
      </body>
    </html>
  );
}
