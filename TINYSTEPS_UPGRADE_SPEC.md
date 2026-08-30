# TinySteps — Upgrade Spec v2

> Tài liệu duy nhất cho AI coding agent (Claude Code / Cursor / Grok).
> Đọc HẾT trước khi code. Làm đúng thứ tự Phase 1 → 2 → 3 → 4.

---

## 0. BỐI CẢNH

### Sản phẩm là gì

TinySteps là web app học tiếng Anh dành cho **giáo viên các môn khác** (Toán, Hóa, Sinh...) tại Việt Nam — những người có trình độ tiếng Anh từ zero đến bập bõm. Mục tiêu không phải "dạy tiếng Anh thành thạo" mà là **xây nền tảng kiên trì** — giúp giáo viên không sợ tiếng Anh, quay lại mỗi ngày, leo dốc nhẹ đến mức không nhận ra mình đang khó lên.

### Triết lý thiết kế — KHÔNG ĐƯỢC vi phạm

1. **Content giữ 100% tiếng Anh.** Không thêm nghĩa tiếng Việt vào exercises, dialogues, vocabulary. UI chrome (`labels.ts`) vẫn tiếng Việt.
2. **Bắt đầu dễ đến mức không thể từ chối.** Bài đầu tiên hoàn thành trong 2–4 phút.
3. **Grammar nhúng trong bối cảnh, không dạy trực tiếp.** Không hiện "Bài này dạy Present Simple".
4. **Spiral progression.** Cùng topic quay lại nhiều lần, phức tạp dần qua 5 levels.
5. **Mỗi bài có bối cảnh thực.** Không drill từ lẻ. Luôn có tình huống cụ thể.
6. **"Câu mang vào lớp"** — mỗi bài kết thúc bằng 3–5 câu thực chiến giáo viên dùng được ngay.

### Hiện trạng

- **175 bài học** (30 Starters + 30 Movers + 40 Flyers + 35 KET + 40 PET)
- **2100 từ vựng**, 57 grammar points, 12 topics
- **~6126 audio files**, ~525 illustrations
- **App stack:** Next.js App Router + TypeScript + Tailwind + Supabase + ts-fsrs
- **Paywall:** 3 bài free (`starters_lesson_001..003`), còn lại trả phí
- **Đang chạy production** tại `tinysteps.xuyenlab.com`

### 3 vấn đề cần sửa (ưu tiên từ cao xuống thấp)

| # | Vấn đề | Ảnh hưởng |
|---|--------|-----------|
| 1 | **CEFR misalignment** — dialogue chứa grammar vượt level (VD: Flyers dùng second conditional, present perfect continuous) | Phá vỡ "leo dốc nhẹ". Người học thấy khó đột ngột → bỏ cuộc |
| 2 | **Exercise lặp/nhàm** — fill_blank cùng đáp án, match dùng image_hint vô nghĩa cho từ trừu tượng | Không kích thích ghi nhớ. Giáo viên tiếng Anh đánh giá thấp |
| 3 | **Flow thiếu bước Say + Takeaway** — dialogue → quiz → điểm, không có luyện nói hay câu mang về | Thiếu output practice và practical value cho mỗi bài |

---

## 1. KIẾN TRÚC NÂNG CẤP

### Nguyên tắc bất di bất dịch

```
✅ Giữ: 175 lesson IDs, paywall logic, SRS, VietQR, audio contract cũ, marketing pages
✅ Giữ: Stack (Next.js, TypeScript strict, Tailwind, Zod, Vitest, Supabase)
✅ Giữ: prepare-content.mjs pipeline (JSON → generated index → app)
✅ Giữ: English-only content, Vietnamese-only UI chrome

❌ Không: thêm nghĩa tiếng Việt vào exercises/dialogues
❌ Không: đổi lesson id format
❌ Không: implement Web Speech / chấm phát âm
❌ Không: thêm dependency mới trừ khi thật sự cần
❌ Không: đụng supabase migrations, admin pages
```

### 4 Phases

```
Phase 1 — CEFR Audit (Python scripts, sửa JSON)         ← SỬA NỀN TẢNG
Phase 2 — Exercise Quality Fix (Python scripts, sửa JSON) ← SỬA NỘI DUNG
Phase 3 — App: Station Model (TypeScript, sửa components) ← CẢI TIẾN UX
Phase 4 — Rewrite 3 Free Lessons (JSON + components)      ← SHOWCASE
```

**Phase 1 + 2 chỉ đụng `tinysteps-data/`. Phase 3 + 4 đụng `tinysteps-app/`.** Không trộn.

---

## Phase 1 — CEFR AUDIT + FIX

### Mục tiêu

Đảm bảo mọi dialogue line trong 175 bài **chỉ dùng grammar structures thuộc level đó hoặc thấp hơn**. Đây là vấn đề nghiêm trọng nhất vì phá vỡ lời hứa cốt lõi của sản phẩm.

### 1.1 CEFR Grammar Constraint Map

Mỗi level chỉ được dùng grammar CỦA level đó + TẤT CẢ levels thấp hơn.

