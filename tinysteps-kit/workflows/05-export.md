# Workflow 05 — Export Agent

## Vai trò
Convert tất cả JSON data thành HTML đẹp, dễ đọc trên phone, để giáo viên review và góp ý.

## Trigger
Human nói: "Export data" hoặc "Run Agent 5"

## Prerequisite
- Agent 1-4 đã hoàn thành
- Tất cả files trong `tinysteps-data/` đã validate

## Skills cần dùng
- @html-css (responsive HTML, mobile-first)
- @json-processing (đọc JSON data)

## Input
- `tinysteps-data/vocabulary/*.json`
- `tinysteps-data/topics/topics.json`
- `tinysteps-data/grammar/*.json`
- `tinysteps-data/lessons/**/*.json`

## Output
- `tinysteps-data/exports/vocabulary-overview.html`
- `tinysteps-data/exports/topics-overview.html`
- `tinysteps-data/exports/lessons-starters.html`
- `tinysteps-data/exports/lessons-movers.html`
- `tinysteps-data/exports/lessons-flyers.html`
- `tinysteps-data/exports/lessons-ket.html`
- `tinysteps-data/exports/lessons-pet.html`

---

## Các bước thực hiện

### Bước 1: Vocabulary Overview
**Làm gì:** Tạo 1 file HTML tổng hợp tất cả vocabulary, nhóm theo level và topic.
**Skill:** @html-css
**Chi tiết:**

1. Đọc 5 vocabulary files
2. Tạo HTML với cấu trúc:
   - Header: "TinySteps — Từ vựng tổng quan"
   - Tab/section cho mỗi level (Starters | Movers | Flyers | KET | PET)
   - Trong mỗi level: nhóm từ theo topic
   - Mỗi từ hiển thị: word, IPA, part of speech, example sentence
   - Không hiển thị: ID, image_hint, related_words (technical fields)

3. Design requirements:
   - Mobile-first (max-width: 720px, padding: 16px)
   - Font: system font stack (không load external fonts để dùng offline)
   - Mỗi từ là 1 card nhỏ với border-bottom
   - IPA hiển thị font-style: italic, color nhạt hơn
   - Example sentence hiển thị trong blockquote nhỏ
   - Có sticky header cho mỗi level section
   - Có counter: "Starters: 300 từ"

4. Cuối trang: summary table (level, số từ, số topics)

**Output:** `tinysteps-data/exports/vocabulary-overview.html`

---

### Bước 2: Topics Overview
**Làm gì:** Tạo 1 file HTML hiển thị 12 topics với spiral progression.
**Skill:** @html-css
**Chi tiết:**

1. Đọc `topics.json`
2. Tạo HTML với cấu trúc:
   - Header: "TinySteps — Chủ đề và lộ trình"
   - 2 sections: "Trường học" và "Sinh hoạt"
   - Mỗi topic là 1 card lớn chứa:
     - Tên topic + description
     - Spiral progression dạng timeline (Starters → PET)
     - Mỗi level trong spiral: focus, can-do statement, 3 example sentences
   - Color code: school topics = teal, daily_life topics = amber

3. Design: timeline dọc cho spiral progression, mỗi level là 1 node trên timeline

**Output:** `tinysteps-data/exports/topics-overview.html`

---

### Bước 3: Lesson files (1 per level)
**Làm gì:** Tạo 5 files HTML, mỗi file chứa tất cả lessons của 1 level.
**Skill:** @html-css
**Chi tiết:**

