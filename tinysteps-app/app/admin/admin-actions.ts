"use server";

import { getAdminIdentity } from "@/lib/admin/admin-auth";
import {
  activateAccessSchema,
  createUserAndActivateSchema,
  revokeAccessSchema,
  searchUserSchema,
} from "@/lib/admin/paid-access-admin-schemas";
import {
  activatePaidAccess,
  createUserAndActivate,
  getLearnerAccessState,
  revokePaidAccess,
  type LearnerAccessState,
} from "@/lib/admin/paid-access-admin";

export type AdminActionState = {
  error?: string;
  message?: string;
  email?: string;
  learner?: LearnerAccessState;
};

const FORBIDDEN = "Không có quyền truy cập." as const;

// Every mutation and lookup re-derives the admin identity from the verified session and the
// server-only allow-list. The page already gates rendering, but re-checking here means a
// forged or replayed action POST from a non-admin session changes nothing and reveals nothing.
async function ensureAdmin(): Promise<boolean> {
  return (await getAdminIdentity()) !== null;
}

/** Map a thrown error to an admin-safe message (never a secret value or raw DB detail). */
function toSafeError(error: unknown): string {
  console.error("admin action failed:", error);
  return "Có lỗi xảy ra. Vui lòng thử lại.";
}

export async function searchUserAction(
  _prev: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  if (!(await ensureAdmin())) return { error: FORBIDDEN };

  const parsed = searchUserSchema.safeParse({ email: formData.get("email") });
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Email không hợp lệ." };
  }

  const { email } = parsed.data;
  try {
    const learner = await getLearnerAccessState(email);
    return { email, learner };
  } catch (error) {
    return { email, error: toSafeError(error) };
  }
}

export async function activateAccessAction(
  _prev: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  if (!(await ensureAdmin())) return { error: FORBIDDEN };

  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const parsed = activateAccessSchema.safeParse({
    userId: formData.get("userId"),
    amountVnd: formData.get("amountVnd"),
    transferRef: formData.get("transferRef"),
    note: formData.get("note") ?? "",
  });
  if (!parsed.success) {
    return { email, error: parsed.error.issues[0]?.message ?? "Dữ liệu không hợp lệ." };
  }

  try {
    await activatePaidAccess(parsed.data);
    const learner = await getLearnerAccessState(email);
    return { email, learner, message: "Đã kích hoạt quyền truy cập." };
  } catch (error) {
    return { email, error: toSafeError(error) };
  }
}

export async function revokeAccessAction(
  _prev: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  if (!(await ensureAdmin())) return { error: FORBIDDEN };

  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const parsed = revokeAccessSchema.safeParse({
    userId: formData.get("userId"),
    reason: formData.get("reason"),
  });
  if (!parsed.success) {
    return { email, error: parsed.error.issues[0]?.message ?? "Dữ liệu không hợp lệ." };
  }

  try {
    const result = await revokePaidAccess(parsed.data);
    const learner = await getLearnerAccessState(email);
    if (!result.ok) {
      const reason =
        result.reason === "already_revoked"
          ? "Quyền truy cập đã bị thu hồi trước đó."
          : "Không tìm thấy quyền truy cập để thu hồi.";
      return { email, learner, error: reason };
    }
    return { email, learner, message: "Đã thu hồi quyền truy cập." };
  } catch (error) {
    return { email, error: toSafeError(error) };
  }
}

export async function createUserAndActivateAction(
  _prev: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  if (!(await ensureAdmin())) return { error: FORBIDDEN };

  const parsed = createUserAndActivateSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
    amountVnd: formData.get("amountVnd"),
    transferRef: formData.get("transferRef"),
    note: formData.get("note") ?? "",
  });
  if (!parsed.success) {
    const email = String(formData.get("email") ?? "").trim().toLowerCase();
    return { email, error: parsed.error.issues[0]?.message ?? "Dữ liệu không hợp lệ." };
  }

  const { email } = parsed.data;
  try {
    const result = await createUserAndActivate(parsed.data);
    if (!result.ok) {
      if (result.reason === "service_not_configured") {
        return {
          email,
          error:
            "Chưa cấu hình SUPABASE_SERVICE_ROLE_KEY trên máy chủ. Thêm biến Sensitive trên Vercel rồi thử lại.",
        };
      }
      if (result.reason === "email_exists") {
        // Account already exists — fall back to search so admin can just activate.
        const learner = await getLearnerAccessState(email);
        return {
          email,
          learner,
          error:
            "Email đã có tài khoản. Dùng nút Tìm bên trên rồi Kích hoạt (không tạo lại).",
        };
      }
      return { email, error: "Không tạo được tài khoản. Vui lòng thử lại." };
    }

    const learner = await getLearnerAccessState(email);
    return {
      email,
      learner,
      message: `Đã tạo tài khoản và kích hoạt VIP cho ${email}.`,
    };
  } catch (error) {
    return { email, error: toSafeError(error) };
  }
}
