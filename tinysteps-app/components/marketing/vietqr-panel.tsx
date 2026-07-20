import {
  bankConfig,
  isBankConfigured,
  transferMemo,
  vietQrImageUrl,
  formatVnd,
} from "@/lib/marketing/offer";

type Props = {
  email: string;
  amountVnd: number;
};

// Shows the buyer a QR with the amount and memo already filled in. The memo carries
// their account email, which is what turns an anonymous bank line into an activation
// we can perform without asking the buyer anything.
export function VietQrPanel({ email, amountVnd }: Props) {
  const memo = transferMemo(email);
  const qrUrl = vietQrImageUrl(amountVnd, memo);

  if (!isBankConfigured() || !qrUrl) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
        <p className="font-semibold text-amber-900">Thông tin chuyển khoản chưa sẵn sàng</p>
        <p className="mt-2 text-sm leading-relaxed text-amber-800">
          Vui lòng nhắn tin trực tiếp để tôi gửi thông tin thanh toán và kích hoạt tài khoản cho bạn.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-center font-bold text-slate-900">
        Quét mã để chuyển {formatVnd(amountVnd)}
      </p>
      {/* eslint-disable-next-line @next/next/no-img-element -- external QR service, not a bundled asset */}
      <img
        alt={`Mã QR chuyển khoản ${formatVnd(amountVnd)}`}
        className="mx-auto mt-4 w-full max-w-[280px] rounded-xl"
        src={qrUrl}
      />

      <dl className="mt-5 space-y-2 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Ngân hàng</dt>
          <dd className="font-medium text-slate-900">{bankConfig.bankCode}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Số tài khoản</dt>
          <dd className="font-mono font-medium text-slate-900">{bankConfig.accountNumber}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Chủ tài khoản</dt>
          <dd className="font-medium text-slate-900">{bankConfig.accountHolder}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Số tiền</dt>
          <dd className="font-medium text-slate-900">{formatVnd(amountVnd)}</dd>
        </div>
      </dl>

      <div className="mt-4 rounded-xl bg-teal-50 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-teal-800">
          Nội dung chuyển khoản
        </p>
        <p className="mt-1 break-all font-mono text-sm font-bold text-teal-900">{memo}</p>
        <p className="mt-2 text-xs leading-relaxed text-teal-800">
          Nếu quét mã QR thì nội dung đã được điền sẵn. Nếu nhập tay, xin giữ đúng nội dung này để
          tôi biết kích hoạt cho tài khoản nào.
        </p>
      </div>
    </div>
  );
}
