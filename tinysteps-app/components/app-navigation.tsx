import Link from "next/link";

const links = [
  ["Lessons", "/lessons"],
  ["Review", "/review"],
  ["Progress", "/dashboard"],
] as const;

export function AppNavigation() {
  return (
    <nav aria-label="Main navigation" className="fixed inset-x-0 bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-3xl justify-around px-4 py-3 text-sm font-semibold text-slate-600">
        {links.map(([label, href]) => <Link href={href} key={href}>{label}</Link>)}
      </div>
    </nav>
  );
}