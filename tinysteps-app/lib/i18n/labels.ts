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

  // SRS review
  ON_TAP: "Ôn tập",
  ON_TAP_TU_VUNG: "Ôn tập từ vựng",
  XEM_DAP_AN: "Xem đáp án",
  NGHE_TU: "Nghe từ",
  NGHE_CAU: "Nghe câu",
  DA_XONG_HOM_NAY: "Đã xong hôm nay 🎉",
  KHONG_CO_TU_ON: "Không có từ nào cần ôn hôm nay.",
  QUAY_LAI_SAU: "Hãy quay lại sau để ôn tiếp.",
  HOAN_THANH_LUOT_ON: "Hoàn thành 1 lượt ôn ✓",
  TIEP_TUC_ON: "Tiếp tục",
  DUNG_LAI: "Dừng lại",
  DA_ON: "Đã ôn",
  TU: "từ",
  TU_MOI: "từ mới",
  CAN_ON: "cần ôn",

  // Dashboard
  BANG_DIEU_KHIEN: "Bảng điều khiển",
  CHUOI_NGAY: "Chuỗi ngày",
  NGAY: "ngày",
  TU_CAN_ON: "từ cần ôn",
  TIEP_TUC_HOC: "Tiếp tục học",
  XEM_TAT_CA_BAI_HOC: "Xem tất cả bài học",
  CHUA_CO_TIEN_DO: "Bạn chưa học bài nào. Bắt đầu ngay nhé!",
  BAT_DAU_HOC: "Bắt đầu học",
  HOC_HOM_NAY_GIU_CHUOI: "Học hôm nay để giữ chuỗi 🔥",
  XIN_CHAO: "Xin chào",

  // Paid access
  CAN_GOI_TRON_BO: "Cần gói học trọn bộ",
  MO_KHOA_TRON_BO: "Mở khóa trọn bộ",
  HOC_THU_MIEN_PHI: "Học thử miễn phí",

  GOP_Y: "Góp ý",
  DANG_XUAT: "Đăng xuất",
  TRANG_CHU: "Trang chủ",
} as const;
