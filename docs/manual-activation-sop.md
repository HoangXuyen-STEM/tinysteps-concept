# SOP — Kích hoạt tài khoản trả phí thủ công

Quy trình vận hành đợt ra mắt: người mua chuyển khoản → đối soát → kích hoạt tay.
Cam kết công khai với người mua: **kích hoạt trong 12 giờ**, **hoàn tiền trong 7 ngày không cần lý do**.

## Chuẩn bị một lần trước khi mở bán

1. Điền biến môi trường trên Vercel (Production) — xem `tinysteps-app/.env.local.example`:
   - `NEXT_PUBLIC_BANK_CODE` (VCB, TCB, MB, ACB, BIDV…), `NEXT_PUBLIC_BANK_ACCOUNT`, `NEXT_PUBLIC_BANK_HOLDER`
   - `NEXT_PUBLIC_CONTACT_URL` (link Zalo/Messenger), `NEXT_PUBLIC_CONTACT_LABEL`
   - `NEXT_PUBLIC_OFFER_STAGE=early_bird` → đổi thành `standard` khi hết 50 suất đầu
   - Chưa điền đủ 3 biến ngân hàng thì trang `/mua` tự hiện thông báo "liên hệ trực tiếp", không hiện QR hỏng.
   - **Bảng quản trị `/admin`** (khuyến nghị thay cho SQL tay): điền biến **chỉ ở máy chủ**
     (KHÔNG có tiền tố `NEXT_PUBLIC_`): `ADMIN_EMAILS` (danh sách email admin, ngăn cách bằng dấu phẩy).
     Thiếu `ADMIN_EMAILS` thì `/admin` trả 404 cho mọi người. **Không cần `SUPABASE_SERVICE_ROLE_KEY`
     trên Vercel nữa** — mọi thao tác kích hoạt/thu hồi chạy bằng chính phiên đăng nhập của admin qua RPC.
     `ADMIN_EMAILS` chỉ là "cổng UI" (ẩn trang); ranh giới bảo mật thật là bảng `admin_users` + các hàm
     SECURITY DEFINER trong migration `000005` — chỉ email nằm trong `admin_users` mới ghi được dữ liệu.
2. Chạy migration `supabase/migrations/000004_paid_access.sql` và
   `supabase/migrations/000005_admin_paid_access_rpc.sql` trên project Supabase.
2a. **Thêm admin đầu tiên** (một lần, trong Supabase → SQL Editor) — thay email của bạn:

```sql
insert into admin_users (user_id, email)
select id, email from auth.users where email = '<email admin của bạn>'
on conflict (user_id) do nothing;
```

   - Không có dòng nào được thêm → email đó chưa có tài khoản Supabase Auth. Tạo tài khoản trước rồi chạy lại.
2b. Nếu audio đã từng upload lên Supabase Storage, chạy lại với cờ ghi đè để các file audio vừa sửa
   thay được bản cũ (hiện là 275 file sau bốn đợt sửa) — nếu không, người học sẽ nghe một đằng đọc một nẻo:
   `node scripts/upload-audio-to-storage.mjs --overwrite`
3. Tạo sheet theo dõi đơn với các cột:
   `thời gian CK | số tiền | email | nội dung CK | trạng thái | thời điểm kích hoạt | nguồn | ghi chú`
   - `trạng thái`: chờ đối soát | đã kích hoạt | đã hoàn tiền | cần liên hệ
   - `nguồn`: nhóm/bài đăng nào ra đơn — cột này quyết định Phase 5 đẩy tiếp kênh nào.

## Quy trình mỗi đơn

1. **Nhận tiền.** App ngân hàng báo có, nội dung dạng `TINYSTEPS <email>`.
2. **Đối soát.** Ghi dòng mới vào sheet. Kiểm tra số tiền khớp giá đang bán (199.000đ giai đoạn early-bird, 300.000đ sau đó).
3. **Kích hoạt.** Cách nhanh: mở `/admin`, tìm theo email → điền số tiền + mã giao dịch + ghi chú → xác nhận.
   Kích hoạt lại một tài khoản đã thu hồi sẽ **cập nhật đúng dòng cũ** (không tạo dòng trùng).
   Cách thủ công (dự phòng) trong Supabase → SQL Editor:

