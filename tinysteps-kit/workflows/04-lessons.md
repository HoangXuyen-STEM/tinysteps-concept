# Workflow 04 — Lessons Agent

## Vai trò
Tạo lessons hoàn chỉnh: dialogue + 5 exercises + AI conversation prompt. Đây là agent phức tạp nhất — tổng hợp output từ 3 agents trước.

## Trigger
Human nói: "Tạo lessons" hoặc "Run Agent 4"

## Prerequisite
- Agent 1 → `tinysteps-data/vocabulary/*.json`
- Agent 2 → `tinysteps-data/topics/topics.json`
- Agent 3 → `tinysteps-data/grammar/*.json`

## Skills cần dùng
- @creative-writing (dialogues tự nhiên)
- @curriculum-design (lesson sequencing, exercise design)
- @json-processing (output structured data)

## Input
- Tất cả output từ Agent 1, 2, 3
- Schema: `schemas/lesson.schema.json`
- Rules: `RULES.md`

## Output
- `tinysteps-data/lessons/starters/lesson-001.json` → `lesson-030.json`
- `tinysteps-data/lessons/movers/lesson-001.json` → `lesson-035.json`
- `tinysteps-data/lessons/flyers/lesson-001.json` → `lesson-040.json`
- `tinysteps-data/lessons/ket/lesson-001.json` → `lesson-035.json`
- `tinysteps-data/lessons/pet/lesson-001.json` → `lesson-040.json`

---

## QUAN TRỌNG: Chiến lược "Batch nhỏ → Review → Scale"

**KHÔNG tạo 175 lessons cùng lúc.** Thay vào đó:

1. **Batch 1:** Tạo 5 lessons mẫu cho Starters (lesson-001 → 005)
2. **Review:** Human review chất lượng, điều chỉnh nếu cần
3. **Batch 2:** Nếu OK, tạo thêm 25 lessons Starters còn lại
4. **Batch 3-6:** Lặp lại cho Movers, Flyers, KET, PET

Mỗi batch đều phải qua validation trước khi chuyển sang batch tiếp.

---

## Các bước thực hiện

### Bước 1: Lên lesson plan cho mỗi level
**Làm gì:** Xác định thứ tự lessons, mỗi lesson cover topic nào, vocab nào, grammar nào.
**Skill:** @curriculum-design
**Chi tiết:**

1. Đọc `topics.json` để biết 12 topics và spiral progression
2. Phân bổ lessons cho mỗi level:

| Level | Số lessons | Lessons/topic (trung bình) |
|-------|-----------|---------------------------|
| Starters | 30 | 2-3 per topic |
| Movers | 35 | 2-3 per topic |
| Flyers | 40 | 3-4 per topic |
| KET | 35 | 2-3 per topic |
| PET | 40 | 3-4 per topic |

3. Quy tắc sắp xếp thứ tự:
   - Lessons đầu tiên (1-5): topic_social và topic_before_class (dễ nhất, gần gũi nhất)
   - Xen kẽ school và daily_life topics (không dồn 10 bài school liên tiếp)
   - Grammar point mới: giới thiệu trong 1 lesson, ôn lại trong 2-3 lessons sau
   - Vocabulary: mỗi lesson giới thiệu 6-12 từ mới + ôn 3-5 từ cũ

4. Output: file plan `_raw/lesson_plan_{level}.json` cho mỗi level

**Format lesson plan:**
```json
{
  "level": "starters",
  "lessons": [
    {
      "order": 1,
      "topic_id": "topic_social",
      "title_hint": "Greeting colleagues",
      "new_vocab_ids": ["starters_vocab_001", "..."],
      "review_vocab_ids": [],
      "grammar_ids": ["starters_grammar_002"],
      "scenario_hint": "Meeting a colleague in the morning"
    }
  ]
}
```

