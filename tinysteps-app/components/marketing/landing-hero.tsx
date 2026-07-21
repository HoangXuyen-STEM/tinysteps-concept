import Link from "next/link";
import { formatVnd, currentPriceVnd } from "@/lib/marketing/offer";

// Hero leads with the founder story rather than the product: the target reader is a
// teacher of another subject who is embarrassed about starting over, and the single
// most persuasive fact available is that the person selling this started over too.
export function LandingHero() {
  return (
    <section className="mx-auto max-w-3xl px-4 pt-12 sm:px-6 sm:pt-16">
      <p className="text-sm font-semibold text-teal-700">Dành cho giáo viên</p>
      <h1 className="mt-3 text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">
        Xây nền tiếng Anh vững, để mỗi bước học tiếp đều nhẹ nhàng hơn
      </h1>
      <p className="mt-4 text-lg leading-relaxed text-slate-600">
        Từ vựng và ngữ pháp nền theo khung Cambridge quen thuộc: Starters → Movers → Flyers → KET →
        PET. Mỗi ngày 10 phút.
      </p>

      <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-6">
        <p className="text-base leading-relaxed text-slate-700">
          &ldquo;Tôi là <strong className="font-semibold text-slate-900">Đỗ Hoàng Xuyên</strong>, giáo
          viên Hóa học. U50, tôi vẫn học và dùng tiếng Anh mỗi ngày. Và tiếng Anh của tôi bắt đầu từ
          bộ <strong className="font-semibold text-slate-900">Starters</strong> — những bài đầu tiên,
          học cùng con gái.&rdquo;
        </p>
        <p className="mt-4 text-sm leading-relaxed text-slate-600">
          TinySteps là chính con đường đó, được sắp xếp lại gọn gàng để bạn đi nhanh hơn tôi ngày
          trước.
        </p>
      </div>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
        <Link
          className="rounded-xl bg-teal-600 px-6 py-3 text-center font-bold text-white shadow-sm transition-colors hover:bg-teal-700"
          href="/login"
        >
          Học thử 3 bài miễn phí
        </Link>
        <Link
          className="rounded-xl border border-slate-200 px-6 py-3 text-center font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          href="/mua"
        >
          Xem gói {formatVnd(currentPriceVnd())}
        </Link>
      </div>
      <p className="mt-3 text-sm text-slate-500">
        Không cần thẻ, không tự động gia hạn. Học thử trước, quyết định sau.
      </p>
    </section>
  );
}
