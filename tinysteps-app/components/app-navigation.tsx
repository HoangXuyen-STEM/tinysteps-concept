import Link from "next/link";
import { labels } from "@/lib/i18n/labels";

const links = [
  { label: labels.TRANG_CHU, href: "/dashboard", icon: "🏠" },
  { label: labels.BAI_HOC, href: "/lessons", icon: "📖" },
  { label: labels.WRITING, href: "/writing", icon: "✍️" },
  { label: labels.LISTENING, href: "/listening", icon: "🎧" },
  { label: labels.ON_TAP, href: "/review", icon: "🔁" },
] as const;

// Google Form URL for pilot feedback (decision 6, plan.md). Link is hidden until the
// user sets this, so an unconfigured pilot doesn't ship a dead "Góp ý" button.
const FEEDBACK_FORM_URL = process.env.NEXT_PUBLIC_FEEDBACK_FORM_URL;

export function AppNavigation() {
  return (
    <nav
      aria-label="Điều hướng chính"
      className="fixed inset-x-0 bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur"
    >
      <div className="mx-auto flex max-w-3xl items-stretch justify-around px-2">
        {links.map(({ label, href, icon }) => (
          <Link
            href={href}
            key={href}
            className="flex min-h-11 flex-1 flex-col items-center justify-center gap-0.5 py-2 text-xs font-semibold text-slate-600"
          >
            <span aria-hidden="true" className="text-lg leading-none">
              {icon}
            </span>
            {label}
          </Link>
        ))}
        {FEEDBACK_FORM_URL && (
          <a
            href={FEEDBACK_FORM_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex min-h-11 flex-1 flex-col items-center justify-center gap-0.5 py-2 text-xs font-semibold text-slate-600"
          >
            <span aria-hidden="true" className="text-lg leading-none">
              💬
            </span>
            {labels.GOP_Y}
          </a>
        )}
      </div>
    </nav>
  );
}