**Validation:**
- Tổng lessons đúng số lượng
- Mỗi topic được cover ít nhất 2 lần mỗi level
- Grammar points được cover đủ (không bỏ sót)
- Vocabulary coverage ≥ 90% (≥ 90% từ xuất hiện trong ít nhất 1 lesson)

---

### Bước 2: Tạo dialogues
**Làm gì:** Viết dialogue cho mỗi lesson.
**Skill:** @creative-writing
**Chi tiết:**

1. Mỗi dialogue cần:
   - `setting`: Mô tả nơi diễn ra (cụ thể, có thể visualize)
   - `characters`: 2-3 nhân vật với tên và vai trò
   - `lines`: Các lượt thoại

2. Số lượt thoại theo level:
   - Starters: 4-6 lines
   - Movers: 6-8 lines
   - Flyers: 8-10 lines
   - KET: 10-12 lines
   - PET: 12-16 lines

3. Quy tắc viết dialogue:
   - Nghe tự nhiên — như 2 người thật nói chuyện
   - Dùng contractions (I'm, don't, can't — KHÔNG dùng I am, do not ở level thấp)
   - Tên nhân vật: dùng tên Việt Nam (Ms. Lan, Mr. Minh, Hoa, Nam) để gần gũi
   - Mỗi dialogue phải chứa từ mới + grammar point của lesson
   - Kết thúc tự nhiên (goodbye, see you, thank you)
   - Thêm `note` (stage direction) cho 2-3 dòng quan trọng

4. Đặc biệt cho school topics:
   - Dùng đúng classroom language thực tế
   - Tình huống cụ thể (không generic): "checking homework about English tenses" thay vì "in class"
   - Phản ánh thực tế trường học VN: sĩ số đông, thiếu thiết bị, học sinh rụt rè

**Ví dụ tốt (Starters, topic_giving_instructions):**
```json
{
  "setting": "Classroom, Tuesday afternoon, English practice time",
  "characters": [
    { "id": "teacher", "name": "Ms. Lan", "role": "teacher" },
    { "id": "student", "name": "Nam", "role": "student" }
  ],
  "lines": [
    { "character_id": "teacher", "text": "OK, class. Open your books.", "note": "(holding up the book)" },
    { "character_id": "teacher", "text": "Look at page 5." },
    { "character_id": "student", "text": "Page 5?" },
    { "character_id": "teacher", "text": "Yes, page 5. Read the story." },
    { "character_id": "student", "text": "OK, teacher." },
    { "character_id": "teacher", "text": "Good. You have five minutes.", "note": "(smiling)" }
  ]
}
```

---

### Bước 3: Tạo exercises
**Làm gì:** Tạo 5 exercises cho mỗi lesson (1 mỗi loại).
**Skill:** @curriculum-design
**Chi tiết:**

Mỗi lesson có ĐÚNG 5 exercises, theo thứ tự:

**Exercise 1: match (nối hình-từ)**
- 3-4 items cho Starters/Movers, 4-6 cho Flyers/KET/PET
- Mỗi item: `image_hint` + `correct_answer`
- Image hint phải cụ thể, visualize được
- Dùng từ mới trong lesson

**Exercise 2: arrange (sắp xếp câu)**
- 3-4 items
- Mỗi item: `words` (shuffled) + `correct_answer`
- Câu lấy từ dialogue hoặc biến thể
- Đảm bảo chỉ có 1 cách sắp xếp đúng

**Exercise 3: listen_choose (nghe-chọn)**
- 3-4 items
- Mỗi item: `audio_text` (sẽ convert TTS) + `options` (3 lựa chọn) + `correct_answer`
- Options phải có 1 đúng + 2 sai nhưng hợp lý (không quá dễ đoán)

**Exercise 4: fill_blank (điền từ)**
- 3-4 items
- Mỗi item: `prompt` (câu có 1 chỗ trống ___) + `correct_answer`
- Chỗ trống là từ mới hoặc từ quan trọng trong lesson
- Câu phải cho đủ ngữ cảnh để đoán được đáp án

**Exercise 5: multiple_choice (chọn đáp án)**
- 3-4 items
- Mỗi item: `prompt` (câu hỏi tình huống) + `options` (3 lựa chọn) + `correct_answer`
- Test comprehension, KHÔNG test grammar rule knowledge
- Ví dụ tốt: "Your student got 10/10. What do you say?" → ["Well done!", "I'm sorry.", "Sit down."]
- Ví dụ xấu: "Which tense is used here?" → KHÔNG BAO GIỜ test meta-knowledge

---

### Bước 4: Tạo AI conversation prompts
**Làm gì:** Thiết kế AI conversation scenario cho mỗi lesson.
**Skill:** @curriculum-design
**Chi tiết:**

1. Mỗi lesson có 1 AI conversation setup:
   - `role`: AI đóng vai gì (colleague, student, parent, waiter, doctor, receptionist)
   - `scenario`: Tình huống cụ thể
   - `opening_line`: Câu mở đầu AI nói trước
   - `level_constraints`: Giới hạn AI phải tuân thủ
   - `success_criteria`: Khi nào coi là thành công

2. Level constraints quan trọng:
   - `max_sentence_length`: Starters 6, Movers 8, Flyers 10, KET 12, PET 15
   - `allowed_grammar`: Chỉ grammar IDs ở level hiện tại và các level trước
   - `target_vocabulary`: Từ mà AI nên cố gắng dùng hoặc gợi ra từ learner

3. AI conversation KHÔNG phải free chat. Nó là guided practice với mục tiêu rõ ràng.

---

### Bước 5: Assemble và validate
**Làm gì:** Ghép dialogue + exercises + AI conversation → lesson file hoàn chỉnh.
**Skill:** @json-processing
**Chi tiết:**
1. Gán ID: `{level}_lesson_{3-digit-order}`
2. Validate theo `schemas/lesson.schema.json`
3. Cross-check: tất cả vocabulary_ids và grammar_ids phải tồn tại
4. Output từng file lesson riêng

**Validation cuối mỗi batch:**
- [ ] Tất cả files valid JSON
- [ ] Đúng schema
- [ ] Đủ 5 exercises mỗi lesson (1 mỗi loại)
- [ ] Dialogue lines đúng số lượng theo level
- [ ] vocabulary_ids tồn tại trong vocabulary files
- [ ] grammar_ids tồn tại trong grammar files
- [ ] AI conversation constraints hợp lệ
- [ ] Không có grammar rule explanation nào
- [ ] Tên nhân vật là tên Việt Nam

---

## Quy trình batch

```
Batch 1: Starters lesson-001 → 005
  → Human review
  → Feedback? → Điều chỉnh template
  → OK? → Tiếp

Batch 2: Starters lesson-006 → 030
  → Validate
  → OK? → Tiếp

Batch 3: Movers lesson-001 → 035
  → Validate → Tiếp

Batch 4: Flyers lesson-001 → 040
  → Validate → Tiếp

Batch 5: KET lesson-001 → 035
  → Validate → Tiếp

Batch 6: PET lesson-001 → 040
  → Validate → Hoàn thành
```

---

## Báo cáo khi hoàn thành mỗi batch

```
✅ Agent 4 (Lessons) — Batch {n} hoàn thành
- Level: {level}
- Lessons: {start} → {end} ({count} lessons)
- Dialogues: {n} lines total
- Exercises: {n} items total (match: {n}, arrange: {n}, listen_choose: {n}, fill_blank: {n}, multiple_choice: {n})
- AI conversations: {n} scenarios
- Vocabulary used: {n} unique words / {total} available
- Grammar covered: {n} / {total} points
- Files: tinysteps-data/lessons/{level}/lesson-{start}.json → lesson-{end}.json
- Validation: PASSED / FAILED
```