```python
GRAMMAR_BY_LEVEL = {
    "starters": {
        "imperative_positive",        # Verb + (object)
        "imperative_negative",        # Don't + Verb
        "present_simple_be",          # am/is/are + noun/adj
        "present_simple_positive",    # Subject + Verb + (object)
        "there_is_there_are",         # There is/are + noun
        "this_that_these_those",      # This/That is | These/Those are
        "singular_plural",            # noun + -s/-es
        "basic_prepositions",         # in/on/under/next to
        "question_what",              # What is/are...? What do/does...?
        "question_how_many",          # How many...?
        "present_simple_negative",    # do/does not + Verb
        "present_simple_questions",   # Do/Does + subject + Verb?
    },
    "movers": {
        "present_continuous",         # am/is/are + Verb-ing
        "past_simple_regular",        # Verb-ed
        "past_simple_irregular",      # Verb-2 (went, saw, etc.)
        "can_cant",                   # can/can't + Verb
        "want_to_verb",              # want/wants + to + Verb
        "like_verb_ing",             # like/likes + Verb-ing
        "comparative_adjectives",     # -er than / more...than
        "possessives",               # my/your/his/her/our/their
        "question_where_when_who",   # Where/When/Who + aux + S + V?
        "conjunctions_and_but_because", # and/but/because
        "past_simple_be",            # was/were
        "past_simple_negative",      # did not + Verb
        "past_simple_questions",     # Did + S + Verb?
    },
    "flyers": {
        "present_perfect_simple",    # have/has + V-ed/3
        "going_to_verb",             # going to + Verb
        "must_mustnt",               # must/mustn't + Verb
        "should_shouldnt",           # should/shouldn't + Verb
        "reported_commands",         # told + object + to + Verb
        "superlative_adjectives",    # the -est / the most
        "adverbs_of_frequency",      # always/usually/often/sometimes/never
        "first_conditional",         # If + present simple, will + verb
        "question_how_long_often",   # How long/often + aux + S + V?
        "too_adjective",             # too + adjective (+ to + verb)
    },
    "ket": {
        "present_perfect_for_since", # have/has + V-ed/3 + for/since
        "could_requests",            # Could + S + V?
        "would_like_to",             # would like + to + V
        "used_to",                   # used to + V
        "relative_clauses_basic",    # who/which + V/clause
        "past_continuous",           # was/were + V-ing
        "passive_voice_simple",      # was/were + V-ed/3
        "so_such",                   # so + adj | such + noun
        "enough",                    # adj + enough | enough + noun
        "question_tags",             # ..., isn't it?
    },
    "pet": {
        "second_conditional",         # If + past simple, would + V
        "present_perfect_continuous", # have/has been + V-ing
        "wish_past_simple",          # wish + past simple
        "reported_speech",           # said (that) + backshifted
        "passive_with_modals",       # modal + be + V-ed/3
        "although_however_despite",  # Although/However/Despite
        "purpose_so_that",           # so that / in order to
        "have_something_done",       # have + object + past participle
        "complex_questions",         # Do you know / Could you tell me + wh-
        "linking_words",             # Furthermore/Moreover/Nevertheless
    },
}

def allowed_grammar(level: str) -> set:
    """Trả về tất cả grammar structures mà level này ĐƯỢC PHÉP dùng."""
    order = ["starters", "movers", "flyers", "ket", "pet"]
    idx = order.index(level)
    result = set()
    for i in range(idx + 1):
        result |= GRAMMAR_BY_LEVEL[order[i]]
    return result
```

### 1.2 Grammar Detection Patterns

Để detect grammar structures trong một câu dialogue, dùng regex/keyword matching:

```python
GRAMMAR_DETECTORS = {
    # PET-only
    "second_conditional": r"\bif\b.*\b(would|wouldn't)\b|\bwould\b.*\bif\b",
    "present_perfect_continuous": r"\b(have|has)\s+been\s+\w+ing\b",
    "wish_past_simple": r"\bwish(es|ed)?\b.*\b(was|were|had|could|knew)\b",
    "reported_speech": r"\bsaid\s+(that\s+)?\w+\s+(was|were|had|would|could)\b",
    "passive_with_modals": r"\b(must|should|can|could|may|might|will|would)\s+be\s+\w+(ed|en|t)\b",
    "although_however_despite": r"\b(although|however|despite|nevertheless|moreover|furthermore)\b",
    "purpose_so_that": r"\bso\s+that\b|\bin\s+order\s+to\b",
    "have_something_done": r"\b(have|has|had)\s+\w+\s+(repaired|fixed|done|made|built|cleaned|checked|delivered)\b",

    # KET-only (not in Flyers)
    "present_perfect_for_since": r"\b(have|has)\s+\w+(ed|en|t)\b.*\b(for|since)\b",
    "could_requests": r"\bcould\s+(you|i|we)\b",
    "would_like_to": r"\b(would\s+like|'d\s+like)\s+to\b",
    "used_to": r"\bused\s+to\s+\w+",
    "past_continuous": r"\b(was|were)\s+\w+ing\b",
    "passive_voice_simple": r"\b(was|were)\s+\w+(ed|en|t)\b(?!\s+to\b)",
    "question_tags": r",\s*(isn't|aren't|wasn't|weren't|don't|doesn't|didn't|won't|can't|hasn't|haven't)\s+(it|he|she|they|we|you)\s*\?",

    # Flyers-only (not in Movers)
    "present_perfect_simple": r"\b(have|has)\s+\w+(ed|en|t)\b",
    "going_to_verb": r"\b(going\s+to|gonna)\s+\w+",
    "must_mustnt": r"\b(must|mustn't)\b",
    "should_shouldnt": r"\b(should|shouldn't)\b",
    "first_conditional": r"\bif\b.*\bwill\b|\bwill\b.*\bif\b",

    # Movers-only (not in Starters)
    "present_continuous": r"\b(am|is|are)\s+\w+ing\b",
    "past_simple_regular": r"\b\w+ed\b",  # broad — refine with word list
    "past_simple_irregular": r"\b(went|saw|came|took|gave|made|got|said|told|thought|knew|found|left|felt|became|brought|kept|began|ran|wrote|sat|stood|lost|paid|met|set|put|read|grew|drew|spoke|broke|chose|fell|held|built|sent|spent|bought|caught|taught|fought|heard|hung|led|meant|shot|showed|shut|woke|wore|won|drove|ate|drank|sang|swam|threw|blew|flew|forgot|hid|rode|shook|stole|woke)\b",
    "can_cant": r"\b(can|can't|cannot)\b",
    "comparative_adjectives": r"\b\w+(er|ier)\s+than\b|\bmore\s+\w+\s+than\b",
    "past_simple_be": r"\b(was|were)\b",
}
```

**Lưu ý:** Regex không hoàn hảo. Nhiều pattern overlap (VD: "was" có thể là past_simple_be hoặc passive_voice_simple). Script nên flag và output cho human review, KHÔNG tự động rewrite. Output format: CSV hoặc JSON report.

### 1.3 Script: `audit_cefr_alignment.py`

Tạo file: `tinysteps-data/audit_cefr_alignment.py`

```
Input:  tinysteps-data/lessons/{level}/lesson-*.json
        tinysteps-data/grammar/{level}.json
Output: tinysteps-data/reports/cefr_audit_report.json
```

Logic:

