# Workflow 03 — Grammar Agent

## Vai trò
Tạo grammar points cho 5 levels. KHÔNG giải thích rules — chỉ cung cấp patterns và nhiều example sentences để learner hấp thụ qua lặp lại.

## Trigger
Human nói: "Tạo grammar data" hoặc "Run Agent 3"

## Prerequisite
- Agent 1 (Vocabulary) hoàn thành → `tinysteps-data/vocabulary/*.json`
- Agent 2 (Topics) hoàn thành → `tinysteps-data/topics/topics.json`

## Skills cần dùng
- @english-linguistics (grammar patterns, common Vietnamese learner mistakes)
- @json-processing (output structured data)

## Input
- `tinysteps-data/vocabulary/*.json`
- `tinysteps-data/topics/topics.json`
- CEFR-SP dataset (câu đã gán nhãn — dùng làm example sentences)
- Cambridge English Grammar Profile (tham khảo grammar point nào thuộc level nào)
- Schema: `schemas/grammar.schema.json`

## Output
- `tinysteps-data/grammar/starters.json`
- `tinysteps-data/grammar/movers.json`
- `tinysteps-data/grammar/flyers.json`
- `tinysteps-data/grammar/ket.json`
- `tinysteps-data/grammar/pet.json`

---

## Các bước thực hiện

### Bước 1: Xác định grammar points cho từng level
**Làm gì:** Liệt kê grammar points cần cover ở mỗi level, dựa trên Cambridge English Grammar Profile.
**Skill:** @english-linguistics
**Chi tiết:**

Tham khảo danh sách sau (điều chỉnh nếu cần):

