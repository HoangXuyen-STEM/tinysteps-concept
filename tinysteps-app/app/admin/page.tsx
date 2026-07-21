import { notFound } from "next/navigation";
import { getAdminIdentity } from "@/lib/admin/admin-auth";
import { AdminDashboard } from "./admin-dashboard";

// Never cache: this surface reads and mutates live access state.
export const dynamic = "force-dynamic";

/**
 * Internal admin dashboard for granting/revoking paid access. Guarded two ways:
 * unauthenticated requests are redirected to /login by middleware, and here we require the
 * signed-in email to be on the server-only allow-list — a UI-level convenience gate. Anyone
 * who is not an admin — signed out, a learner, or a signed-in non-admin — gets a plain 404
 * that reveals nothing about the page existing. The real authorization boundary for every
 * grant/revoke is the SECURITY DEFINER RPC's own admin-table check in the database, so no
 * service-role key is needed on this host.
 */
export default async function AdminPage() {
  const identity = await getAdminIdentity();
  if (!identity) notFound();

  return <AdminDashboard adminEmail={identity.email} />;
}
