import "server-only";
import { createClient as createSupabaseClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Thrown when the server-only configuration the admin surface depends on is missing.
 * Callers translate this into a safe "misconfigured" state for admins and a plain 404
 * for everyone else — the message here must never leak a secret value, only the name
 * of the variable that is absent.
 */
export class AdminConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AdminConfigError";
  }
}

/**
 * A service-role Supabase client that bypasses RLS. Server-only: the key must never be
 * bundled for the browser, so this module imports "server-only" and reads a non-public
 * env var. A new client is created per call rather than a module singleton, matching the
 * per-request discipline of the anon server client, and auth persistence is disabled
 * because there is no user session to store — this client acts as the backend itself.
 *
 * Fails closed: if the URL or service-role key is absent it throws AdminConfigError
 * instead of constructing a half-configured client that would surface confusing runtime
 * errors deeper in a mutation.
 */
export function createAdminClient(): SupabaseClient {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url) throw new AdminConfigError("NEXT_PUBLIC_SUPABASE_URL is not set");
  if (!serviceRoleKey) throw new AdminConfigError("SUPABASE_SERVICE_ROLE_KEY is not set");

  return createSupabaseClient(url, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

/** True when the service-role key needed for admin mutations is present. */
export const isAdminServiceConfigured = () =>
  Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY);