```python
for each lesson in all 175 lessons:
    level = lesson["level"]
    allowed = allowed_grammar(level)

    for each line in lesson["dialogue"]["lines"]:
        detected = detect_grammar_structures(line["text"])
        violations = detected - allowed
        if violations:
            report.append({
                "lesson_id": lesson["id"],
                "level": level,
                "line_text": line["text"],
                "violations": list(violations),
                "detected_all": list(detected),
            })

    # Cũng kiểm tra exercise sentences
    for each exercise in lesson["exercises"]:
        if exercise["type"] == "arrange":
            for item in exercise["items"]:
                detected = detect_grammar_structures(item["correct_answer"])
                violations = detected - allowed
                # flag nếu có violation

        if exercise["type"] in ["listen_choose", "fill_blank"]:
            for item in exercise["items"]:
                text = item.get("audio_text") or item.get("prompt", "")
                detected = detect_grammar_structures(text)
                violations = detected - allowed
                # flag nếu có violation
```

Output report format:

```json
{
  "total_lessons": 175,
  "lessons_with_violations": 47,
  "violations": [
    {
      "lesson_id": "flyers_lesson_002",
      "level": "flyers",
      "location": "dialogue.lines[5]",
      "text": "I would if I had more free time after school.",
      "violations": ["second_conditional"],
      "severity": "high"
    }
  ],
  "summary_by_level": {
    "starters": {"total": 30, "violations": 3},
    "movers": {"total": 30, "violations": 8},
    "flyers": {"total": 40, "violations": 15},
    "ket": {"total": 35, "violations": 12},
    "pet": {"total": 40, "violations": 9}
  }
}
```

### 1.4 Script: `fix_cefr_violations.py`

Tạo file: `tinysteps-data/fix_cefr_violations.py`

Sau khi audit report được human review và confirm:

```
Input:  tinysteps-data/reports/cefr_audit_report.json (reviewed)
        tinysteps-data/lessons/{level}/lesson-*.json
Output: tinysteps-data/lessons/{level}/lesson-*.json (modified in-place)
        tinysteps-data/reports/cefr_fix_log.json
```

Logic cho mỗi violation:

1. **Dialogue line rewrite:** Viết lại câu dùng CHỈ grammar structures trong `allowed_grammar(level)`. Giữ nguyên ý nghĩa, giữ nguyên character_id, giữ nguyên setting.

2. **Constraint khi rewrite:**
   - Starters: max 6 words/sentence
   - Movers: max 8 words/sentence
   - Flyers: max 10 words/sentence
   - KET: max 14 words/sentence
   - PET: max 18 words/sentence

3. **Giữ nguyên số dòng dialogue** (để không phải regenerate audio). Nếu không thể fix mà giữ số dòng → flag "needs_manual_review".

4. **Exercise items:** Nếu arrange `correct_answer` hoặc fill_blank `prompt` chứa violation → rewrite tương tự.

**QUAN TRỌNG:** Script này CÓ THỂ dùng AI API (Gemini/Claude) để rewrite, nhưng output phải qua validation check: rewritten text phải pass CEFR audit (chạy lại detector trên text mới).

### 1.5 Acceptance Criteria Phase 1

```bash
# Chạy audit
cd tinysteps-data
python3 audit_cefr_alignment.py

# Xác nhận report tồn tại
cat reports/cefr_audit_report.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'Lessons with violations: {d[\"lessons_with_violations\"]}')
for level, info in d['summary_by_level'].items():
    print(f'  {level}: {info[\"violations\"]} violations / {info[\"total\"]} lessons')
"

# Sau khi fix:
python3 audit_cefr_alignment.py  # phải ra 0 violations
python3 validate_data.py          # existing validator vẫn pass
```

---

## Phase 2 — EXERCISE QUALITY FIX

### Mục tiêu

Sửa 3 loại lỗi chất lượng trong exercises mà không đổi exercise types hay app code.

### 2.1 Script: `audit_exercise_quality.py`

Tạo file: `tinysteps-data/audit_exercise_quality.py`

**Check 1: Fill-blank repetitive answers**

```python
for each lesson:
    for each exercise where type == "fill_blank":
        answers = [item["correct_answer"] for item in exercise["items"]]
        unique = set(answers)
        if len(unique) == 1 and len(answers) >= 3:
            flag("REPETITIVE", lesson_id, exercise_index,
                 f"All {len(answers)} items have same answer: '{answers[0]}'")
        elif len(unique) / len(answers) < 0.5:
            flag("LOW_VARIETY", lesson_id, exercise_index,
                 f"{len(answers)} items but only {len(unique)} unique answers")
```

**Check 2: Image hint quality for abstract words**

```python
# Words that cannot be meaningfully illustrated with a single image
ABSTRACT_WORDS = {
    "should", "must", "can", "could", "would", "might", "may",
    "attention", "procedure", "permission", "ability", "opinion",
    "experience", "knowledge", "understanding", "communication",
    "although", "however", "despite", "furthermore", "nevertheless",
    "enough", "already", "yet", "since", "recently",
}

for each lesson:
    for each exercise where type in ("match", "multiple_choice"):
        for each item:
            if item.get("correct_answer", "").lower() in ABSTRACT_WORDS:
                flag("ABSTRACT_IMAGE", lesson_id, exercise_index,
                     f"Image hint for abstract word '{item['correct_answer']}': "
                     f"'{item.get('image_hint', '')}'")

            # Also check for broken grammar in image_hint
            hint = item.get("image_hint", "")
            if re.search(r"\ba\s+[aeiou]", hint):  # "a attention"
                flag("HINT_GRAMMAR", lesson_id, exercise_index,
                     f"Grammar error in image_hint: '{hint}'")
            if re.search(r"showing a person to \w+", hint):  # "showing a person to should"
                flag("HINT_NONSENSE", lesson_id, exercise_index,
                     f"Nonsensical image_hint: '{hint}'")
```

**Check 3: Grammar-exercise alignment**

```python
for each lesson:
    claimed_grammar = set(lesson["grammar_ids"])
    practiced_grammar = set()

    for each exercise in lesson["exercises"]:
        # Detect which grammar patterns the exercise items actually practice
        for item in exercise.get("items", []):
            text = (item.get("correct_answer", "") + " " +
                    item.get("prompt", "") + " " +
                    item.get("audio_text", ""))
            detected = detect_grammar_structures(text)
            practiced_grammar |= detected

    claimed_not_practiced = claimed_grammar - practiced_grammar
    if claimed_not_practiced:
        flag("GRAMMAR_MISMATCH", lesson_id,
             f"Grammar claimed but not practiced: "
             f"{[grammar_id_to_name(g) for g in claimed_not_practiced]}")
```

