"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";

export type AuthState = { error?: string; message?: string };

async function siteOrigin() {
  // Prefer an explicit site URL in prod; fall back to the request origin in dev.
  const configured = process.env.NEXT_PUBLIC_SITE_URL;
  if (configured) return configured;
  const host = (await headers()).get("origin");
  return host ?? "";
}

export async function signInWithPassword(
  _prev: AuthState,
  formData: FormData,
): Promise<AuthState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  if (!email || !password) return { error: "Vui lòng nhập email và mật khẩu." };

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) return { error: "Email hoặc mật khẩu không đúng." };

  redirect("/dashboard");
}

export async function signInWithMagicLink(
  _prev: AuthState,
  formData: FormData,
): Promise<AuthState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) return { error: "Vui lòng nhập email." };

  const supabase = await createClient();
  // shouldCreateUser:false — pilot accounts are created manually in the dashboard;
  // an unknown email must never silently become a new account.
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      shouldCreateUser: false,
      emailRedirectTo: `${await siteOrigin()}/auth/confirm?next=/dashboard`,
    },
  });
  if (error) return { error: "Không gửi được liên kết. Kiểm tra lại email." };

  // Same message whether or not the email exists, so the form never reveals which
  // addresses have accounts.
  return { message: "Nếu email hợp lệ, liên kết đăng nhập đã được gửi. Kiểm tra hộp thư." };
}