1. Đọc lesson files của từng level
2. Mỗi file HTML có cấu trúc:
   - Header: "TinySteps — Bài học {Level}" + số lessons
   - Table of contents (danh sách lessons với title, clickable)
   - Mỗi lesson hiển thị:

   ```
   ┌─────────────────────────────────┐
   │ Lesson 1: Good morning!        │
   │ Topic: Before class             │
   │ Time: ~4 minutes                │
   ├─────────────────────────────────┤
   │ 📍 Scenario                     │
   │ You arrive at school and meet   │
   │ a colleague...                  │
   ├─────────────────────────────────┤
   │ 💬 Dialogue                     │
   │ Ms. Lan: Good morning!          │
   │ Mr. Minh: Good morning! How...  │
   ├─────────────────────────────────┤
   │ 📝 Vocabulary (8 words)         │
   │ hello /həˈləʊ/ — interjection   │
   │ ...                             │
   ├─────────────────────────────────┤
   │ ✏️ Exercises                    │
   │ 1. Match: ...                   │
   │ 2. Arrange: ...                 │
   │ 3. Listen & choose: ...         │
   │ 4. Fill the blank: ...          │
   │ 5. Multiple choice: ...         │
   ├─────────────────────────────────┤
   │ 🤖 AI Conversation              │
   │ Role: colleague                 │
   │ "Good morning! How are you?"    │
   └─────────────────────────────────┘
   ```

3. Design cho exercises:
   - Match: hiển thị dạng 2 cột (image_hint | word)
   - Arrange: hiển thị shuffled words trong badges, đáp án ẩn (click to reveal)
   - Listen: hiển thị audio_text + options
   - Fill blank: hiển thị câu với ___ highlighted
   - Multiple choice: hiển thị options dạng radio buttons (visual only, không interactive)
   - Đáp án: mặc định ẩn, có nút "Hiện đáp án" toggle

4. Navigation: nút Previous/Next lesson ở cuối mỗi lesson

5. Print-friendly: `@media print` ẩn navigation, hiện đáp án

**Output:**
```
tinysteps-data/exports/lessons-starters.html
tinysteps-data/exports/lessons-movers.html
tinysteps-data/exports/lessons-flyers.html
tinysteps-data/exports/lessons-ket.html
tinysteps-data/exports/lessons-pet.html
```

---

### Bước 4: Index page
**Làm gì:** Tạo 1 file index.html liên kết tất cả exports.
**Skill:** @html-css
**Chi tiết:**

1. Tạo landing page đơn giản:
   - Title: "TinySteps — Tài liệu review"
   - Links tới tất cả export files
   - Summary stats: tổng số từ, tổng số lessons, tổng số exercises
   - Footer: "Vui lòng gửi góp ý cho thầy Xuyên"

**Output:** `tinysteps-data/exports/index.html`

---

### Bước 5: Validate exports
**Làm gì:** Kiểm tra tất cả HTML files hoạt động đúng.
**Skill:** @html-css
**Chi tiết:**
1. Mở từng file trong browser, kiểm tra:
   - Hiển thị đúng trên mobile viewport (375px width)
   - Không bị vỡ layout
   - Tất cả links trong Table of Contents hoạt động
   - Nút "Hiện đáp án" hoạt động (JavaScript toggle)
   - Không có broken characters (UTF-8 encoding)
2. Kiểm tra data integrity:
   - Số từ trong vocabulary overview = tổng từ trong JSON
   - Số lessons trong mỗi file = số lesson JSON files
   - Không có "undefined" hoặc "null" hiển thị

**Validation cuối:**
- [ ] 8 HTML files tạo thành công
- [ ] Tất cả responsive trên mobile
- [ ] Table of contents links hoạt động
- [ ] Toggle đáp án hoạt động
- [ ] Data khớp với JSON source
- [ ] UTF-8 encoding đúng
- [ ] Print-friendly

---

## Báo cáo khi hoàn thành

```
✅ Agent 5 (Export) hoàn thành
- Files:
  - vocabulary-overview.html ({n} words)
  - topics-overview.html ({n} topics, {n} spiral entries)
  - lessons-starters.html ({n} lessons)
  - lessons-movers.html ({n} lessons)
  - lessons-flyers.html ({n} lessons)
  - lessons-ket.html ({n} lessons)
  - lessons-pet.html ({n} lessons)
  - index.html (landing page)
- Tổng: {n} HTML files
- Validation: PASSED / FAILED
- Deploy: Sẵn sàng upload lên Cloudflare Pages
```
