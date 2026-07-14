"use client";

import { useActionState } from "react";
import {
  signInWithMagicLink,
  signInWithPassword,
  type AuthState,
} from "@/app/actions/auth-actions";

const initialState: AuthState = {};

export function LoginForm() {
  const [passwordState, passwordAction, passwordPending] = useActionState(
    signInWithPassword,
    initialState,
  );
  const [linkState, linkAction, linkPending] = useActionState(
    signInWithMagicLink,
    initialState,
  );

  return (
    <div className="mt-6 space-y-8">
      <form action={passwordAction} className="space-y-4">
        <div className="space-y-1">
          <label htmlFor="email" className="text-sm font-medium text-slate-700">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-base"
          />
        </div>
        <div className="space-y-1">
          <label htmlFor="password" className="text-sm font-medium text-slate-700">
            Mật khẩu
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-base"
          />
        </div>
        <button
          type="submit"
          disabled={passwordPending}
          className="w-full rounded-lg bg-teal-700 py-2.5 font-semibold text-white disabled:opacity-60"
        >
          {passwordPending ? "Đang đăng nhập…" : "Đăng nhập"}
        </button>
        {passwordState.error ? (
          <p className="text-sm text-red-600">{passwordState.error}</p>
        ) : null}
      </form>

      <div className="flex items-center gap-3 text-xs text-slate-400">
        <span className="h-px flex-1 bg-slate-200" />
        HOẶC
        <span className="h-px flex-1 bg-slate-200" />
      </div>

      <form action={linkAction} className="space-y-3">
        <p className="text-sm text-slate-600">
          Nhận liên kết đăng nhập qua email (không cần mật khẩu).
        </p>
        <input
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder="Email"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-base"
        />
        <button
          type="submit"
          disabled={linkPending}
          className="w-full rounded-lg border border-teal-700 py-2.5 font-semibold text-teal-700 disabled:opacity-60"
        >
          {linkPending ? "Đang gửi…" : "Gửi liên kết đăng nhập"}
        </button>
        {linkState.error ? (
          <p className="text-sm text-red-600">{linkState.error}</p>
        ) : null}
        {linkState.message ? (
          <p className="text-sm text-teal-700">{linkState.message}</p>
        ) : null}
      </form>
    </div>
  );
}