**Starters (8-10 points):**
- Imperative positive (Open your book.)
- Imperative negative (Don't run.)
- Present simple — be (I am a teacher.)
- Present simple — positive (I like coffee.)
- There is / there are (There is a pen on the desk.)
- This / that / these / those
- Singular/plural nouns
- Basic prepositions: in, on, under, next to
- Question: What is this?
- Question: How many?

**Movers (10-12 points):**
- Present continuous (I am reading.)
- Past simple — regular (I walked to school.)
- Past simple — common irregulars (I went, I saw, I had)
- Can / can't (I can swim.)
- Want to + verb (I want to eat.)
- Like + verb-ing (I like reading.)
- Comparative adjectives (bigger, smaller)
- Possessives (my, your, his, her)
- Question: Where / When / Who
- Conjunctions: and, but, because

**Flyers (10-12 points):**
- Present perfect simple (I have finished.)
- Going to + verb (I'm going to study.)
- Must / mustn't (You must listen.)
- Should / shouldn't (You should try again.)
- Superlative adjectives (the biggest)
- Adverbs of frequency (always, sometimes, never)
- First conditional basic (If it rains, we stay inside.)
- Question: How long / How often
- Reported commands (She told me to sit down.)
- Too + adjective (It's too difficult.)

**KET (10-12 points):**
- Present perfect with for/since
- Past continuous (I was working when...)
- Could (for ability and requests)
- Would like to (I'd like to suggest...)
- Passive voice simple (The report was written.)
- Relative clauses basic (The teacher who...)
- So / such (It was so interesting.)
- Enough + noun / adjective + enough
- Question tags (It's hot, isn't it?)
- Used to (I used to teach math.)

**PET (10-12 points):**
- Second conditional (If I had time, I would...)
- Present perfect continuous (I've been teaching for 10 years.)
- Reported speech (He said that...)
- Passive with modals (It should be done by Friday.)
- Although / however / despite
- Purpose: so that / in order to
- Wish + past simple (I wish I could speak better.)
- Have something done (I had my car fixed.)
- Complex question forms
- Linking words for argument (furthermore, on the other hand)

**Output bước này:** File tạm `_raw/grammar_list.json`

---

### Bước 2: Tạo example sentences cho mỗi grammar point
**Làm gì:** Tạo 5-10 example sentences cho mỗi grammar point. ĐÂY LÀ PHẦN QUAN TRỌNG NHẤT.
**Skill:** @english-linguistics, @json-processing
**Chi tiết:**
1. Với mỗi grammar point, tạo 5-10 example sentences:
   - **Ưu tiên 1:** Lấy từ CEFR-SP dataset (câu đã validate bởi chuyên gia)
   - **Ưu tiên 2:** AI generate câu mới nếu CEFR-SP không đủ
2. Mỗi example phải có:
   - `sentence`: Câu hoàn chỉnh, tự nhiên
   - `context`: Bối cảnh ngắn (ví dụ: "teacher starting class", "ordering coffee")
3. Example sentences phải:
   - CHỈ dùng vocabulary trong level đó (check against vocabulary files)
   - Gắn với 1 trong 12 topics
   - Nghe tự nhiên — như người thật nói, KHÔNG như textbook
   - Đa dạng contexts (trộn school + daily_life)

**Ví dụ tốt vs xấu:**
```
Tốt: "Open your book to page 10." (context: teacher starting lesson)
Xấu: "The imperative form is used for commands." (giải thích rule — TUYỆT ĐỐI KHÔNG)

Tốt: "I went to the market yesterday." (context: telling a colleague about weekend)
Xấu: "Subject + past tense verb + object." (formula — KHÔNG)
```

4. Gán `topic_ids` cho mỗi grammar point dựa trên contexts của examples

**Output bước này:** File tạm `_raw/grammar_with_examples.json`

**Validation:**
- Mỗi grammar point có 5-10 examples
- Examples chỉ dùng từ trong level
- Không có rule explanation nào
- Context đa dạng (không lặp)

---

### Bước 3: Thêm common mistakes
**Làm gì:** Thêm 2-3 common mistakes mà người Việt hay mắc cho mỗi grammar point.
**Skill:** @english-linguistics
**Chi tiết:**
1. Với mỗi grammar point, thêm 2-3 pairs `wrong` / `correct`
2. Tập trung vào lỗi đặc thù người Việt:
   - Thiếu "s" ở ngôi 3 số ít (He go → He goes)
   - Thiếu "to be" (I teacher → I am a teacher)
   - Sai word order (I very like → I really like / I like ... very much)
   - Thiếu articles (I am teacher → I am a teacher)
   - Nhầm tenses (Yesterday I go → Yesterday I went)
   - Dùng "have" thay "there is" (Have a pen on the desk → There is a pen)
   - Thiếu subject (Is very hot → It is very hot)
3. Thêm `builds_on` nếu grammar point này mở rộng từ level trước

**Output bước này:** Cập nhật vào `_raw/grammar_with_examples.json`

---

### Bước 4: Gán ID, validate, output
**Làm gì:** Gán ID, validate schema, output 5 files.
**Skill:** @json-processing
**Chi tiết:**
1. Gán ID format: `{level}_grammar_{3-digit-number}`
2. Validate toàn bộ theo `schemas/grammar.schema.json`
3. Cập nhật `grammar_ids` trong `tinysteps-data/topics/topics.json` (fill vào spiral entries)
4. Output 5 files

**Output cuối cùng:**
```
tinysteps-data/grammar/starters.json
tinysteps-data/grammar/movers.json
tinysteps-data/grammar/flyers.json
tinysteps-data/grammar/ket.json
tinysteps-data/grammar/pet.json
```

**Cập nhật:**
```
tinysteps-data/topics/topics.json (thêm grammar_ids vào spiral entries)
```

**Validation cuối:**
- [ ] 5 files valid JSON
- [ ] Đúng schema
- [ ] ~50 grammar points tổng cộng (8-12 mỗi level)
- [ ] Mỗi point có 5-10 example sentences
- [ ] Mỗi point có 2-3 common mistakes
- [ ] KHÔNG có rule explanation nào trong data
- [ ] Examples chỉ dùng vocab trong level
- [ ] grammar_ids đã cập nhật trong topics.json
- [ ] builds_on links hợp lệ (ID tồn tại ở level trước)

---

## Báo cáo khi hoàn thành

```
✅ Agent 3 (Grammar) hoàn thành
- Starters: {n} grammar points, {n} examples
- Movers: {n} grammar points, {n} examples
- Flyers: {n} grammar points, {n} examples
- KET: {n} grammar points, {n} examples
- PET: {n} grammar points, {n} examples
- Tổng: {n} grammar points, {n} example sentences
- Common mistakes: {n} pairs
- Nguồn examples: CEFR-SP {x}%, AI generated {y}%
- Files: tinysteps-data/grammar/*.json
- Updated: tinysteps-data/topics/topics.json
- Validation: PASSED / FAILED
```