```sql
insert into paid_access (user_id, amount_vnd, transfer_ref, note)
select id, 199000, '<mã giao dịch>', 'early-bird'
from auth.users
where email = '<email người mua>';
```

   - Không có dòng nào được tạo → email chưa đăng ký tài khoản. Chuyển sang mục "Tình huống bất thường".
   - Kiểm tra nhanh: `select * from paid_access where user_id = (select id from auth.users where email = '<email>');`
4. **Nhắn xác nhận** cho người mua (mẫu bên dưới). Cập nhật sheet: trạng thái + thời điểm kích hoạt.
5. **Chăm sóc ngày thứ 3:** nhắn hỏi đã học tới đâu, có vướng gì không. Vừa giữ chân vừa lấy lời chứng thực.

## Hoàn tiền

1. Chuyển trả đủ số tiền đã nhận, không hỏi lý do.
2. Thu hồi quyền — không xóa dòng, để giữ lịch sử đối soát. Cách nhanh: mở `/admin`, tìm email → điền lý do →
   xác nhận "Thu hồi". Cách thủ công (dự phòng):

```sql
update paid_access set revoked_at = now(), note = 'refund: <lý do ngắn>'
where user_id = (select id from auth.users where email = '<email>');
```

3. Cập nhật sheet trạng thái `đã hoàn tiền`. Ghi lại lý do — dữ liệu này quý cho Phase 5.

## Tình huống bất thường

| Tình huống | Xử lý |
|---|---|
| CK không có nội dung / sai cú pháp | Đối soát theo số tiền + thời gian, nhắn hỏi email đăng ký. Chưa xác định được thì **chưa kích hoạt**. |
| Email trong nội dung CK chưa có tài khoản | Nhắn hướng dẫn tạo tài khoản trước, giữ đơn ở trạng thái "cần liên hệ". |
| Chuyển thiếu tiền | Nhắn lịch sự, xin chuyển bù phần thiếu hoặc hoàn lại toàn bộ nếu họ đổi ý. |
| Chuyển dư tiền | Hoàn lại phần dư ngay, nói rõ trong tin nhắn xác nhận. |
| Hai người cùng một email | Không thể xảy ra — email là khóa tài khoản. Nếu có, liên hệ làm rõ trước khi kích hoạt. |

## Mẫu tin nhắn

**Xác nhận + chào mừng**

> Em/tôi đã nhận được chuyển khoản của thầy/cô và kích hoạt tài khoản rồi ạ.
> Thầy/cô đăng nhập lại tại <link app> là học được trọn bộ 5 cấp độ.
> Gợi ý bắt đầu: học tiếp từ chỗ đang dở, mỗi ngày 10-15 phút, phần "Ôn tập" sẽ tự nhắc lại từ sắp quên.
> Có gì vướng thầy/cô cứ nhắn em/tôi bất cứ lúc nào ạ.

**CK thiếu nội dung**

> Em/tôi thấy có một khoản chuyển khoản <số tiền> lúc <giờ> nhưng chưa rõ email đăng ký.
> Thầy/cô cho em/tôi xin email đã dùng tạo tài khoản TinySteps để kích hoạt đúng người ạ.

**Chưa có tài khoản**

> Em/tôi đã nhận được tiền của thầy/cô ạ. Thầy/cô tạo giúp tài khoản tại <link app>/login bằng email
> <email trong nội dung CK>, xong nhắn em/tôi một tiếng là em/tôi kích hoạt ngay ạ.

## Ngưỡng cần tự động hóa

Kích hoạt tay chỉ hợp với quy mô ra mắt (trần 100 học viên). Khi đơn đều đặn **>5-10/tuần** hoặc việc đối soát bắt đầu trễ hơn cam kết 12 giờ, mở plan kỹ thuật tích hợp SePay/VietQR tự động. Dưới ngưỡng đó thì làm tay vẫn rẻ và an toàn hơn.
