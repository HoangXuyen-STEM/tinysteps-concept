import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { LandingHero } from "@/components/marketing/landing-hero";
import { LandingPillars } from "@/components/marketing/landing-pillars";
import { LandingPricing } from "@/components/marketing/landing-pricing";
import { LandingFaq } from "@/components/marketing/landing-faq";

export const metadata: Metadata = {
  title: "TinySteps — Xây nền tiếng Anh cho giáo viên",
  description:
    "Từ vựng và ngữ pháp nền theo khung Cambridge, mỗi ngày 10 phút. Học thử 3 bài miễn phí.",
};

// "/" serves the sales page to visitors and sends signed-in learners straight to the
// product — one URL to share, no separate marketing host to keep in sync.
export default async function LandingPage() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  if (data?.claims?.sub) redirect("/dashboard");

  return (
    <main className="pb-8">
      <LandingHero />
      <LandingPillars />
      <LandingPricing />
      <LandingFaq />
    </main>
  );
}
