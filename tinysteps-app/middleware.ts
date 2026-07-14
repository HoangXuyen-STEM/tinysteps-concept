import { type NextRequest } from "next/server";
import { updateSession } from "@/utils/supabase/middleware";

export async function middleware(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  // Run on every request except static assets and media so the session stays fresh.
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:mp3|png|jpg|jpeg|svg|ico|webp)$).*)",
  ],
};
