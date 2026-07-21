# TinySteps production fixes checkpoint — 2026-07-21

Tiếp nối `handoff-2026-07-20-launch-checkpoint.md`. Hôm nay đã deploy production
thành công lên Vercel + custom domain, chạy smoke test và sửa các vấn đề phát hiện.

## Nguyên tắc định hướng

Web sẽ cải thiện liên tục theo **feedback từ người học**. Các quyết định về nội dung,
UX, chấm điểm nên ưu tiên trải nghiệm và thành quả người học; chốt sớm rồi tinh chỉnh
theo phản hồi thực tế thay vì cố hoàn hảo trước khi ra mắt.

## Đã hoàn thành hôm nay

### Deploy & hạ tầng
- Vercel import repo + deploy thành công; domain `tinysteps.xuyenlab.com` đã
  `Valid Configuration`, HTTPS chạy.
- **Region:** ghim `sin1` (Singapore) qua `tinysteps-app/vercel.json`. Trước đó chạy
  `iad1` (US East). TTFB landing giảm ~0.5–0.67s → ~0.31–0.34s. Xác nhận qua
  `x-vercel-id: hkg1::sin1::...`.
- Supabase Auth cấu hình cho production domain; magic-link hoạt động.

### Gỡ thương hiệu FSEL (commit 54083b7)
- Bỏ tên FSEL khỏi landing (hero, pillars, FAQ, footer disclaimer), chuyển trọng tâm
  sang trải nghiệm & thành quả người học.
- Workspace marketing riêng (`~/Projects/tinysteps-marketing`, không phải git repo) cũng
  đã gỡ FSEL ở messaging-house, content-calendar, plan + phases; giữ nguyên timing
  launch 18-24/8 (chỉ mô tả "tháng tự học", không nêu tên).

### Sửa lỗi phát hiện khi smoke test
- **Magic-link báo "liên kết không hợp lệ":** template Supabase dùng
  `{{ .ConfirmationURL }}` → sửa thành
  `{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email` (khớp route
  `app/auth/confirm/route.ts`). Đã đăng nhập được.
- **Vercel "Deployment Blocked" (commit email):** email commit không khớp GitHub. Đã
  set `git config user.email dhxuyen@thpt-ngogiatu-daklak.edu.vn` (repo-local) → deploy OK.
- **Audio không phát:** đã tự phát được sau khi kiểm tra (env `NEXT_PUBLIC_AUDIO_BASE_URL`
  trên Vercel đúng).
- **Chấm đáp án cứng (commit 4636ff3):** `normalize()` mở rộng contraction — "I am" = "I'm",
  "don't" = "do not"… áp dụng đối xứng nên không bao giờ chấm sai câu đúng. 84/84 test pass.
- **Multiple-choice "Look at the picture" nhưng không có ảnh (commit 2a4b8c3, dd2967b):**
  - 525 item MC nhét mô tả ảnh vào text, UI không render ảnh.
  - Tách mô tả → field `image_hint`, prompt còn lại "What is this?".
  - Phát hiện image_hint của MC **trùng 100%** với bài `match` (cùng thứ tự item, cả 175
    bài) → MC dùng lại 525 ảnh match đã có trên Supabase, không sinh ảnh mới.
  - UI: có ảnh thì hiện ảnh, chưa có thì hiện mô tả text làm gợi ý (fallback an toàn).

## Commit hôm nay (đã push origin/main)

```
b016e72 perf: pin serverless region to Singapore for the Vietnam audience
dd2967b feat: reuse match illustrations for multiple-choice items
2a4b8c3 feat: give multiple-choice exercises their own picture
4636ff3 fix: accept contraction and full-form answers as equivalent
3e3c7ae chore: trigger redeploy with verified git email
54083b7 copy: remove FSEL brand mentions from landing copy
```

## Trạng thái kiểm thử

- Vitest: 9 files, 84/84 pass (thêm test contraction).
- tsc: pass. ESLint: pass. Next build: pass.

## Smoke test còn lại (cần session đăng nhập + DB — chưa chạy)

1. **Lưu tiến độ:** học xong 1 bài → `/lessons` hiện đã hoàn thành → reload vẫn còn.
2. **Review SRS:** `/review` hiện thẻ ôn tập (hoặc "chưa có thẻ" nếu chưa học).
3. **`/mua` + VietQR:** khi đã đăng nhập phải hiện QR + đúng Ngân hàng/Số TK/Chủ TK +
   nội dung CK chứa email. Nếu hiện ô vàng "chưa sẵn sàng" → 3 biến
   `NEXT_PUBLIC_BANK_CODE/ACCOUNT/HOLDER` chưa set trên Vercel (không có trong Git, phải
   nhập tay).
4. **Paid access:** kích hoạt tay theo `docs/manual-activation-sop.md` → reload `/mua`
   phải thành "Tài khoản đã kích hoạt".

## Tùy chọn nâng cấp (không bắt buộc cho launch)

- **Landing tĩnh:** bỏ `getClaims()` trên trang công khai để landing thành static/ISR,
  phục vụ từ edge (~0.05s). Đòn bẩy tốc độ tiếp theo sau region.
- **Ảnh riêng cho MC:** nếu muốn ảnh khác bài match, chạy pipeline sinh ảnh theo
  `plans/260721-1213-multiple-choice-illustrations/plan.md`. UI tự chuyển sang ảnh mới,
  không cần sửa code.

## Unresolved / cần chú ý

- Chưa xác minh 3 biến bank env trên Vercel (mục smoke test 3) — kiểm tra trước khi nhận
  đơn thật.
- Chưa chạy 4 mục smoke test cần đăng nhập ở trên.
