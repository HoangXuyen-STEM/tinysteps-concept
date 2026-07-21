import "server-only";
import { createClient } from "@/utils/supabase/server";
import type { ActivateAccessInput, RevokeAccessInput } from "./paid-access-admin-schemas";

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
