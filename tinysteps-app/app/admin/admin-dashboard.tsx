"use client";

import { useActionState, useEffect, useState } from "react";
import {
  searchUserAction,
  activateAccessAction,
  revokeAccessAction,
  createUserAndActivateAction,
  type AdminActionState,
} from "./admin-actions";
import type { LearnerAccessState, LearnerProgressSummary } from "@/lib/admin/paid-access-admin";


const empty: AdminActionState = {};

function AccessBadge({ access }: { access: LearnerAccessState }) {
  if (!access.found) {
    return <p className="text-sm text-red-600">Không tìm thấy học viên với email này.</p>;
  }
  const row = access.access;
  const active = row && !row.revoked_at;
  return (
    <div className="mt-2 space-y-1 text-sm text-slate-700">
      <p>
        <span className="text-slate-500">Học viên:</span> {access.email}
      </p>
      <p>
        <span className="text-slate-500">Trạng thái:</span>{" "}
        {active ? (
          <span className="font-semibold text-teal-700">Đang có quyền truy cập</span>
        ) : row ? (
          <span className="font-semibold text-amber-700">Đã thu hồi</span>
        ) : (
          <span className="font-semibold text-slate-500">Chưa kích hoạt</span>
        )}
      </p>
      {row ? (
        <p className="text-xs text-slate-500">
          Cấp: {new Date(row.granted_at).toLocaleString("vi-VN")}
          {row.amount_vnd ? ` · ${row.amount_vnd.toLocaleString("vi-VN")}đ` : ""}
          {row.transfer_ref ? ` · ${row.transfer_ref}` : ""}
          {row.revoked_at ? ` · thu hồi ${new Date(row.revoked_at).toLocaleString("vi-VN")}` : ""}
        </p>
      ) : null}
    </div>
  );
}

const input = "w-full rounded-lg border border-slate-300 px-3 py-2 text-base";
const label = "text-sm font-medium text-slate-700";

