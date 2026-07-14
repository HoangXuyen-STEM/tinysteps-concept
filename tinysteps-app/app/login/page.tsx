import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { LoginForm } from "./login-form";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  if (data?.claims?.sub) redirect("/dashboard");

  const { error } = await searchParams;

  return (
    <main>
      <h1 className="text-2xl font-bold">Đăng nhập</h1>
      <p className="mt-2 text-slate-600">Tiếp tục hành trình học tiếng Anh của bạn.</p>
      {error === "link" ? (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          Liên kết không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.
        </p>
      ) : null}
      <LoginForm />
    </main>
  );
}
