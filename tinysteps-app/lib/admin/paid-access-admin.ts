import "server-only";
import { createAdminClient } from "@/utils/supabase/admin";
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

// The pilot is capped at ~100 learners, so a bounded scan of the auth user list is simpler
// and adequate for an exact-email lookup (the admin API has no server-side email filter).
// The cap stops an unexpectedly large user table from turning this into an unbounded loop.
const MAX_USER_PAGES = 20;
const USERS_PER_PAGE = 100;

/** The auth user whose email matches exactly (case-insensitive), or null if none. */
async function findUserByEmail(email: string): Promise<{ userId: string; email: string } | null> {
  const admin = createAdminClient();
  const target = email.toLowerCase();

  for (let page = 1; page <= MAX_USER_PAGES; page++) {
    const { data, error } = await admin.auth.admin.listUsers({ page, perPage: USERS_PER_PAGE });
    if (error) throw error;

    const match = data.users.find((user) => user.email?.toLowerCase() === target);
    if (match?.email) return { userId: match.id, email: match.email };

    if (data.users.length < USERS_PER_PAGE) break; // last page reached
  }
  return null;
}

/** Current paid-access row for a user, or null when no grant has ever been written. */
async function getPaidAccessRow(userId: string): Promise<PaidAccessRow | null> {
  const admin = createAdminClient();
  const { data, error } = await admin
    .from("paid_access")
    .select("user_id, granted_at, amount_vnd, transfer_ref, note, revoked_at")
    .eq("user_id", userId)
    .maybeSingle();

  if (error) throw error;
  return data as PaidAccessRow | null;
}

/**
 * The learner matching an email plus their current access row. Returns only the single
 * matched learner's data — never the wider user list — so the admin UI cannot become a
 * directory of everyone's accounts.
 */
export async function getLearnerAccessState(email: string): Promise<LearnerAccessState> {
  const user = await findUserByEmail(email);
  if (!user) return { found: false };
  const access = await getPaidAccessRow(user.userId);
  return { found: true, userId: user.userId, email: user.email, access };
}

/**
 * Grant (or re-grant) paid access. Upserts on the user_id primary key, so re-activating a
 * previously revoked learner UPDATES their existing row — clearing revoked_at and refreshing
 * granted_at — rather than inserting a duplicate the primary key would reject anyway. Returns
 * the resulting row for the UI to display.
 */
export async function activatePaidAccess(input: ActivateAccessInput): Promise<PaidAccessRow> {
  const admin = createAdminClient();
  const { data, error } = await admin
    .from("paid_access")
    .upsert(
      {
        user_id: input.userId,
        granted_at: new Date().toISOString(),
        amount_vnd: input.amountVnd,
        transfer_ref: input.transferRef,
        note: input.note || null,
        revoked_at: null,
      },
      { onConflict: "user_id" },
    )
    .select("user_id, granted_at, amount_vnd, transfer_ref, note, revoked_at")
    .single();

  if (error) throw error;
  return data as PaidAccessRow;
}

/**
 * Revoke an existing grant (refund). Sets revoked_at and records the reason in the note.
 * Updates only a row that exists and is not already revoked; if there is nothing active to
 * revoke it returns notFound/alreadyRevoked so the UI can explain instead of silently no-op.
 */
export async function revokePaidAccess(
  input: RevokeAccessInput,
): Promise<
  | { ok: true; access: PaidAccessRow }
  | { ok: false; reason: "not_found" | "already_revoked" }
> {
  const existing = await getPaidAccessRow(input.userId);
  if (!existing) return { ok: false, reason: "not_found" };
  if (existing.revoked_at) return { ok: false, reason: "already_revoked" };

  const admin = createAdminClient();
  const note = existing.note
    ? `${existing.note} | revoked: ${input.reason}`
    : `revoked: ${input.reason}`;

  const { data, error } = await admin
    .from("paid_access")
    .update({ revoked_at: new Date().toISOString(), note })
    .eq("user_id", input.userId)
    .select("user_id, granted_at, amount_vnd, transfer_ref, note, revoked_at")
    .single();

  if (error) throw error;
  return { ok: true, access: data as PaidAccessRow };
}
