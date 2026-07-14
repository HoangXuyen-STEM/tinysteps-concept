import "server-only";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

// A NEW client per request, reading this request's cookies. Never a module-level
// singleton: in serverless a shared client would leak one user's auth into another's request.
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // Called from a Server Component, which cannot write cookies.
            // Safe to ignore: middleware refreshes the session on every request.
          }
        },
      },
    },
  );
}
