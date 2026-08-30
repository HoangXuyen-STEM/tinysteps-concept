import Link from "next/link";
import { labels } from "@/lib/i18n/labels";

const links = [
  { label: labels.TRANG_CHU, href: "/dashboard", icon: "🏠", gated: false },
  { label: labels.BAI_HOC, href: "/lessons", icon: "📖", gated: false },
  { label: labels.WRITING, href: "/writing", icon: "✍️", gated: true },
  { label: labels.LISTENING, href: "/listening", icon: "🎧", gated: true },
  { label: labels.ON_TAP, href: "/review", icon: "🔁", gated: false },
] as const;

const FEEDBACK_FORM_URL = process.env.NEXT_PUBLIC_FEEDBACK_FORM_URL;

type Props = {
  hasMoversProgress?: boolean;
};

export function AppNavigation({ hasMoversProgress = false }: Props) {
  return (
    <nav
      aria-label="Điều hướng chính"
      className="fixed inset-x-0 bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur"
    >
      <div className="mx-auto flex max-w-3xl items-stretch justify-around px-2">
        {links.map(({ label, href, icon, gated }) => {
          const locked = gated && !hasMoversProgress;
          const className =
            "flex min-h-11 flex-1 flex-col items-center justify-center gap-0.5 py-2 text-xs font-semibold text-slate-600";
          if (locked) {
            return (
              <span
                key={href}
                className={`${className} pointer-events-none opacity-50`}
                aria-disabled="true"
              >
                <span aria-hidden="true" className="text-lg leading-none">
                  {labels.SAP_RA_MAT}
                </span>
                {label}
              </span>
            );
          }
          return (
            <Link href={href} key={href} className={className}>
              <span aria-hidden="true" className="text-lg leading-none">
                {icon}
              </span>
              {label}
            </Link>
          );
        })}
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
