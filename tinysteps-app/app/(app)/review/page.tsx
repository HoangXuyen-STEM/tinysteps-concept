import Link from "next/link";
import { getReviewQueue } from "@/lib/srs/srs-queue-queries";
import { ReviewSession } from "@/components/srs/review-session";
import { labels } from "@/lib/i18n/labels";

export default async function ReviewPage() {
  const { items, dueCount, newCount } = await getReviewQueue();

  if (items.length === 0) {
    return (
      <main>
        <h1 className="text-2xl font-bold text-slate-800">{labels.ON_TAP_TU_VUNG}</h1>
        <div className="mt-6 rounded-3xl border border-slate-100 bg-white p-8 text-center shadow-sm">
          <div className="mb-3 text-4xl">🌱</div>
          <p className="font-semibold text-slate-700">{labels.KHONG_CO_TU_ON}</p>
          <p className="mt-1 text-sm text-slate-500">{labels.QUAY_LAI_SAU}</p>
          <Link
            href="/lessons"
            className="mt-6 inline-block rounded-xl bg-teal-600 px-6 py-3 font-bold text-white transition-colors hover:bg-teal-700"
          >
            {labels.BAI_HOC}
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main>
      <ReviewSession items={items} dueCount={dueCount} newCount={newCount} />
    </main>
  );
}
