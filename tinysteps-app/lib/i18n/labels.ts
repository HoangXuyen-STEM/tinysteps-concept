/**
 * Vietnamese UI labels for app chrome.
 * Simple const map — no i18n framework (YAGNI for MVP).
 * English lesson content stays English; only surrounding UI is Vietnamese.
 */
export const labels = {
  // Audio
  NGHE: "Nghe",
  NGHE_TAT_CA: "Nghe tất cả",
  DANG_PHAT: "Đang phát…",

  // Exercises
  BAI_TAP: "Bài tập",
  KIEM_TRA: "Kiểm tra",
  XAC_NHAN: "Xác nhận",
  TIEP_TUC: "Tiếp tục",
  DUNG: "Đúng!",
  SAI: "Sai",
  DAP_AN_DUNG: "Đáp án đúng",

  // Lesson player
  BAI_HOC: "Bài học",
  BAT_DAU: "Bắt đầu luyện tập",
  HOAN_THANH_BAI: "Hoàn thành bài",

  // Result
  KET_QUA: "Kết quả",
  DIEM: "Điểm",
  CAU_DUNG: "câu đúng",
  XUAT_SAC: "Xuất sắc! 🎉",
  TOT_LAM: "Tốt lắm! 👏",
  CO_GANG_THEM: "Cố gắng thêm nhé! 💪",
  LAM_LAI: "Làm lại",
  VE_DANH_SACH: "Về danh sách",

  // Progress badges
  DA_HOAN_THANH: "Đã hoàn thành",
  DANG_HOC: "Đang học",
  CHUA_HOC: "Chưa học",
  HOAN_THANH: "hoàn thành",
} as const;
