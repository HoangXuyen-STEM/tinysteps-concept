import "server-only";
import { createClient } from "@/utils/supabase/server";
import { createAdminClient, AdminConfigError } from "@/utils/supabase/admin";
import type {
  ActivateAccessInput,
  CreateUserAndActivateInput,
  RevokeAccessInput,
} from "./paid-access-admin-schemas";

export type PaidAccessRow = {
  user_id: string;
  granted_at: string;
  amount_vnd: number | null;
  transfer_ref: string | null;
  note: string | null;
  revoked_at: string | null;
};

export type LearnerAccessState =
  | { found: false }
  | { found: true; userId: string; email: string; access: PaidAccessRow | null };

// One row shape returned by admin_search_learner: the learner joined to their paid_access
// row (columns null + access_exists false when no grant was ever written).
type SearchRow = PaidAccessRow & { email: string; access_exists: boolean };

/**
 * All calls run through the ordinary anon-key server client, in the signed-in admin's
 * session, so auth.uid() inside each SECURITY DEFINER function resolves to them and the
 * function's own admin-table check is the real authorization boundary. No service-role key
 * is involved anywhere in this path.
 */

/**
 * The learner matching an email plus their current access row. The RPC returns only the
 * single matched learner — never the wider user list — so the admin UI cannot become a
 * directory of everyone's accounts. Returns found:false when no user matches.
 */
export async function getLearnerAccessState(email: string): Promise<LearnerAccessState> {
  const supabase = await createClient();
  const { data, error } = await supabase.rpc("admin_search_learner", { p_email: email });
  if (error) throw error;

  const rows = (data ?? []) as SearchRow[];
  const row = rows[0];
  if (!row) return { found: false };

  const access: PaidAccessRow | null = row.access_exists
    ? {
        user_id: row.user_id,
        granted_at: row.granted_at,
        amount_vnd: row.amount_vnd,
        transfer_ref: row.transfer_ref,
        note: row.note,
        revoked_at: row.revoked_at,
      }
    : null;

  return { found: true, userId: row.user_id, email: row.email, access };
}

/**
 * Grant (or re-grant) paid access. The RPC upserts on the user_id primary key, so
 * re-activating a previously revoked learner UPDATES their existing row — clearing
 * revoked_at and refreshing granted_at — rather than inserting a duplicate. Returns the
 * resulting row for the UI to display.
 */
export async function activatePaidAccess(input: ActivateAccessInput): Promise<PaidAccessRow> {
  const supabase = await createClient();
  const { data, error } = await supabase.rpc("admin_activate_paid_access", {
    p_user_id: input.userId,
    p_amount_vnd: input.amountVnd,
    p_transfer_ref: input.transferRef,
    p_note: input.note || null,
  });
  if (error) throw error;
  return data as PaidAccessRow;
}

/**
 * Revoke an existing grant (refund). The RPC sets revoked_at and appends the reason into
 * note; it fails gracefully with not_found/already_revoked so the UI can explain instead of
 * silently no-op.
 */
export async function revokePaidAccess(
  input: RevokeAccessInput,
): Promise<
  | { ok: true; access: PaidAccessRow }
  | { ok: false; reason: "not_found" | "already_revoked" }
> {
  const supabase = await createClient();
  const { data, error } = await supabase.rpc("admin_revoke_paid_access", {
    p_user_id: input.userId,
    p_reason: input.reason,
  });
  if (error) throw error;

  return data as
    | { ok: true; access: PaidAccessRow }
    | { ok: false; reason: "not_found" | "already_revoked" };
}

export type CreateUserResult =
  | { ok: true; userId: string; email: string; access: PaidAccessRow }
  | { ok: false; reason: "email_exists" | "service_not_configured" | "create_failed"; detail?: string };

/**
 * Create a new Auth user (email already confirmed) with a temporary password, then grant
 * paid access via the existing SECURITY DEFINER RPC. Uses the service-role client only for
 * auth.admin.createUser — grant still runs as the signed-in admin through the RPC so the
 * admin_users boundary stays intact.
 */
export async function createUserAndActivate(
  input: CreateUserAndActivateInput,
): Promise<CreateUserResult> {
  let admin;
  try {
    admin = createAdminClient();
  } catch (error) {
    if (error instanceof AdminConfigError) {
      return { ok: false, reason: "service_not_configured", detail: error.message };
    }
    throw error;
  }

  const { data: created, error: createError } = await admin.auth.admin.createUser({
    email: input.email,
    password: input.password,
    email_confirm: true,
  });

  if (createError) {
    const msg = createError.message?.toLowerCase() ?? "";
    if (msg.includes("already") || msg.includes("registered") || msg.includes("exists")) {
      return { ok: false, reason: "email_exists", detail: createError.message };
    }
    return { ok: false, reason: "create_failed", detail: createError.message };
  }

  const userId = created.user?.id;
  if (!userId) {
    return { ok: false, reason: "create_failed", detail: "No user id returned." };
  }

  const access = await activatePaidAccess({
    userId,
    amountVnd: input.amountVnd,
    transferRef: input.transferRef,
    note: input.note,
  });

  return { ok: true, userId, email: input.email, access };
}

export type LearnerProgressSummary = {
  userId: string;
  email: string;
  lastSignInAt: string | null;
  createdAt: string;
  isPaid: boolean;
  lessonsCompleted: number;
  lessonsInProgress: number;
  daysActive: number;
};

/**
 * Fetch the progress overview for all learners via SECURITY DEFINER RPC.
 * Only authenticated admin sessions receive rows — non-admins trigger a 403.
 */
export async function getLearnerProgressOverview(): Promise<LearnerProgressSummary[]> {
  const supabase = await createClient();
  const { data, error } = await supabase.rpc("admin_list_learner_progress");
  if (error) throw error;

  return ((data ?? []) as any[]).map((row) => ({
    userId: row.user_id,
    email: row.email,
    lastSignInAt: row.last_sign_in_at,
    createdAt: row.created_at,
    isPaid: Boolean(row.is_paid),
    lessonsCompleted: Number(row.lessons_completed ?? 0),
    lessonsInProgress: Number(row.lessons_in_progress ?? 0),
    daysActive: Number(row.days_active ?? 0),
  }));
}

