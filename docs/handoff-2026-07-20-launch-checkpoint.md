# TinySteps launch checkpoint — 2026-07-20

## Trạng thái hiện tại

TinySteps đã code-complete và data/storage-ready cho đợt paid pilot. GitHub private
repository đã được tạo và nhánh `main` đã push thành công. Bước kế tiếp là import
repository vào Vercel, nối custom domain, rồi smoke-test production.

## Đã hoàn thành

### Supabase và Storage

- Supabase project URL đã cấu hình local bằng public variables; service-role key đã
  được xóa khỏi `.env.local` sau khi upload.
- Migration trả phí đã áp dụng: truy vấn `to_regclass('public.paid_access')` trả về
  `paid_access`.
- Bucket `illustrations`: 525/525 QA-approved illustration URL trả HTTP 200.
- Bucket `audio`: upload 6.126 file. Full coverage check ban đầu tìm thấy 8 file sót;
  8 file đó đã được selective-upload lại và từng URL đều trả HTTP 200.
- `NEXT_PUBLIC_AUDIO_BASE_URL` và `NEXT_PUBLIC_ASSET_BASE_URL` đều dùng Storage public
  root, không thêm hậu tố `/audio` hoặc `/illustrations`.

### Ứng dụng

- Match exercise đã đọc illustration manifest và render ảnh từ Supabase CDN.
- Có neutral SVG fallback khi manifest thiếu hoặc ảnh tải lỗi; không hiện
  `image_hint` thành đáp án trên màn hình.
- Landing page, trang `/mua`, VietQR, paywall, paid-access gate, dashboard, SRS review
  và manual activation SOP đã có trong code.
- Health endpoint báo cả audio manifest và illustration count.
- Có các script kiểm tra launch env, audio coverage và illustration coverage.

### Thanh toán

- Agribank đã cấu hình local bằng mã VietQR chính thức `VBA`.
- Số tài khoản/chủ tài khoản lấy từ QR do chủ dự án cung cấp; không ghi trong tài liệu
  hoặc Git.
- Zalo xác nhận đã cấu hình local.
- Offer stage đang là `early_bird` (199.000đ; giá chuẩn trong app là 300.000đ).
- VietQR động đã kiểm tra: HTTP 200, content type `image/png`.
- `NEXT_PUBLIC_SITE_URL=https://tinysteps.xuyenlab.com`.
- `node --env-file=.env.local scripts/check-launch-env.mjs` báo
  `Launch configuration is ready.`

### Kiểm thử

- Vitest: 9 files, 80/80 tests passed.
- Data regression checks: 14/14 lesson cases và 37/37 vocabulary/grammar cases passed.
- ESLint: passed.
- Next.js production build: passed; 13 routes generated.
- Secret scan trước commit: không có Supabase, GitHub, Google, OpenAI key hay private
  key trong snapshot.

### GitHub

- Private repository: `https://github.com/HoangXuyen-STEM/tinysteps-concept`
- Default/local branch: `main`.
- Launch-ready commit: `2ba45c8 feat: prepare TinySteps paid pilot launch`.
- Local branch theo dõi `origin/main`.
- `.env.local`, `tinysteps-data/.env`, editor swap files, generated audio/image
  binaries và ảnh QR ngân hàng đều được ignore.

## Việc làm tiếp theo

1. Mở `https://vercel.com/new`, import private repository
   `HoangXuyen-STEM/tinysteps-concept`.
2. Vercel project name: `tinysteps-concept`; Framework: Next.js; Root Directory:
   `tinysteps-app`; giữ build/install/output defaults.
3. Copy toàn bộ public runtime variables từ local `.env.local` vào Vercel Production
   và Preview. Tuyệt đối không thêm service-role key hoặc Gemini key.
4. Deploy lần đầu và giữ lại URL `*.vercel.app` để chẩn đoán.
5. Vercel → Settings → Domains: thêm `tinysteps.xuyenlab.com`.
6. Cloudflare DNS cho `xuyenlab.com`: tạo/chỉnh CNAME `tinysteps` trỏ tới **đúng target
   Vercel hiển thị**, Proxy status `DNS only`, TTL Auto.
7. Chờ Vercel báo `Valid Configuration` và HTTPS hoạt động.
8. Supabase Auth → URL Configuration:
   - Site URL: `https://tinysteps.xuyenlab.com`
   - Redirect allowlist: thêm production domain (giữ localhost cho development)
   - kiểm tra lại magic-link template và custom SMTP.
9. Chạy production smoke test theo `docs/deployment-guide.md`: landing → login → 3 bài
   free → audio/ảnh → lưu tiến độ → review → `/mua` → QR → paid access.

## Quyết định chưa thay đổi

- Pilot access vẫn là mô hình kín: public signup OFF, magic link dùng
  `shouldCreateUser: false`, 10 tài khoản pilot được tạo tay trong Supabase Dashboard.
- Nếu muốn người lạ tự đăng ký để mở bán công khai, cần một quyết định riêng và thay
  đổi auth/onboarding; không tự ý bật signup trong lúc deploy pilot.
- Kích hoạt sau chuyển khoản vẫn làm tay theo `docs/manual-activation-sop.md`; chỉ tự
  động hóa khi đơn đều đặn vượt khoảng 5–10 đơn/tuần.

## Bắt đầu lại ngày mai

```bash
cd /home/hoang-xuyen/Projects/tinysteps-concept
git status --short --branch
```

Kỳ vọng: nhánh `main` đồng bộ với `origin/main`, không có thay đổi ngoài checkpoint
này sau khi nó được commit.
