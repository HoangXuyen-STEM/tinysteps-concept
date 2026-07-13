# TinySteps — Rules (Do & Don't)

Áp dụng cho TẤT CẢ agents trong pipeline. Mỗi workflow có thêm rules riêng.

---

## DO — Luôn tuân thủ

### Ngôn ngữ & Nội dung
- **DO** viết tất cả vocabulary, dialogues, examples bằng tiếng Anh. Không kèm bản dịch tiếng Việt trong JSON data.
- **DO** dùng câu ngắn, từ phổ biến, tình huống thực tế. Ưu tiên high-frequency words.
- **DO** đảm bảo mỗi từ/câu gắn với 1 bối cảnh cụ thể (ở trường, ở chợ, ở nhà hàng...).
- **DO** tuân thủ CEFR level nghiêm ngặt. Starters chỉ dùng từ Starters, không "lỡ" dùng từ level cao hơn.
- **DO** thiết kế spiral progression: cùng 1 topic xuất hiện ở nhiều level với độ phức tạp tăng dần.
- **DO** thêm image_hint cho mỗi vocabulary entry (mô tả ngắn bằng English để generate hình minh họa sau).

### Kỹ thuật
- **DO** validate JSON trước khi lưu. Mỗi file phải valid JSON, không có trailing comma.
- **DO** dùng đúng schema đã định nghĩa trong `schemas/`. Không thêm field mới mà không cập nhật schema.
- **DO** dùng snake_case cho tất cả keys trong JSON.
- **DO** dùng ID format: `{level}_{type}_{number}` (ví dụ: `starters_vocab_001`, `movers_lesson_015`).
- **DO** ghi log số lượng items đã tạo sau mỗi bước để dễ kiểm tra.
- **DO** đọc output của agent trước (nếu có) làm input, không tự generate lại data đã có.

### Chất lượng
- **DO** đảm bảo mỗi lesson có đúng 5 loại exercises: match (nối hình-từ), arrange (sắp xếp câu), listen-choose (nghe-chọn), fill-blank (điền từ), multiple-choice (chọn đáp án).
- **DO** đảm bảo dialogues nghe tự nhiên — như người thật nói, không như sách giáo khoa.
- **DO** ưu tiên câu mẫu mà giáo viên VN có thể dùng ngay trong công việc.

---

## DON'T — Tuyệt đối không

### Ngôn ngữ & Nội dung
- **DON'T** giải thích grammar rules trực tiếp. Không có "Present simple is used when...". Grammar được học qua ví dụ và lặp lại.
- **DON'T** dùng từ vựng academic/formal quá mức. Ưu tiên spoken English thực tế.
- **DON'T** tạo bài tập drill từ lẻ (từ không có ngữ cảnh). Mỗi từ phải nằm trong 1 tình huống.
- **DON'T** dùng slang, idioms phức tạp, hoặc cultural references khó hiểu với người Việt.
- **DON'T** trộn level — không dùng từ B1 trong bài Starters dù nó "có vẻ đơn giản".
- **DON'T** tạo nội dung nhạy cảm: chính trị, tôn giáo, bạo lực, phân biệt.

### Kỹ thuật
- **DON'T** thay đổi schema JSON mà không báo. Nếu cần field mới, dừng lại và hỏi.
- **DON'T** tạo file ngoài cấu trúc thư mục đã quy định trong PROJECT_SPEC.md.
- **DON'T** hardcode paths. Dùng relative paths từ root `tinysteps-data/`.
- **DON'T** tạo file quá lớn (>500KB/file). Nếu lesson data quá nhiều, chia nhỏ theo level.
- **DON'T** skip validation step. Mỗi agent phải validate output trước khi hoàn thành.

### Quy trình
- **DON'T** chạy agent sau khi agent trước chưa hoàn thành và validate xong.
- **DON'T** tự ý thay đổi số lượng modules (12) hoặc levels (5) đã quy định.
- **DON'T** tự ý quyết định khi gặp ambiguity. Dừng lại, liệt kê options, và hỏi Xuyen.
- **DON'T** generate toàn bộ 175 lessons trong 1 lần. Tạo 5-10 lessons mẫu trước, review, rồi mới scale.

---

## Quality Checklist (áp dụng cho mỗi agent sau khi hoàn thành)

- [ ] Output JSON valid (no syntax errors)
- [ ] Đúng schema (so với file trong `schemas/`)
- [ ] Đúng số lượng items như kế hoạch
- [ ] Không có duplicate IDs
- [ ] Không có từ/câu vượt level
- [ ] Mỗi item có đủ required fields
- [ ] ID format đúng: `{level}_{type}_{number}`
- [ ] File size < 500KB
