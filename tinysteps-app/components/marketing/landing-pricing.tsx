import Link from "next/link";
import { offer, formatVnd } from "@/lib/marketing/offer";

const included = [
  "Trọn bộ 5 cấp độ: Starters, Movers, Flyers, KET, PET",
  "Ôn tập ngắt quãng tự động — học rồi không rơi rụng",
  "Âm thanh chuẩn cho từ vựng và hội thoại",
  "Theo dõi tiến độ và chuỗi ngày học",
  "Học trọn đời, không phí gia hạn",
] as const;

export function LandingPricing() {
  return (
    <section className="mx-auto mt-16 max-w-3xl px-4 sm:px-6" id="gia">
      <h2 className="text-2xl font-bold text-slate-900">Một lần, học trọn</h2>
      <p className="mt-2 leading-relaxed text-slate-600">
        Mức phí này để bù chi phí máy chủ và giọng đọc. TinySteps là dự án tâm huyết của một giáo
        viên, không phải một cỗ máy bán hàng.
      </p>

      <div className="mt-6 rounded-2xl border-2 border-teal-600 bg-white p-6 shadow-sm">
        <p className="inline-block rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-800">
          Ưu đãi ra mắt · {offer.earlyBirdSeats} người đầu tiên
        </p>
        <div className="mt-4 flex items-baseline gap-3">
          <span className="text-4xl font-bold text-slate-900">
            {formatVnd(offer.earlyBirdPriceVnd)}
          </span>
          <span className="text-lg text-slate-400 line-through">
            {formatVnd(offer.fullPriceVnd)}
          </span>
        </div>
        <p className="mt-2 text-sm text-slate-600">
          Đợt ra mắt nhận tối đa {offer.totalSeats} học viên rồi đóng đăng ký — để tôi kịp hỗ trợ
          từng người một cách tử tế.
        </p>

        <ul className="mt-5 space-y-2">
          {included.map((item) => (
            <li className="flex gap-2 text-slate-700" key={item}>
              <span aria-hidden="true" className="text-teal-600">
                ✓
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>

        <Link
          className="mt-6 block rounded-xl bg-teal-600 px-6 py-3 text-center font-bold text-white shadow-sm transition-colors hover:bg-teal-700"
          href="/mua"
        >
          Đăng ký học trọn gói
        </Link>
        <p className="mt-3 text-center text-sm text-slate-500">
          Hoàn tiền trong {offer.refundDays} ngày, không cần lý do.
        </p>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-slate-500">
        So sánh cho dễ hình dung: một buổi học thêm thường 200.000-300.000đ, một khóa ở trung tâm
        thường 2-5 triệu.
      </p>
    </section>
  );
}