**Check 4: AI conversation duplication across levels**

```python
conversations = {}  # key: (opening_line, scenario) → list of lesson_ids

for each lesson:
    ai = lesson.get("ai_conversation", {})
    key = (ai.get("opening_line", ""), ai.get("scenario", ""))
    conversations.setdefault(key, []).append(lesson["id"])

for key, lesson_ids in conversations.items():
    if len(lesson_ids) > 1:
        levels = set(get_level(lid) for lid in lesson_ids)
        if len(levels) > 1:  # same text across DIFFERENT levels
            flag("AI_CONV_DUPLICATE", lesson_ids,
                 f"Same opening_line across levels: {levels}")
```

Output: `tinysteps-data/reports/exercise_quality_report.json`

### 2.2 Script: `fix_exercise_quality.py`

Tạo file: `tinysteps-data/fix_exercise_quality.py`

Fixes cho từng loại lỗi:

**Fix REPETITIVE fill_blank:**
- Lấy grammar patterns của lesson → tạo items test các aspects khác nhau của cùng pattern
- VD: passive_with_modals → thay vì 3x "be", tạo items test modal (must/should/can), agent (by...), và past participle

**Fix ABSTRACT_IMAGE match/MC at KET/PET:**
- Đối với lessons ở KET + PET: chuyển match items có abstract words sang dạng **sentence context matching**
- Thay `image_hint` + `correct_answer` (single word) bằng `prompt` (sentence with gap) + `correct_answer` (word fits the gap)
- VD: thay vì hình → "procedure", đổi thành `"The school safety ___ must be followed."` → `"procedure"`
- **Không đổi exercise type name.** Vẫn là "match" nhưng items dùng `prompt` thay vì `image_hint` khi `correct_answer` là abstract word. App code render đã handle cả hai cases (check `match-exercise.tsx`).

**Fix HINT_GRAMMAR / HINT_NONSENSE:**
- Rewrite image_hint cho đúng ngữ pháp và có nghĩa
- VD: `"a clean graphic illustration of a attention"` → `"a student paying close attention to the teacher"`
- VD: `"an action illustration showing a person to should"` → remove item, thay bằng concrete word

**Fix AI_CONV_DUPLICATE:**
- Với mỗi nhóm trùng: giữ bản ở level thấp nhất, rewrite bản ở levels cao hơn
- Level cao hơn nên có opening_line phức tạp hơn, scenario cụ thể hơn

### 2.3 Acceptance Criteria Phase 2

```bash
cd tinysteps-data

# Audit
python3 audit_exercise_quality.py

# Sau khi fix:
python3 audit_exercise_quality.py    # 0 flags
python3 audit_cefr_alignment.py      # vẫn 0 violations (fix không tạo violation mới)
python3 validate_data.py             # existing validator vẫn pass

# Rebuild app content index
cd ../tinysteps-app
node scripts/prepare-content.mjs     # phải pass (đúng số bài mỗi level)
npx tsc --noEmit                     # TypeScript clean
npm test                             # existing tests pass
```

---

## Phase 3 — APP: STATION MODEL

### Mục tiêu

Thêm bước Say + Takeaway vào lesson flow. 175 bài hiện tại tự động có 4 stations mà không cần đổi JSON.

### 3.1 Labels

File: `tinysteps-app/lib/i18n/labels.ts`

Thêm:

```typescript
// Station labels
NOI_THEO: "Nói theo",
TOI_DA_NOI: "Tôi đã nói",
BO_QUA_NOI: "Bỏ qua",
CAU_MANG_DI: "Câu mang vào lớp",
NGHE_LAI_CAU: "Nghe lại",
TIEP_THEO_NOI: "Tiếp: nói theo",
TIEP_THEO_LUYEN: "Tiếp: luyện tập",

// Dashboard
XEM_LO_TRINH: "Xem cả lộ trình",
AN_LO_TRINH: "Thu gọn",

// Error
LUU_LOI: "Không lưu được điểm. Thử lại.",

// Tab states
SAP_RA_MAT: "Sắp có",
```

### 3.2 Station Helper

Tạo file: `tinysteps-app/lib/lesson/stations.ts`

```typescript
import type { Lesson } from "@/lib/types/content-types";

export type StationId = "look" | "say" | "practice" | "takeaway";

/**
 * Returns station sequence for a lesson.
 * v1 lessons (no schema_version) get the default 4 stations.
 * v2 lessons can customize via `stations` field.
 */
export function stationsFor(lesson: Lesson): StationId[] {
  const raw = lesson as Record<string, unknown>;
  if (
    raw.schema_version === 2 &&
    Array.isArray(raw.stations) &&
    raw.stations.length > 0
  ) {
    return raw.stations as StationId[];
  }
  return ["look", "say", "practice", "takeaway"];
}

/**
 * Returns takeaway lines for end-of-lesson display.
 * v2 lessons have curated `takeaway_lines`.
 * v1 lessons use the first 4 dialogue lines (practical fallback).
 */
export function takeawayLines(lesson: Lesson): string[] {
  const raw = lesson as Record<string, unknown>;
  if (Array.isArray(raw.takeaway_lines) && raw.takeaway_lines.length > 0) {
    return raw.takeaway_lines as string[];
  }
  // For v1: pick lines that look like commands/instructions, not greetings
  // Fallback: first 4 lines
  return lesson.dialogue.lines.slice(0, 4).map((line) => line.text);
}
```

Unit test: `tinysteps-app/lib/lesson/__tests__/stations.test.ts`

