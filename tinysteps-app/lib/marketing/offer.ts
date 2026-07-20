/**
 * Launch offer terms. Single source of truth so the landing page, the purchase page
 * and the paywall never quote different numbers at a buyer mid-decision.
 */
export const offer = {
  fullPriceVnd: 300_000,
  earlyBirdPriceVnd: 199_000,
  earlyBirdSeats: 50,
  totalSeats: 100,
  refundDays: 7,
  activationHours: 12,
} as const;

export const formatVnd = (amount: number) => `${amount.toLocaleString("vi-VN")}đ`;

/**
 * Which price is being charged right now. Seats are counted by hand during the launch,
 * so flipping this env var to "standard" after the early-bird seats are gone is the
 * whole switchover — no deploy of new code needed.
 */
export const isEarlyBird = () => process.env.NEXT_PUBLIC_OFFER_STAGE !== "standard";

export const currentPriceVnd = () =>
  isEarlyBird() ? offer.earlyBirdPriceVnd : offer.fullPriceVnd;

/**
 * Bank details for the manual VietQR flow, supplied per-deployment so account numbers
 * never sit in the repository. The purchase page degrades to a "liên hệ trực tiếp"
 * message when these are unset, rather than rendering a broken QR.
 */
export const bankConfig = {
  bankCode: process.env.NEXT_PUBLIC_BANK_CODE,
  accountNumber: process.env.NEXT_PUBLIC_BANK_ACCOUNT,
  accountHolder: process.env.NEXT_PUBLIC_BANK_HOLDER,
  contactUrl: process.env.NEXT_PUBLIC_CONTACT_URL,
  contactLabel: process.env.NEXT_PUBLIC_CONTACT_LABEL ?? "Nhắn tin cho tôi",
} as const;

export const isBankConfigured = () =>
  Boolean(bankConfig.bankCode && bankConfig.accountNumber && bankConfig.accountHolder);

/** Transfer memo that lets a payment be matched to an account without asking. */
export const transferMemo = (email: string) => `TINYSTEPS ${email}`.trim();

/**
 * VietQR renders a scannable transfer QR with the amount and memo pre-filled, which
 * removes the two mistakes that cost the most reconciliation time: wrong amount and
 * missing memo.
 */
export function vietQrImageUrl(amountVnd: number, memo: string): string | null {
  if (!isBankConfigured()) return null;
  const params = new URLSearchParams({
    amount: String(amountVnd),
    addInfo: memo,
    accountName: bankConfig.accountHolder!,
  });
  return `https://img.vietqr.io/image/${bankConfig.bankCode}-${bankConfig.accountNumber}-compact2.png?${params}`;
}
