import { createBrowserClient } from "@supabase/ssr";

// One browser client per tab is safe: it is scoped to the signed-in user's cookies.
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