```typescript
import { stationsFor, takeawayLines } from "../stations";

// Fixture: minimal v1 lesson (no schema_version)
const v1Lesson = {
  id: "starters_lesson_001",
  level: "starters",
  dialogue: {
    lines: [
      { character_id: "a", text: "Good morning!" },
      { character_id: "b", text: "Open your book." },
      { character_id: "a", text: "Sit down, please." },
      { character_id: "b", text: "Yes, teacher." },
    ],
  },
  exercises: [],
} as any;

// Fixture: v2 lesson with custom stations
const v2Lesson = {
  ...v1Lesson,
  schema_version: 2,
  stations: ["look", "practice", "takeaway"],
  takeaway_lines: ["Sit down, please.", "Open your book."],
} as any;

test("v1 lesson gets default 4 stations", () => {
  expect(stationsFor(v1Lesson)).toEqual(["look", "say", "practice", "takeaway"]);
});

test("v2 lesson uses custom stations", () => {
  expect(stationsFor(v2Lesson)).toEqual(["look", "practice", "takeaway"]);
});

test("v1 takeaway uses first 4 dialogue lines", () => {
  expect(takeawayLines(v1Lesson)).toEqual([
    "Good morning!",
    "Open your book.",
    "Sit down, please.",
    "Yes, teacher.",
  ]);
});

test("v2 takeaway uses curated lines", () => {
  expect(takeawayLines(v2Lesson)).toEqual([
    "Sit down, please.",
    "Open your book.",
  ]);
});
```

### 3.3 SayStation Component

Tạo file: `tinysteps-app/components/lesson/say-station.tsx`

```
Props:
  dialogue: Lesson["dialogue"]
  audioUrls: Record<string, string | null>
  onComplete: () => void

Behavior:
  - Hiển thị từng dialogue line lần lượt (không phải tất cả cùng lúc)
  - Mỗi line hiện: text tiếng Anh + nút AudioButton (play audio line_NN)
  - Nút chính: labels.TOI_DA_NOI → chuyển sang line tiếp
  - Line cuối → gọi onComplete()
  - Nút phụ (text nhỏ, dưới nút chính): labels.BO_QUA_NOI → gọi onComplete()
    (Giáo viên U50 có thể không muốn nói thành tiếng, đặc biệt ở nơi đông người)
  - KHÔNG có mic, KHÔNG chấm đúng/sai
  - Animation: fade-in mỗi line mới
```

### 3.4 TakeawayStation Component

Tạo file: `tinysteps-app/components/lesson/takeaway-station.tsx`

```
Props:
  lines: string[]           — từ takeawayLines(lesson)
  audioUrls: Record<string, string | null>
  score: number             — % đúng
  correctCount: number
  totalItems: number
  onReplay: () => void
  listHref: string          — link về danh sách bài

Behavior:
  - Headline: labels.CAU_MANG_DI (KHÔNG dùng "Cố gắng thêm" hay emoji lớn làm headline)
  - List 3–5 câu English, mỗi câu có AudioButton nếu map được line_NN audio
    (câu từ dialogue index 0..n → lineKey(index). Nếu takeaway_lines custom không map
    được dialogue index → chỉ hiện text, không có audio. OK.)
  - Dưới list: hiện điểm nhỏ "{score}% · {correctCount}/{totalItems} câu đúng"
  - 2 nút: labels.VE_DANH_SACH (primary) + labels.LAM_LAI (secondary)
  - KHÔNG hiện emoji lớn (🏆/👍/💪) hay headline khích lệ. Tone bình tĩnh.
```

### 3.5 Sửa LessonPlayer

File: `tinysteps-app/components/lesson/lesson-player.tsx`

Đổi state machine:

```typescript
// CŨ:
type PlayerState = "dialogue" | "exercises" | "submitting" | "result";

// MỚI:
type PlayerState = "look" | "say" | "practice" | "submitting" | "takeaway";
```

Flow:

```
look: render DialogueView + nút labels.TIEP_THEO_NOI → "say"
say: render SayStation → onComplete → "practice"
practice: render ExerciseRunner (y hệt cũ)
submitting: KHÔNG dùng alert(). Hiện inline error banner labels.LUU_LOI + nút thử lại
takeaway: render TakeawayStation với score + takeaway lines
handleReplay: về "look"
```

Import `stationsFor` và `takeawayLines` từ `lib/lesson/stations.ts`. Dùng `stationsFor(lesson)` để xác định flow — nếu lesson v2 không có "say" trong stations thì skip.

Giữ `startLesson(lesson.id)` fire-and-forget on mount.

### 3.6 Dashboard Simplification

File: `tinysteps-app/components/dashboard/dashboard-view.tsx`

Thay đổi:
- Luôn hiện 1 CTA lớn: next lesson hoặc "Bắt đầu học"
- Mặc định chỉ hiện progress bar cho **Starters** và **level đang có completed > 0**
- Thêm nút toggle `labels.XEM_LO_TRINH` / `labels.AN_LO_TRINH` để expand/collapse
  các level chưa bắt đầu
- Default: collapsed. Lý do: giáo viên mới vào thấy 5 level dài dằng dặc sẽ nản

### 3.7 Navigation Tab Adjustment

File: `tinysteps-app/components/app-navigation.tsx`

Thay đổi:
- Giữ 5 tab luôn hiển thị (KHÔNG ẩn tab)
- Tab Listening + Writing: nếu user chưa complete bài Movers nào → hiện label
  `labels.SAP_RA_MAT` thay vì icon, và disable link (pointer-events-none, opacity-50)
- Khi user complete ≥ 1 bài Movers → tab hoạt động bình thường

Cách lấy "đã có bài movers+":
- Layout `(app)/layout.tsx` đã có server-side context → pass prop `hasMoversProgress`
  vào AppNavigation
- Hoặc tạo helper `lib/progress/current-level.ts` nếu layout chưa có data

### 3.8 Acceptance Criteria Phase 3

```bash
cd tinysteps-app
npm test                     # all tests pass including new station tests
npx tsc --noEmit             # TypeScript clean
npx next build               # production build green

# Smoke test (manual):
# 1. /login → starters_lesson_001 → Look → Say → 5 quiz → Takeaway
# 2. Takeaway hiện "Câu mang vào lớp" + 4 câu + điểm nhỏ
# 3. "Làm lại" → quay về Look
# 4. Mở starters_lesson_010 (v1) → vẫn Look → Say → 5 quiz → Takeaway
# 5. User chưa học Movers → tab Listening/Writing hiện "Sắp có", disabled
# 6. Dashboard: chỉ hiện Starters bar, nút "Xem cả lộ trình" expand/collapse
# 7. /mua và paywall lesson_004+ không đổi
```

---

## Phase 4 — REWRITE 3 FREE LESSONS

### Mục tiêu

