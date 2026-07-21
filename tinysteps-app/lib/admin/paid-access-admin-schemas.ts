import { z } from "zod";

// Shared field rules. Kept in one place so the search, activate and revoke forms validate
// identically on every server call and never diverge.

const email = z
  .string()
  .trim()
  .min(1, "Nhập email học viên.")
  .email("Email không hợp lệ.")
  .transform((value) => value.toLowerCase());

// A manual bank transfer is whole VND, always positive, and comfortably under the max
// integer the paid_access.amount_vnd column stores. Reject anything else rather than write
// a nonsensical reconciliation amount.
const amountVnd = z.coerce
  .number({ error: "Nhập số tiền đã nhận." })
  .int("Số tiền phải là số nguyên.")
  .positive("Số tiền phải lớn hơn 0.")
  .max(1_000_000_000, "Số tiền quá lớn.");

const transferRef = z.string().trim().min(1, "Nhập mã giao dịch.").max(200);
const note = z.string().trim().max(500).optional().default("");
const reason = z.string().trim().min(1, "Nhập lý do thu hồi.").max(500);

export const searchUserSchema = z.object({ email });

export const activateAccessSchema = z.object({
  userId: z.string().uuid("Thiếu học viên hợp lệ."),
  amountVnd,
  transferRef,
  note,
});

export const revokeAccessSchema = z.object({
  userId: z.string().uuid("Thiếu học viên hợp lệ."),
  reason,
});

export type ActivateAccessInput = z.infer<typeof activateAccessSchema>;
export type RevokeAccessInput = z.infer<typeof revokeAccessSchema>;
