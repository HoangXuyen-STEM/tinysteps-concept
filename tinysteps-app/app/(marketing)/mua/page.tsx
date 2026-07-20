import type { Metadata } from "next";
import Link from "next/link";
import { createClient } from "@/utils/supabase/server";
import { hasPaidAccess } from "@/lib/access/paid-access";
import { VietQrPanel } from "@/components/marketing/vietqr-panel";
import { offer, formatVnd, currentPriceVnd, isEarlyBird, bankConfig } from "@/lib/marketing/offer";

export const metadata: Metadata = {
  title: "Đăng ký học trọn gói — TinySteps",
  description: `Học trọn bộ 5 cấp độ TinySteps. Hoàn tiền trong ${offer.refundDays} ngày.`,
};

// Three states share one URL: a visitor evaluating the offer, a signed-in learner who
// needs transfer details, and someone already activated. Splitting them into separate
// routes would only create links that go stale as a buyer moves through the flow.
export default async function PurchasePage() {
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const email = data?.claims?.email as string | undefined;
  const isSignedIn = Boolean(data?.claims?.sub);
  const alreadyPaid = isSignedIn ? await hasPaidAccess() : false;

  const price = currentPriceVnd();

  if (alreadyPaid) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        <h1 className="text-2xl font-bold text-slate-900">Tài khoản đã kích hoạt</h1>
        <p className="mt-3 leading-relaxed text-slate-600">
          Bạn đã có quyền học trọn bộ. Cảm ơn bạn đã tin tưởng TinySteps.
        </p>
        <Link
          className="mt-6 inline-block rounded-xl bg-teal-600 px-6 py-3 font-bold text-white transition-colors hover:bg-teal-700"
          href="/dashboard"
        >
          Vào học ngay
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900">Đăng ký học trọn gói</h1>
      <div className="mt-3 flex items-baseline gap-3">
        <span className="text-3xl font-bold text-slate-900">{formatVnd(price)}</span>
        {isEarlyBird() && (
          <span className="text-lg text-slate-400 line-through">
            {formatVnd(offer.fullPriceVnd)}
          </span>
        )}
      </div>
      <p className="mt-2 text-slate-600">
        Trả một lần, học trọn đời cả 5 cấp độ. Hoàn tiền trong {offer.refundDays} ngày, không cần lý
        do.
      </p>

      <ol className="mt-8 space-y-4">
        <li className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="font-bold text-slate-900">1. Tạo tài khoản</p>
          <p className="mt-1 text-sm leading-relaxed text-slate-600">
            Tài khoản dùng email của bạn — đây cũng là cách tôi biết cần kích hoạt cho ai.
          </p>
          {isSignedIn ? (
            <p className="mt-3 text-sm font-medium text-teal-700">✓ Đã đăng nhập: {email}</p>
          ) : (
            <Link
              className="mt-3 inline-block rounded-xl bg-teal-600 px-5 py-2.5 font-bold text-white transition-colors hover:bg-teal-700"
              href="/login"
            >
              Tạo tài khoản / Đăng nhập
            </Link>
          )}
        </li>

        <li className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="font-bold text-slate-900">2. Chuyển khoản</p>
          {isSignedIn && email ? (
            <div className="mt-4">
              <VietQrPanel amountVnd={price} email={email} />
            </div>
          ) : (
            <p className="mt-1 text-sm leading-relaxed text-slate-600">
              Sau khi đăng nhập, mã QR chuyển khoản sẽ hiện ở đây với số tiền và nội dung điền sẵn.
            </p>
          )}
        </li>

        <li className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="font-bold text-slate-900">3. Tôi kích hoạt tài khoản cho bạn</p>
          <p className="mt-1 text-sm leading-relaxed text-slate-600">
            Trong vòng {offer.activationHours} giờ kể từ khi nhận được chuyển khoản, thường là nhanh
            hơn nhiều. Bạn sẽ nhận được tin nhắn xác nhận và có thể vào học ngay.
          </p>
          {bankConfig.contactUrl && (
            <a
              className="mt-3 inline-block rounded-xl border border-slate-200 px-5 py-2.5 font-semibold text-slate-700 transition-colors hover:bg-slate-50"
              href={bankConfig.contactUrl}
              rel="noopener noreferrer"
              target="_blank"
            >
              {bankConfig.contactLabel}
            </a>
          )}
        </li>
      </ol>

      <div className="mt-8 rounded-2xl bg-slate-50 p-5">
        <p className="font-semibold text-slate-900">Chính sách hoàn tiền</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          Trong {offer.refundDays} ngày kể từ khi tài khoản được kích hoạt, nếu bạn thấy TinySteps
          không hợp với mình, nhắn cho tôi một câu là tôi hoàn lại đủ số tiền. Không cần giải thích,
          không hỏi lý do.
        </p>
      </div>
    </main>
  );
}