3 bài free trở thành showcase chất lượng mới: content đúng CEFR, exercises đa dạng, takeaway curated.

### 4.1 Types (mở rộng)

File: `tinysteps-app/lib/types/content-types.ts`

Thêm (KHÔNG xóa types cũ):

```typescript
export type SchemaVersion = 1 | 2;

export type PictureYesNoExercise = {
  type: "picture_yes_no";
  instruction: string;
  image_hint: string;
  items: { sentence: string; correct_answer: "yes" | "no" }[];
};

// Mở rộng Exercise union
export type Exercise =
  | MatchExercise
  | ArrangeExercise
  | ListenChooseExercise
  | FillBlankExercise
  | MultipleChoiceExercise
  | PictureYesNoExercise;

// Lesson type mở rộng (optional fields cho v2)
// KHÔNG require schema_version — 172 bài cũ không có
export interface Lesson {
  // ... existing required fields ...
  schema_version?: SchemaVersion;
  stations?: StationId[];
  takeaway_lines?: string[];
  scene_image_hint?: string;
}
```

### 4.2 Zod Schema

File: `tinysteps-app/lib/content/content-schemas.ts`

- Thêm `pictureYesNoExercise` với literal `"picture_yes_no"`
- `lessonSchema.exercises`: đổi `min(2).max(8)` (từ min 5 → min 2)
- Thêm optional fields: `schema_version`, `stations`, `takeaway_lines`, `scene_image_hint`
- **KHÔNG require `schema_version`** — 172 bài cũ không có field này

### 4.3 computeScore Update

File: `tinysteps-app/lib/exercises/check-answer.ts`

```typescript
function itemCorrectAnswer(item: unknown): string | null {
  if (!item || typeof item !== "object") return null;
  const rec = item as Record<string, unknown>;
  return typeof rec.correct_answer === "string" ? rec.correct_answer : null;
}
```

`totalItems`: chỉ đếm exercises có `items` array. Skip types không chấm điểm.

Test: fixture v1 (5 types) vẫn cho đúng score. PictureYesNo "yes"/"no" check case-insensitive.

### 4.4 PictureYesNo Component

Tạo file: `tinysteps-app/components/exercises/picture-yes-no-exercise.tsx`

```
Props:
  lessonId: string
  exercise: PictureYesNoExercise
  exerciseIndex: number
  onItemAnswer: (itemIndex: number, userAnswer: string) => void
  onComplete: () => void

Behavior:
  - Hiện 1 ảnh scene (từ illustration manifest, key "scene")
  - Tuần tự từng item: hiện sentence tiếng Anh + 2 nút "Yes" / "No"
  - FeedbackBar sau mỗi item
  - Không hiện ảnh scene nếu không có → fallback SVG placeholder
```

ExerciseRunner: thêm `case "picture_yes_no"` → render PictureYesNoExerciseComponent.

### 4.5 Nội dung 3 bài free

Sửa JSON trong `tinysteps-data/lessons/starters/` VÀ regenerate index.

**QUAN TRỌNG:** Sau khi sửa JSON, chạy:

```bash
cd tinysteps-app
node scripts/prepare-content.mjs
```

#### `starters_lesson_001` — Good morning, class

```json
{
  "id": "starters_lesson_001",
  "level": "starters",
  "schema_version": 2,
  "topic_id": "topic_before_class",
  "order": 1,
  "title": "Good morning, class",
  "scenario": "Monday morning. You open the classroom door and start the lesson.",
  "estimated_minutes": 4,
  "stations": ["look", "say", "practice", "takeaway"],
  "takeaway_lines": [
    "Good morning, class.",
    "Sit down, please.",
    "Open your book.",
    "Look at the board."
  ],
  "dialogue": {
    "setting": "Classroom door, Monday morning",
    "characters": [
      {"id": "char_a", "name": "Ms. Lan", "role": "teacher"},
      {"id": "char_b", "name": "Class", "role": "students"}
    ],
    "lines": [
      {"character_id": "char_a", "text": "Good morning, class."},
      {"character_id": "char_b", "text": "Good morning, teacher."},
      {"character_id": "char_a", "text": "Sit down, please. Open your book."},
      {"character_id": "char_b", "text": "Yes, teacher."}
    ]
  },
  "vocabulary_ids": ["starters_vocab_001", "starters_vocab_003", "starters_vocab_004", "starters_vocab_006", "starters_vocab_027"],
  "grammar_ids": ["starters_grammar_001"],
  "exercises": [
    {
      "type": "match",
      "instruction": "Match the picture with the correct word.",
      "items": [
        {"image_hint": "the sun rising over a school building", "correct_answer": "morning"},
        {"image_hint": "an open English textbook on a desk", "correct_answer": "book"},
        {"image_hint": "a female teacher smiling at the front of a class", "correct_answer": "teacher"}
      ]
    },
    {
      "type": "listen_choose",
      "instruction": "Listen and choose the correct sentence.",
      "items": [
        {"audio_text": "Open your book.", "options": ["Open your book.", "Sit down, please.", "Good morning."], "correct_answer": "Open your book."},
        {"audio_text": "Sit down, please.", "options": ["Good morning.", "Sit down, please.", "Open your book."], "correct_answer": "Sit down, please."},
        {"audio_text": "Look at the board.", "options": ["Sit down, please.", "Open your book.", "Look at the board."], "correct_answer": "Look at the board."}
      ]
    },
    {
      "type": "arrange",
      "instruction": "Put the words in the correct order.",
      "items": [
        {"words": ["your", ".", "Open", "book"], "correct_answer": "Open your book."},
        {"words": ["down", "please", "Sit", ".", ","], "correct_answer": "Sit down, please."},
        {"words": ["at", ".", "Look", "the", "board"], "correct_answer": "Look at the board."}
      ]
    }
  ],
  "ai_conversation": {
    "role": "student",
    "scenario": "Respond to classroom instructions.",
    "opening_line": "Good morning, teacher! What do we do first?",
    "level_constraints": {
      "max_sentence_length": 6,
      "allowed_grammar": ["starters_grammar_001"],
      "target_vocabulary": ["starters_vocab_001", "starters_vocab_003", "starters_vocab_004"]
    },
    "success_criteria": "Learner gives simple classroom instructions."
  }
}
```

**Grammar check:** Chỉ dùng imperative_positive (Open, Sit, Look) + present_simple_be (ngầm). Đúng Starters.

