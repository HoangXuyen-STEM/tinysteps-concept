import "server-only";
import { createClient } from "@/utils/supabase/server";

/**
 * The allow-list of admin/owner emails, parsed from the server-only ADMIN_EMAILS env var
 * (comma-separated). Normalised to trimmed lowercase so a casing or whitespace slip in the
 * env value does not silently lock the owner out. Never NEXT_PUBLIC_ — the identity of the
 * people who can grant paid access is not something the browser needs.
 */
export function getAdminEmails(): string[] {
  const raw = process.env.ADMIN_EMAILS;
  if (!raw) return [];
  return raw
    .split(",")
    .map((email) => email.trim().toLowerCase())
    .filter(Boolean);
}

/** True when at least one admin email is configured. Without it, nobody is an admin. */
export const isAdminAllowListConfigured = () => getAdminEmails().length > 0;

export type AdminIdentity = { userId: string; email: string };

/**
 * The signed-in admin, or null when the caller is signed out, has no email, or their email
 * is not on the allow-list. Authorization is derived from the verified session (getClaims
 * validates the JWT locally) and the server-only allow-list — never from anything the client
 * can set. Returns null rather than throwing so callers can uniformly map "not an admin" to a
 * 404, revealing nothing about whether the admin surface exists.
 *
 * Note this does not require the service-role key: identity can be established from the allow
 * list alone, so a configured admin still gets a helpful config error when only the service
 * key is missing, while non-admins get 404 either way.
 */
export async function getAdminIdentity(): Promise<AdminIdentity | null> {
  const admins = getAdminEmails();
  if (admins.length === 0) return null;

  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const userId = data?.claims?.sub;
  const email = typeof data?.claims?.email === "string" ? data.claims.email.toLowerCase() : undefined;

  if (!userId || !email) return null;
  if (!admins.includes(email)) return null;

  return { userId, email };
}

/** True when the current caller is an authorized admin. */
export const isAdmin = async () => (await getAdminIdentity()) !== null;
