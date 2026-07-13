# Workflow 02 — Topics Agent

## Vai trò
Tổ chức 12 modules (topics), map vocabulary vào từng topic, và thiết kế spiral progression across 5 levels.

## Trigger
Human nói: "Tạo topics data" hoặc "Run Agent 2"

## Prerequisite
Agent 1 (Vocabulary) đã hoàn thành. Files `tinysteps-data/vocabulary/*.json` phải tồn tại.

## Skills cần dùng
- @json-processing (đọc vocabulary, output topics)
- @curriculum-design (spiral progression, CEFR alignment)

## Input
- `tinysteps-data/vocabulary/*.json` (output từ Agent 1)
- Schema: `schemas/topic.schema.json`
- Rules: `RULES.md`
- 12 modules đã quy định trong `PROJECT_SPEC.md`

## Output
- `tinysteps-data/topics/topics.json`

---

## Các bước thực hiện

### Bước 1: Tạo khung 12 topics
**Làm gì:** Tạo skeleton cho 12 topics với metadata cơ bản.
**Skill:** @json-processing
**Chi tiết:**
1. Tạo 12 topic entries theo danh sách sau:

**Nhóm school (group_id: "school"):**

| ID | Name | Description |
|----|------|-------------|
| topic_before_class | Before class | Preparing for lessons, morning routines at school, greeting colleagues |
| topic_in_class | In class | Managing activities, interacting with students during lessons |
| topic_giving_instructions | Giving instructions | Telling students what to do, explaining tasks and activities |
| topic_checking_understanding | Checking understanding | Asking if students understand, confirming comprehension |
| topic_praise_correction | Praise & correction | Encouraging students, correcting mistakes positively |
| topic_school_communication | School communication | Parent meetings, emails, colleague discussions, reports |

**Nhóm daily_life (group_id: "daily_life"):**

| ID | Name | Description |
|----|------|-------------|
| topic_market | At the market | Shopping for food and goods, asking prices, bargaining |
| topic_restaurant | At a restaurant | Ordering food, asking for menu, paying the bill |
| topic_travel | Travel & directions | Asking for directions, booking tickets, at the airport/hotel |
| topic_phone | Phone calls | Making and receiving phone calls, leaving messages |
| topic_health | Health & doctor | Describing symptoms, visiting a doctor, buying medicine |
| topic_social | Social conversations | Greetings, small talk, introductions, weather, hobbies |

2. Cho mỗi topic, tạo `spiral` array rỗng (sẽ fill ở bước tiếp)

**Output bước này:** File tạm `_raw/topics_skeleton.json`

---

### Bước 2: Map vocabulary vào topics
**Làm gì:** Đọc tất cả vocabulary files, phân loại từng từ vào 1 hoặc nhiều topics.
**Skill:** @json-processing, @english-linguistics
**Chi tiết:**
1. Đọc 5 files vocabulary (starters → pet)
2. Với mỗi từ, xác định topic phù hợp dựa trên:
   - `topic_ids` đã gán tạm bởi Agent 1 (tham khảo)
   - Semantic meaning của từ
   - Bối cảnh trong `example_sentence`
3. Một từ có thể thuộc nhiều topics (ví dụ: "please" thuộc hầu hết topics)
4. Đảm bảo mỗi topic ở mỗi level có ít nhất 10 từ vựng
5. Cập nhật ngược lại `topic_ids` trong vocabulary files nếu cần

**Quy tắc phân loại:**
- Từ liên quan đến lớp học (book, pen, homework, exam) → school topics
- Từ liên quan đến ăn uống (rice, chicken, water, menu) → topic_restaurant hoặc topic_market
- Từ chung (hello, please, thank you, yes, no) → có thể thuộc nhiều topics
- Nếu không rõ → gán vào topic_social (catch-all)

**Output bước này:** File tạm `_raw/topics_with_vocab.json`

**Validation:**
- Mỗi từ vựng phải thuộc ít nhất 1 topic
- Mỗi topic ở mỗi level có ≥ 10 từ
- Không có topic nào trống ở bất kỳ level nào

---

### Bước 3: Thiết kế spiral progression
**Làm gì:** Cho mỗi topic, mô tả nó evolve như thế nào qua 5 levels.
**Skill:** @curriculum-design
**Chi tiết:**
1. Với mỗi topic × mỗi level, tạo spiral entry gồm:
   - `focus`: Khía cạnh nào của topic được cover ở level này
   - `can_do_statement`: Learner có thể làm gì sau khi hoàn thành
   - `example_sentences`: 3-5 câu ví dụ thể hiện complexity ở level này
   - `vocabulary_ids`: Danh sách từ vựng thuộc topic này ở level này
   - `grammar_ids`: Để trống (Agent 3 sẽ fill)

2. Đảm bảo spiral tăng dần rõ ràng:

**Ví dụ mẫu cho topic_restaurant:**
```
Starters:
  focus: "Food names and basic preferences"
  can_do: "Can name common foods and say what they like"
  examples: ["I like rice.", "This is water.", "Chicken, please."]

Movers:
  focus: "Ordering simple items"
  can_do: "Can order food and drinks using simple phrases"
  examples: ["Can I have some water?", "I want chicken and rice.", "How much is it?"]

Flyers:
  focus: "Full restaurant interactions"
  can_do: "Can have a simple conversation with a waiter"
  examples: ["Could I see the menu, please?", "I'd like the grilled fish.", "Can we have the bill?"]

KET:
  focus: "Preferences, complaints, and special requests"
  can_do: "Can express preferences, make special requests, and handle problems"
  examples: ["I'd prefer a table by the window.", "This isn't what I ordered.", "Could you recommend something?"]

PET:
  focus: "Detailed descriptions and reviews"
  can_do: "Can describe food, give opinions, and discuss dietary needs"
  examples: ["The chicken was delicious but a bit too salty.", "I'm vegetarian — do you have any options?", "I'd recommend the seafood pasta."]
```

3. Áp dụng pattern tương tự cho 11 topics còn lại

**Lưu ý:**
- Can-do statements phải realistic cho giáo viên VN
- Example sentences phải CHỈ dùng từ trong level đó
- School topics nên có examples sát thực tế trường học VN

**Output bước này:** Cập nhật vào `_raw/topics_with_vocab.json`

---

### Bước 4: Validate và output
**Làm gì:** Validate toàn bộ, format theo schema, output file cuối cùng.
**Skill:** @json-processing
**Chi tiết:**
1. Validate theo `schemas/topic.schema.json`
2. Cross-check vocabulary_ids — tất cả phải tồn tại trong vocabulary files
3. Đảm bảo đủ 12 topics × 5 levels = 60 spiral entries
4. Output file cuối: `tinysteps-data/topics/topics.json`

**Output cuối cùng:**
```
tinysteps-data/topics/topics.json
```

**Validation cuối:**
- [ ] File valid JSON
- [ ] Đúng schema
- [ ] 12 topics, 2 groups (6+6)
- [ ] 60 spiral entries (12 × 5)
- [ ] Tất cả vocabulary_ids tồn tại trong vocabulary files
- [ ] Mỗi topic/level có ≥ 10 vocabulary items
- [ ] Can-do statements rõ ràng và realistic
- [ ] Example sentences đúng level

---

## Báo cáo khi hoàn thành

```
✅ Agent 2 (Topics) hoàn thành
- Topics: 12 (school: 6, daily_life: 6)
- Spiral entries: 60
- Vocabulary coverage: {n}% từ đã được gán topic
- Files: tinysteps-data/topics/topics.json
- Validation: PASSED / FAILED (chi tiết)
```
