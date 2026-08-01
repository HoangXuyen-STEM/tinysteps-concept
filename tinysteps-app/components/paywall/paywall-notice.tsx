import Link from "next/link";
import { offer, formatVnd, currentPriceVnd } from "@/lib/marketing/offer";
import { FREE_LESSON_IDS } from "@/lib/access/paid-access";

type Props = {
  lessonTitle: string;
  freeCount?: number;
  backHref?: string;
  backLabel?: string;
};

// Shown in place of a locked lesson. Names the lesson the learner tried to open so the
// block reads as "this one needs the full package" rather than a dead end.
export function PaywallNotice({
  lessonTitle,
  freeCount = FREE_LESSON_IDS.length,
  backHref = "/lessons",
  backLabel = "Quay lại danh sách bài học",
}: Props) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
      <p className="text-3xl" aria-hidden="true">
        🔒
      </p>
      <h1 className="mt-3 text-xl font-bold text-slate-900">{lessonTitle}</h1>
      <p className="mt-2 leading-relaxed text-slate-600">
        Bài này nằm trong gói học trọn bộ. Bạn đã học xong {freeCount} bài miễn phí —
        cảm ơn bạn đã dành thời gian cho TinySteps.
      </p>

      <div className="mt-5 rounded-xl bg-slate-50 p-4 text-left">
        <p className="font-semibold text-slate-900">Mở khóa trọn bộ 5 cấp độ</p>
        <p className="mt-1 text-sm leading-relaxed text-slate-600">
          Starters, Movers, Flyers, KET, PET · trả một lần {formatVnd(currentPriceVnd())} · hoàn tiền
          trong {offer.refundDays} ngày nếu không ưng.
        </p>
      </div>

      <Link
        className="mt-5 inline-block rounded-xl bg-teal-600 px-6 py-3 font-bold text-white shadow-sm transition-colors hover:bg-teal-700"
        href="/mua"
      >
        Xem gói học trọn bộ
      </Link>
      <p className="mt-4">
        <Link className="text-sm font-medium text-slate-500 hover:text-slate-700" href={backHref}>
          {backLabel}
        </Link>
      </p>
    </div>
  );
}
