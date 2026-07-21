import Link from "next/link";
import { createClient } from "@/utils/supabase/server";

// Public pages (landing, purchase). No bottom nav: a signed-out visitor cannot reach
// the product screens it links to, and a sales page reads better full-bleed.
export default async function MarketingLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // A signed-in visitor still lands here (the landing and /mua are shared by both
  // states), so the header CTA must follow the session: "Đăng nhập" is wrong once
  // they are already in.
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const isSignedIn = Boolean(data?.claims?.sub);

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-slate-100">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4 sm:px-6">
          <Link className="text-sm font-semibold tracking-wide text-teal-700" href="/">
            TinySteps
          </Link>
          <Link
            className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
            href={isSignedIn ? "/dashboard" : "/login"}
          >
            {isSignedIn ? "Vào học" : "Đăng nhập"}
          </Link>
        </div>
      </header>
      {children}
      <footer className="mt-16 border-t border-slate-100 py-8">
        <div className="mx-auto max-w-3xl px-4 text-sm text-slate-500 sm:px-6">
          <p className="font-medium text-slate-700">TinySteps</p>
          <p className="mt-1">Đỗ Hoàng Xuyên · Giáo viên Hóa học</p>
          <p className="mt-3 text-xs leading-relaxed">
            TinySteps là dự án cá nhân, không trực thuộc và không liên kết với Bộ Giáo dục và Đào tạo
            hay bất kỳ tổ chức nào khác.
          </p>
        </div>
      </footer>
    </div>
  );
}