#### `starters_lesson_002` — Open your book

```json
{
  "id": "starters_lesson_002",
  "level": "starters",
  "schema_version": 2,
  "topic_id": "topic_in_class",
  "order": 2,
  "title": "Open your book",
  "scenario": "The class is noisy. You give short instructions.",
  "estimated_minutes": 4,
  "stations": ["look", "say", "practice", "takeaway"],
  "takeaway_lines": [
    "Listen to me.",
    "Look at the board.",
    "Don't run.",
    "Close your book."
  ],
  "dialogue": {
    "setting": "Classroom, students are noisy",
    "characters": [
      {"id": "char_a", "name": "Mr. Binh", "role": "teacher"},
      {"id": "char_b", "name": "Nam", "role": "student"}
    ],
    "lines": [
      {"character_id": "char_a", "text": "Listen to me, please."},
      {"character_id": "char_b", "text": "Yes, teacher."},
      {"character_id": "char_a", "text": "Don't run in class."},
      {"character_id": "char_b", "text": "Sorry, teacher."}
    ]
  },
  "vocabulary_ids": ["starters_vocab_004", "starters_vocab_005", "starters_vocab_006", "starters_vocab_009", "starters_vocab_027"],
  "grammar_ids": ["starters_grammar_001", "starters_grammar_002"],
  "exercises": [
    {
      "type": "match",
      "instruction": "Match the picture with the correct word.",
      "items": [
        {"image_hint": "a blue ink pen lying on a notebook", "correct_answer": "pen"},
        {"image_hint": "a student sitting at a desk", "correct_answer": "sit"},
        {"image_hint": "an open classroom door", "correct_answer": "door"}
      ]
    },
    {
      "type": "listen_choose",
      "instruction": "Listen and choose the correct sentence.",
      "items": [
        {"audio_text": "Listen to me.", "options": ["Look at the board.", "Listen to me.", "Don't run."], "correct_answer": "Listen to me."},
        {"audio_text": "Don't run.", "options": ["Don't run.", "Listen to me.", "Close your book."], "correct_answer": "Don't run."},
        {"audio_text": "Close your book.", "options": ["Listen to me.", "Don't run.", "Close your book."], "correct_answer": "Close your book."}
      ]
    },
    {
      "type": "arrange",
      "instruction": "Put the words in the correct order.",
      "items": [
        {"words": ["to", ".", "me", "Listen"], "correct_answer": "Listen to me."},
        {"words": ["run", ".", "Don't"], "correct_answer": "Don't run."},
        {"words": ["your", "Close", ".", "book"], "correct_answer": "Close your book."}
      ]
    }
  ],
  "ai_conversation": {
    "role": "student",
    "scenario": "Follow classroom instructions from teacher.",
    "opening_line": "Teacher, the class is very noisy today.",
    "level_constraints": {
      "max_sentence_length": 6,
      "allowed_grammar": ["starters_grammar_001", "starters_grammar_002"],
      "target_vocabulary": ["starters_vocab_004", "starters_vocab_009"]
    },
    "success_criteria": "Learner gives positive and negative commands."
  }
}
```

**Grammar check:** imperative_positive + imperative_negative. Đúng Starters.

#### `starters_lesson_003` — Good job

```json
{
  "id": "starters_lesson_003",
  "level": "starters",
  "schema_version": 2,
  "topic_id": "topic_praise_correction",
  "order": 3,
  "title": "Good job",
  "scenario": "A student answers your question. You praise and help.",
  "estimated_minutes": 4,
  "stations": ["look", "say", "practice", "takeaway"],
  "takeaway_lines": [
    "Good job.",
    "Well done.",
    "Try again.",
    "Louder, please."
  ],
  "dialogue": {
    "setting": "Classroom, during a lesson",
    "characters": [
      {"id": "char_a", "name": "Ms. Hoa", "role": "teacher"},
      {"id": "char_b", "name": "Lan", "role": "student"}
    ],
    "lines": [
      {"character_id": "char_a", "text": "Read this word, please."},
      {"character_id": "char_b", "text": "Apple."},
      {"character_id": "char_a", "text": "Good job! Louder, please."},
      {"character_id": "char_b", "text": "Apple!"}
    ]
  },
  "vocabulary_ids": ["starters_vocab_001", "starters_vocab_006", "starters_vocab_027", "starters_vocab_028", "starters_vocab_029"],
  "grammar_ids": ["starters_grammar_001"],
  "exercises": [
    {
      "type": "match",
      "instruction": "Match the picture with the correct word.",
      "items": [
        {"image_hint": "a teacher giving thumbs up to a student", "correct_answer": "good"},
        {"image_hint": "a red apple on a teacher desk", "correct_answer": "apple"},
        {"image_hint": "a student reading aloud from a book", "correct_answer": "read"}
      ]
    },
    {
      "type": "listen_choose",
      "instruction": "Listen and choose the correct sentence.",
      "items": [
        {"audio_text": "Good job.", "options": ["Try again.", "Good job.", "Louder, please."], "correct_answer": "Good job."},
        {"audio_text": "Try again.", "options": ["Good job.", "Well done.", "Try again."], "correct_answer": "Try again."},
        {"audio_text": "Louder, please.", "options": ["Louder, please.", "Try again.", "Good job."], "correct_answer": "Louder, please."}
      ]
    },
    {
      "type": "arrange",
      "instruction": "Put the words in the correct order.",
      "items": [
        {"words": ["this", "Read", ".", "word"], "correct_answer": "Read this word."},
        {"words": ["please", ".", "Louder", ","], "correct_answer": "Louder, please."},
        {"words": ["job", ".", "Good"], "correct_answer": "Good job."}
      ]
    }
  ],
  "ai_conversation": {
    "role": "student",
    "scenario": "Answer teacher questions and receive feedback.",
    "opening_line": "Teacher, is my answer correct?",
    "level_constraints": {
      "max_sentence_length": 6,
      "allowed_grammar": ["starters_grammar_001"],
      "target_vocabulary": ["starters_vocab_001", "starters_vocab_006", "starters_vocab_027"]
    },
    "success_criteria": "Learner praises student and gives gentle correction."
  }
}
```

**Grammar check:** imperative_positive only. Đúng Starters.

