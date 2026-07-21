import { notFound } from "next/navigation";
import { getAdminIdentity } from "@/lib/admin/admin-auth";
import { isAdminServiceConfigured } from "@/utils/supabase/admin";
import { AdminDashboard } from "./admin-dashboard";

// Never cache: this surface reads and mutates live access state.
export const dynamic = "force-dynamic";

/**
 * Internal admin dashboard for granting/revoking paid access. Guarded two ways:
 * unauthenticated requests are redirected to /login by middleware, and here we require the
 * signed-in email to be on the server-only allow-list. Anyone who is not an admin — signed
 * out, a learner, or a signed-in non-admin — gets a plain 404 that reveals nothing about the
 * page existing. A configured admin whose service-role key is missing sees a safe config
 * error (variable name only, never a value).
 */
export default async function AdminPage() {
  const identity = await getAdminIdentity();
  if (!identity) notFound();

  if (!isAdminServiceConfigured()) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-10">
        <h1 className="text-2xl font-bold text-slate-900">Bảng quản trị</h1>
        <div className="mt-6 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <p className="font-semibold">Chưa thể thao tác quyền truy cập.</p>
          <p className="mt-1">
            Biến môi trường máy chủ <code className="font-mono">SUPABASE_SERVICE_ROLE_KEY</code>{" "}
            chưa được cấu hình. Thêm biến này trên máy chủ (không phải biến{" "}
            <code className="font-mono">NEXT_PUBLIC_*</code>) rồi tải lại trang.
          </p>
        </div>
      </main>
    );
  }

  return <AdminDashboard adminEmail={identity.email} />;
}
