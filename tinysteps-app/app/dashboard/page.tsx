import { createClient } from "@/utils/supabase/server";

export default async function DashboardPage() {
  // Middleware already guards this route; read the user for a personalised greeting.
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const email = data?.claims?.email as string | undefined;

  return (
    <main>
      <h1 className="text-2xl font-bold">Xin chào{email ? `, ${email}` : ""}</h1>
      <p className="mt-2 text-slate-600">Bảng tiến độ đầy đủ sẽ có ở Phase 06.</p>
      <form action="/auth/signout" method="post" className="mt-6">
        <button
          type="submit"
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
        >
          Đăng xuất
        </button>
      </form>
    </main>
  );
}