### 4.6 Vocabulary ID Verification

Trước khi commit 3 bài free, grep xác nhận tất cả `vocabulary_ids` và `grammar_ids` tồn tại:

```bash
cd tinysteps-data

# Extract all vocab IDs used in 3 free lessons
python3 -c "
import json, sys

used_ids = set()
for f in ['lessons/starters/lesson-001.json', 'lessons/starters/lesson-002.json', 'lessons/starters/lesson-003.json']:
    d = json.load(open(f))
    used_ids.update(d['vocabulary_ids'])
    used_ids.update(d['grammar_ids'])

vocab = json.load(open('vocabulary/starters.json'))
vocab_ids = {w['id'] for w in vocab['words']}

grammar = json.load(open('grammar/starters.json'))
grammar_ids = {g['id'] for g in grammar['grammar_points']}

available = vocab_ids | grammar_ids
missing = used_ids - available
if missing:
    print(f'MISSING IDs: {missing}')
    sys.exit(1)
else:
    print(f'All {len(used_ids)} IDs verified.')
"
```

### 4.7 Acceptance Criteria Phase 4

```bash
cd tinysteps-data
python3 validate_data.py             # pass
python3 audit_cefr_alignment.py      # 0 violations

cd ../tinysteps-app
node scripts/prepare-content.mjs     # pass
npx tsc --noEmit                     # clean
npm test                             # pass
npx next build                       # green

# Smoke test:
# 1. starters_lesson_001 → Look (4 lines) → Say (4 lines) → 3 exercises → Takeaway (4 câu lệnh lớp)
# 2. starters_lesson_004 (v1, paywall) → paywall notice
# 3. starters_lesson_005 (v1, trả phí) → Look → Say → 5 quiz cũ → Takeaway (4 dòng đầu)
# 4. Dashboard + nav không lỗi
```

---

## THỰC THI

### Thứ tự file đụng

```
PHASE 1 (Python, tinysteps-data/ only):
  tinysteps-data/audit_cefr_alignment.py           (NEW)
  tinysteps-data/fix_cefr_violations.py             (NEW)
  tinysteps-data/reports/cefr_audit_report.json     (NEW, generated)
  tinysteps-data/lessons/**/*.json                  (modified by fix script)

PHASE 2 (Python, tinysteps-data/ only):
  tinysteps-data/audit_exercise_quality.py          (NEW)
  tinysteps-data/fix_exercise_quality.py            (NEW)
  tinysteps-data/reports/exercise_quality_report.json (NEW, generated)
  tinysteps-data/lessons/**/*.json                  (modified by fix script)

PHASE 3 (TypeScript, tinysteps-app/ only):
  tinysteps-app/lib/i18n/labels.ts                  (add keys)
  tinysteps-app/lib/lesson/stations.ts              (NEW)
  tinysteps-app/lib/lesson/__tests__/stations.test.ts (NEW)
  tinysteps-app/components/lesson/say-station.tsx   (NEW)
  tinysteps-app/components/lesson/takeaway-station.tsx (NEW)
  tinysteps-app/components/lesson/lesson-player.tsx (rewrite state machine)
  tinysteps-app/components/dashboard/dashboard-view.tsx (simplify)
  tinysteps-app/components/app-navigation.tsx       (tab states)

PHASE 4 (Both):
  tinysteps-app/lib/types/content-types.ts          (add PictureYesNo, optional fields)
  tinysteps-app/lib/content/content-schemas.ts      (Zod update)
  tinysteps-app/lib/exercises/check-answer.ts       (safe itemCorrectAnswer)
  tinysteps-app/components/exercises/picture-yes-no-exercise.tsx (NEW)
  tinysteps-app/components/exercises/exercise-runner.tsx (add case)
  tinysteps-data/lessons/starters/lesson-001.json   (rewrite)
  tinysteps-data/lessons/starters/lesson-002.json   (rewrite)
  tinysteps-data/lessons/starters/lesson-003.json   (rewrite)
  tinysteps-kit/schemas/lesson.v2.schema.json       (NEW)

NOT TOUCHED:
  paid-access.ts (IDs unchanged)
  audio-keys.ts (contract unchanged)
  supabase/ (no migrations)
  marketing pages
  admin pages
  listening/writing players
```

### Lệnh kiểm tra sau mỗi phase

```bash
# Từ root repo:

# Phase 1+2:
cd tinysteps-data
python3 validate_data.py
python3 audit_cefr_alignment.py

# Phase 3+4:
cd tinysteps-app
node scripts/prepare-content.mjs
npm test
npx tsc --noEmit
npx next build
```

### Ghi chú cho agent

1. **Commit nhỏ**, `fix:` / `feat:` theo convention.
2. **KHÔNG commit** `.env`, QR images, service role keys.
3. **KHÔNG thêm dependency** trừ khi thật sự cần và ghi rõ lý do.
4. **JSON sửa xong phải chạy `prepare-content.mjs`** để regenerate `generated-lessons-index.ts`. KHÔNG sửa tay file generated.
5. **`ai_conversation` vẫn required** trong Zod schema — đừng xóa khỏi 3 bài rewrite.
6. **English-only** trong JSON. Labels Việt chỉ trong `labels.ts`.
7. **Mỗi phase phải pass acceptance criteria** trước khi sang phase tiếp.
8. **Regex grammar detectors không hoàn hảo.** Phase 1 audit script nên output cho human review, KHÔNG tự động rewrite mà không confirm. Script `fix_cefr_violations.py` chạy SAU khi human review report.

---

## TƯƠNG LAI (không code trong lần này)

Các việc để sau khi Phase 1–4 hoàn thành:

- **P5:** Script stamp `schema_version: 1` + `takeaway_lines` cho 172 bài cũ (curated, không fallback)
- **P6:** Rewrite thêm Starters school-topic lessons (dùng v2 schema)
- **P7:** Movers differences + form listening type
- **P8:** KET/PET `prompt_write` exercise type (email 25/100 words)
- **P9:** Pronunciation guide (hiện IPA + audio, không chấm điểm)
- **P10:** Onboarding placement test (10 câu, assign starting level)

---

*Spec version: 2.0 — August 2026*
*Author: XuyenLab + Claude review*
*Replaces: GROK_BUILD_LESSON_STATIONS.md (incorporated as Phase 3+4)*