export function AdminDashboard({
  adminEmail,
  progressList = [],
}: {
  adminEmail: string;
  progressList?: LearnerProgressSummary[];
}) {
  const [searchState, searchAction, searching] = useActionState(searchUserAction, empty);
  const [activateState, activateAction, activating] = useActionState(activateAccessAction, empty);
  const [revokeState, revokeAction, revoking] = useActionState(revokeAccessAction, empty);
  const [createState, createAction, creating] = useActionState(createUserAndActivateAction, empty);

  // The learner shown is whichever action most recently resolved with a result. Only one form
  // runs per interaction, so syncing each action's payload into local state keeps the panel in
  // step with the latest mutation without threading state through separate hooks.
  const [learner, setLearner] = useState<LearnerAccessState | null>(null);
  const [email, setEmail] = useState<string>("");

  useEffect(() => {
    for (const state of [searchState, activateState, revokeState, createState]) {
      if (state.email) setEmail(state.email);
      if (state.learner) setLearner(state.learner);
    }
  }, [searchState, activateState, revokeState, createState]);

  const userId = learner?.found ? learner.userId : "";
  const messages = [searchState, activateState, revokeState, createState];
  const error = messages.map((s) => s.error).find(Boolean);
  const message = messages.map((s) => s.message).find(Boolean);

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Bảng quản trị</h1>
        <p className="mt-1 text-sm text-slate-500">Đăng nhập: {adminEmail}</p>
      </header>

      <section className="mb-8 rounded-xl border border-teal-200 bg-teal-50/40 p-4">
        <h2 className="font-semibold text-slate-900">Tạo tài khoản + kích hoạt VIP</h2>
        <p className="mt-1 text-sm text-slate-600">
          Tạo email/mật khẩu mới và mở toàn bộ nội dung trong một bước. Dùng cho pilot hoặc khi
          người học chưa tự đăng ký.
        </p>
        <form
          action={createAction}
          onSubmit={(e) => {
            const form = e.currentTarget;
            const newEmail = (form.elements.namedItem("email") as HTMLInputElement)?.value;
            if (!confirm(`Tạo tài khoản và kích hoạt VIP cho ${newEmail}?`)) e.preventDefault();
          }}
          className="mt-4 grid gap-3 sm:grid-cols-2"
        >
          <div className="space-y-1 sm:col-span-2">
            <label className={label} htmlFor="create-email">
              Email học viên
            </label>
            <input id="create-email" name="email" type="email" required className={input} />
          </div>
          <div className="space-y-1">
            <label className={label} htmlFor="create-password">
              Mật khẩu tạm (tối thiểu 8 ký tự)
            </label>
            <input
              id="create-password"
              name="password"
              type="text"
              required
              minLength={8}
              className={input}
              autoComplete="off"
            />
          </div>
          <div className="space-y-1">
            <label className={label} htmlFor="create-amount">
              Số tiền (VND)
            </label>
            <input
              id="create-amount"
              name="amountVnd"
              type="number"
              min="1"
              required
              defaultValue={199000}
              className={input}
            />
          </div>
          <div className="space-y-1">
            <label className={label} htmlFor="create-ref">
              Mã giao dịch / tham chiếu
            </label>
            <input
              id="create-ref"
              name="transferRef"
              type="text"
              required
              defaultValue="PILOT"
              className={input}
            />
          </div>
          <div className="space-y-1">
            <label className={label} htmlFor="create-note">
              Ghi chú
            </label>
            <input id="create-note" name="note" type="text" defaultValue="pilot" className={input} />
          </div>
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={creating}
              className="w-full rounded-lg bg-teal-700 py-2 font-semibold text-white disabled:opacity-60"
            >
              {creating ? "Đang tạo…" : "Tạo tài khoản + kích hoạt VIP"}
            </button>
          </div>
        </form>
      </section>

      <h2 className="mb-2 font-semibold text-slate-900">Tìm & quản lý học viên có sẵn</h2>
      <form action={searchAction} className="flex gap-2">
        <input
          name="email"
          type="email"
          required
          placeholder="Email học viên"
          className={input}
          defaultValue={email}
        />
        <button
          type="submit"
          disabled={searching}
          className="whitespace-nowrap rounded-lg bg-teal-700 px-4 py-2 font-semibold text-white disabled:opacity-60"
        >
          {searching ? "Đang tìm…" : "Tìm"}
        </button>
      </form>

      {error ? (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
      ) : null}
      {message ? (
        <p className="mt-4 rounded-lg bg-teal-50 px-3 py-2 text-sm text-teal-700">{message}</p>
      ) : null}

      {learner ? (
        <section className="mt-6 rounded-xl border border-slate-200 p-4">
          <AccessBadge access={learner} />

          {learner.found ? (
            <div className="mt-6 grid gap-8 sm:grid-cols-2">
              <form
                action={activateAction}
                onSubmit={(e) => {
                  if (!confirm(`Kích hoạt quyền truy cập cho ${email}?`)) e.preventDefault();
                }}
                className="space-y-3"
              >
                <p className="font-semibold text-slate-800">Kích hoạt</p>
                <input type="hidden" name="userId" value={userId} />
                <input type="hidden" name="email" value={email} />
                <div className="space-y-1">
                  <label className={label} htmlFor="amountVnd">
                    Số tiền (VND)
                  </label>
                  <input id="amountVnd" name="amountVnd" type="number" min="1" required className={input} />
                </div>
                <div className="space-y-1">
                  <label className={label} htmlFor="transferRef">
                    Mã giao dịch
                  </label>
                  <input id="transferRef" name="transferRef" type="text" required className={input} />
                </div>
                <div className="space-y-1">
                  <label className={label} htmlFor="note">
                    Ghi chú
                  </label>
                  <input id="note" name="note" type="text" className={input} />
                </div>
                <button
                  type="submit"
                  disabled={activating}
                  className="w-full rounded-lg bg-teal-700 py-2 font-semibold text-white disabled:opacity-60"
                >
                  {activating ? "Đang lưu…" : "Kích hoạt"}
                </button>
              </form>

              <form
                action={revokeAction}
                onSubmit={(e) => {
                  if (!confirm(`Thu hồi quyền truy cập của ${email}?`)) e.preventDefault();
                }}
                className="space-y-3"
              >
                <p className="font-semibold text-slate-800">Thu hồi</p>
                <input type="hidden" name="userId" value={userId} />
                <input type="hidden" name="email" value={email} />
                <div className="space-y-1">
                  <label className={label} htmlFor="reason">
                    Lý do
                  </label>
                  <input id="reason" name="reason" type="text" required className={input} />
                </div>
                <button
                  type="submit"
                  disabled={revoking}
                  className="w-full rounded-lg border border-red-600 py-2 font-semibold text-red-600 disabled:opacity-60"
                >
                  {revoking ? "Đang thu hồi…" : "Thu hồi"}
                </button>
              </form>
            </div>
          ) : null}
        </section>
      ) : null}

      <section className="mt-10 rounded-xl border border-slate-200 p-4">
        <h2 className="font-semibold text-slate-900">Tiến trình học tập học viên</h2>
        <p className="mt-1 text-xs text-slate-500">
          Thống kê thời gian thực từ hệ thống
          {progressList.length > 0 ? ` (${progressList.length} học viên).` : "."}
        </p>

        {progressList.length === 0 ? (
          <p className="mt-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Chưa có dữ liệu học viên để hiển thị. Kiểm tra đã chạy migration{" "}
            <code className="rounded bg-amber-100 px-1">000009</code> trên Supabase chưa, rồi
            tải lại trang.
          </p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600">
                <tr>
                  <th className="py-2 px-2">Học viên</th>
                  <th className="py-2 px-2">Quyền VIP</th>
                  <th className="py-2 px-2">Đăng nhập mới nhất</th>
                  <th className="py-2 px-2 text-center">Đã hoàn thành</th>
                  <th className="py-2 px-2 text-center">Đang học</th>
                  <th className="py-2 px-2 text-center">Ngày học</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {progressList.map((item) => (
                  <tr key={item.userId} className="hover:bg-slate-50/60">
                    <td className="py-2 px-2 font-medium text-slate-900">{item.email}</td>
                    <td className="py-2 px-2">
                      {item.isPaid ? (
                        <span className="rounded bg-teal-100 px-2 py-0.5 text-xs font-semibold text-teal-800">
                          VIP
                        </span>
                      ) : (
                        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                          Miễn phí
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-2 text-xs text-slate-500">
                      {item.lastSignInAt
                        ? new Date(item.lastSignInAt).toLocaleString("vi-VN")
                        : "Chưa vào"}
                    </td>
                    <td className="py-2 px-2 text-center font-semibold text-teal-700">
                      {item.lessonsCompleted} bài
                    </td>
                    <td className="py-2 px-2 text-center text-slate-600">
                      {item.lessonsInProgress} bài
                    </td>
                    <td className="py-2 px-2 text-center text-slate-600">
                      {item.daysActive} ngày
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
