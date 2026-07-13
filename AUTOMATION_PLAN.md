# TinySteps Automation Engine v2 — Kế Hoạch Thực Hiện

## Mục tiêu
Chạy `python3 tinysteps-data/generate_lessons.py` → sinh 175 bài học JSON + cập nhật toàn bộ 5 trang HTML review portal.

## Files thay đổi
| File | Thao tác |
|---|---|
| `tinysteps-data/generate_lessons.py` | Viết lại hoàn toàn |
| `tinysteps-data/exports/lessons-*.html` | Inject data từ JSON (script tự động) |
| `tinysteps-data/exports/index.html` | Update progress counters (script tự động) |

---

## Lưu ý quan trọng trước khi chạy

`lessons-starters.html` hiện đang chứa **5 bài học thủ công** (nội dung khác với `lesson-001.json` đến `lesson-005.json`). Khi script chạy, phần HTML data sẽ bị **thay thế hoàn toàn** bởi nội dung trong các file JSON. Nếu muốn giữ nội dung HTML cũ cho 5 bài mẫu, hãy cập nhật lại các file `lessons/starters/lesson-00{1-5}.json` trước.

---

## Tóm tắt lỗi trong script hiện tại

| Vị trí | Lỗi | Hậu quả |
|---|---|---|
| `generate_exercises()` — listen_choose | `options = [word, f"not_{word}", f"bad_{word}"]` | Output: `"Please look at the not_book."` — không phải tiếng Anh |
| `generate_exercises()` — fill_blank | `word[len(word)//2:]` | Output: `"Please check the ___ok."` — câu bị cắt đứt |
| `generate_exercises()` — arrange | Hardcode cứng 3 câu giống nhau mọi bài | Bài 20 chủ đề `topic_market` vẫn ra "Open your book." |
| `main()` | Không có HTML pipeline | 5 trang `lessons-*.html` không được cập nhật |

---

## Task 1 — Helper: `blank_key_word()`

Thêm hàm này vào file, **trước** `generate_exercises()`:

```python
import re as _re

def blank_key_word(sentence, grammar_name):
    """Trả về (prompt_có_blank, correct_answer) cho fill_blank exercise."""
    # Danh sách từ cần blank theo tên grammar pattern
    TARGETS = {
        "present_simple_be":             ["am", "is", "are", "'m", "'s"],
        "imperative_negative":           ["Don't", "don't"],
        "present_continuous":            ["am", "is", "are", "'m", "'s"],
        "can_cant":                      ["can", "can't", "Can"],
        "want_to_verb":                  ["want", "wants"],
        "present_perfect_simple":        ["have", "has", "haven't"],
        "going_to_verb":                 ["going"],
        "must_mustnt":                   ["must", "mustn't"],
        "should_shouldnt":               ["should", "shouldn't"],
        "reported_commands":             ["told"],
        "present_perfect_for_since":     ["have", "has"],
        "could_requests":                ["Could", "could"],
        "would_like_to":                 ["would", "'d"],
        "used_to":                       ["used"],
        "relative_clauses_basic":        ["who", "which"],
        "second_conditional":            ["would"],
        "present_perfect_continuous":    ["been"],
        "wish_past_simple":              ["wish", "wishes"],
        "reported_speech":               ["said", "told"],
        "passive_with_modals":           ["be", "been"],
    }
    # Patterns blank từ đầu câu (verb command)
    FIRST_WORD_PATTERNS = {"imperative_positive"}
    # Patterns blank từ thứ 2 (main verb sau subject)
    SECOND_WORD_PATTERNS = {"present_simple_positive", "past_simple_regular", "past_simple_irregular"}

    sentence = sentence.strip()
    words = sentence.split()
    targets = TARGETS.get(grammar_name)

    if targets:
        for i, word in enumerate(words):
            clean = word.strip(".,!?;:'\"")
            if clean in targets:
                answer = clean
                words[i] = words[i].replace(clean, "___", 1)
                return " ".join(words), answer

    if grammar_name in FIRST_WORD_PATTERNS and words:
        answer = words[0].strip(".,!?")
        words[0] = "___"
        return " ".join(words), answer

    if grammar_name in SECOND_WORD_PATTERNS and len(words) >= 2:
        answer = words[1].strip(".,!?")
        words[1] = "___"
        return " ".join(words), answer

    # Fallback: blank từ đầu tiên
    if words:
        answer = words[0].strip(".,!?")
        words[0] = "___"
        return " ".join(words), answer

    return None, None
```

---

## Task 2 — Viết lại `generate_exercises()`

Thay thế toàn bộ hàm `generate_exercises()` hiện tại bằng code sau:

```python
def generate_exercises(lvl, vocab_items, grammar_items):
    import random as rnd

    v = vocab_items

    # ── 1. MATCH ─────────────────────────────────────────────────────
    # Dùng image_hint từ vocab registry — không tạo fake strings
    match_pool = [w for w in v if w.get("image_hint")][:3]
    if len(match_pool) < 3:
        existing = {m["word"] for m in match_pool}
        for w in v:
            if len(match_pool) >= 3:
                break
            if w["word"] not in existing:
                match_pool.append(w)
                existing.add(w["word"])
    match_items = [
        {"image_hint": w.get("image_hint", f"an image of {w['word']}"), "correct_answer": w["word"]}
        for w in match_pool
    ]

    # ── 2. ARRANGE ───────────────────────────────────────────────────
    # Dùng example sentences từ grammar registry — không hardcode
    all_examples = [ex for gp in grammar_items for ex in gp.get("examples", [])]
    arrange_items = []
    for ex in all_examples[:3]:
        sent = ex["sentence"]
        # Tokenize: tách dấu câu thành token riêng
        tokens = _re.findall(r"[\w']+|[.,!?]", sent)
        if len(tokens) < 2:
            continue
        shuffled = tokens[:]
        for _ in range(10):  # shuffle cho đến khi khác với bản gốc
            rnd.shuffle(shuffled)
            if shuffled != tokens:
                break
        arrange_items.append({"words": shuffled, "correct_answer": sent})
    if not arrange_items:
        # Fallback nếu không có examples
        for gp in grammar_items:
            for ex in gp.get("examples", []):
                tokens = ex["sentence"].split()
                rnd.shuffle(tokens)
                arrange_items.append({"words": tokens, "correct_answer": ex["sentence"]})
                break
            if arrange_items:
                break

    # ── 3. LISTEN CHOOSE ─────────────────────────────────────────────
    # Đáp án đúng + 2 distractors là câu THẬT từ grammar examples
    all_sents = [ex["sentence"] for gp in grammar_items for ex in gp.get("examples", [])]
    listen_items = []
    for sent in all_sents[:3]:
        distractors = [s for s in all_sents if s != sent][:2]
        # Bổ sung từ common_mistakes nếu thiếu
        if len(distractors) < 2:
            for gp in grammar_items:
                for cm in gp.get("common_mistakes", []):
                    c = cm.get("correct", "")
                    if c and c != sent and c not in distractors:
                        distractors.append(c)
                    if len(distractors) >= 2:
                        break
        options = [sent] + distractors[:2]
        rnd.shuffle(options)
        listen_items.append({
            "audio_text": sent,
            "options": options,
            "correct_answer": sent
        })

    # ── 4. FILL BLANK ─────────────────────────────────────────────────
    # Dùng blank_key_word() để tạo prompt đúng grammar
    fill_items = []
    for gp in grammar_items[:1]:
        for ex in gp.get("examples", [])[:3]:
            prompt, answer = blank_key_word(ex["sentence"], gp["name"])
            if prompt and answer:
                fill_items.append({"prompt": prompt, "correct_answer": answer})
    if not fill_items:
        for w in v[:3]:
            fill_items.append({
                "prompt": f"This is a ___. (hint: {w.get('image_hint', w['word'])})",
                "correct_answer": w["word"]
            })

    # ── 5. MULTIPLE CHOICE ────────────────────────────────────────────
    # Distractor là từ vựng THẬT từ registry — không dùng fake strings
    mcq_items = []
    for w in v[:3]:
        word = w["word"]
        hint = w.get("image_hint", f"a picture of {word}")
        distractors = [other["word"] for other in v if other["word"] != word][:2]
        options = [word] + distractors
        rnd.shuffle(options)
        mcq_items.append({
            "prompt": f"Look at the picture ({hint}). What is this?",
            "options": options,
            "correct_answer": word
        })

    return [
        {"type": "match",           "instruction": "Match the picture with the correct word.",  "items": match_items},
        {"type": "arrange",         "instruction": "Put the words in the correct order.",       "items": arrange_items},
        {"type": "listen_choose",   "instruction": "Listen and choose the correct sentence.",   "items": listen_items},
        {"type": "fill_blank",      "instruction": "Fill in the missing word.",                 "items": fill_items},
        {"type": "multiple_choice", "instruction": "Choose the best answer.",                   "items": mcq_items},
    ]
```

---

## Task 3 — Dialogue Bank (toàn bộ 12 chủ đề × 3 nhóm × 2 variant)

Thêm constant `DIALOGUE_BANK` vào đầu file (sau phần imports). Cấu trúc mỗi entry:
- Key level group: `"starters"` | `"movers"` | `"advanced"` (covers flyers/ket/pet)
- Mỗi group chứa danh sách 2 variant
- Mỗi variant là danh sách `(char_role, text, note_or_None)`
- `char_role`: `"a"` = nhân vật chính (teacher/buyer/traveler), `"b"` = nhân vật phụ

```python
DIALOGUE_BANK = {

    # ──────────────────────────────────────────────────────────────────
    "topic_before_class": {
        "starters": [
            [   # Variant A — 4 lines
                ("a", "Good morning! How are you today?", "(smiling)"),
                ("b", "Good morning! I am fine, thank you.", None),
                ("a", "I am a teacher here. Are you ready for class?", None),
                ("b", "Yes, I am ready. See you later!", None),
            ],
            [   # Variant B — 5 lines
                ("a", "Good morning, colleague!", None),
                ("b", "Good morning! How are you?", None),
                ("a", "I am good. I am a teacher too.", None),
                ("b", "Good. Are you ready for class today?", None),
                ("a", "Yes! See you in the classroom.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Good morning! Did you arrive early today?", None),
                ("b", "Yes, I arrived before seven o'clock.", None),
                ("a", "I prepared the classroom yesterday afternoon.", None),
                ("b", "Did you clean the board?", None),
                ("a", "Yes, I cleaned the board and wrote the timetable.", None),
                ("b", "Excellent. Let's have a great lesson today!", None),
            ],
            [   # Variant B — 7 lines
                ("a", "Good morning! Are you ready for today's lesson?", None),
                ("b", "Yes! I prepared my materials yesterday evening.", None),
                ("a", "I arrived early and set up the desks.", None),
                ("b", "I also prepared some worksheets for the students.", None),
                ("a", "We work well as a team.", None),
                ("b", "Yes, the students really enjoy our lessons.", None),
                ("a", "See you in class!", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Good morning. I'd like to check the school schedule before class.", None),
                ("b", "Sure. The principal updated the timetable this morning.", None),
                ("a", "We should inform the other teachers about the change.", None),
                ("b", "I have already sent them an email with the new details.", None),
                ("a", "Furthermore, we need to prepare worksheets for Period Three.", None),
                ("b", "I agree. If we finish early, we will have time to review.", None),
                ("a", "Let me explain the new procedure to the staff members.", None),
                ("b", "Thank you. Your preparation is always very helpful.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "Good morning. I wanted to discuss this morning's lesson plan.", None),
                ("b", "Yes, I was going to suggest we review the schedule together.", None),
                ("a", "Period Two is confirmed at nine o'clock.", None),
                ("b", "We should also prepare the safety procedure handout.", None),
                ("a", "I printed twenty copies after the staff meeting yesterday.", None),
                ("b", "Excellent. Furthermore, the new colleague needs a classroom briefing.", None),
                ("a", "I will take care of that before the first bell.", None),
                ("b", "If we coordinate well, the lessons will run very smoothly.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_in_class": {
        "starters": [
            [   # Variant A — 4 lines
                ("a", "Open your book, please.", "(pointing to desk)"),
                ("b", "Yes, teacher. I am opening it.", None),
                ("a", "Good. Look at the board. This is a blue pen.", None),
                ("b", "I see it, teacher.", None),
            ],
            [   # Variant B — 5 lines
                ("a", "Stand up, class! Good morning!", None),
                ("b", "Good morning, teacher!", None),
                ("a", "Sit down. Look at the board.", None),
                ("b", "Yes, teacher. We are looking.", None),
                ("a", "Good. Listen to me, please.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Show me your homework, please.", None),
                ("b", "Here it is, teacher. I finished it last night.", None),
                ("a", "Good student! Now help me clean the board.", None),
                ("b", "Yes, I am cleaning it now.", None),
                ("a", "Do you understand the next activity?", None),
                ("b", "Yes, I understand it very well.", None),
            ],
            [   # Variant B — 7 lines
                ("a", "Did you bring your book today?", None),
                ("b", "Yes, teacher. Here is my book.", None),
                ("a", "Good. Open it to page twelve.", None),
                ("b", "I opened it. Should I read aloud?", None),
                ("a", "Yes, read the first sentence, please.", None),
                ("b", "I am reading it now.", None),
                ("a", "Excellent. Very good progress!", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Can you explain this word to your classmates?", None),
                ("b", "Yes. It means we should pay attention during the lesson.", None),
                ("a", "That is a correct explanation. Excellent progress!", None),
                ("b", "Thank you, teacher. I always practise speaking at home.", None),
                ("a", "If you continue, your English will improve very quickly.", None),
                ("b", "I'd like to ask a question about the next task.", None),
                ("a", "Of course. What is your question?", None),
                ("b", "I think the task is interesting, but I need more time.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "Today we are going to discuss classroom communication.", None),
                ("b", "I have been thinking about ways to improve my speaking.", None),
                ("a", "That is great. You should also focus on listening carefully.", None),
                ("b", "Could you recommend some practice activities?", None),
                ("a", "Yes, I suggest you join the after-school English club.", None),
                ("b", "I would if I had more free time after school.", None),
                ("a", "I understand. Even ten minutes of daily practice helps.", None),
                ("b", "Thank you, teacher. I will try my best.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_giving_instructions": {
        "starters": [
            [   # Variant A — 4 lines
                ("a", "Listen to me, class!", "(raising hand)"),
                ("b", "Yes, teacher. We are listening.", None),
                ("a", "Look at the board. Don't run in the class.", None),
                ("b", "Yes, teacher. We understand.", None),
            ],
            [   # Variant B — 5 lines
                ("a", "Don't talk, please. Look here.", None),
                ("b", "I am sorry, teacher.", None),
                ("a", "Stand up, class.", None),
                ("b", "We are standing.", None),
                ("a", "Good. Now sit down and listen.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Clean the board, please.", None),
                ("b", "Yes, I am cleaning it right now.", None),
                ("a", "Then open your book and do the exercise.", None),
                ("b", "Should we do the vocabulary task too?", None),
                ("a", "Yes, please. Help your partner.", None),
                ("b", "We will start immediately.", None),
            ],
            [   # Variant B — 7 lines
                ("a", "Class, please do your homework tonight.", None),
                ("b", "Yes, teacher. What page should we do?", None),
                ("a", "Do page fifteen and page sixteen.", None),
                ("b", "Should we write the answers in pencil?", None),
                ("a", "Yes, write in pencil and check your work.", None),
                ("b", "Can we work with a partner?", None),
                ("a", "Yes, you can work together.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "You must follow the instructions carefully during the test.", None),
                ("b", "Understood, teacher. Should we write our names on the paper?", None),
                ("a", "Yes, write your full name at the top of the page.", None),
                ("b", "Could we use a dictionary for the reading section?", None),
                ("a", "No, this is a closed-book test. Please put it away.", None),
                ("b", "If we make a mistake, should we cross it out neatly?", None),
                ("a", "Yes, draw one line through the wrong answer and rewrite.", None),
                ("b", "Thank you for the clear instructions.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I'd like to explain the procedure for this group project.", None),
                ("b", "Could you tell us the deadline for the final report?", None),
                ("a", "The report should be submitted by Friday morning.", None),
                ("b", "Should we present our work to the class as well?", None),
                ("a", "Yes, each group will have five minutes to present.", None),
                ("b", "Furthermore, should we include images in the slides?", None),
                ("a", "Yes, visual materials are strongly recommended.", None),
                ("b", "We will follow your instructions carefully, teacher.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_checking_understanding": {
        "starters": [
            [   # Variant A — 4 lines
                ("a", "Look here, class. Is this a book?", "(pointing)"),
                ("b", "Yes, teacher. It is a book.", None),
                ("a", "Good. Listen. What is this?", None),
                ("b", "It is a pen, teacher.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Listen to me. Look at the board.", None),
                ("b", "Yes, teacher. We are looking.", None),
                ("a", "Is this a good student?", None),
                ("b", "Yes! He is a very good student.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Do you understand the reading task?", None),
                ("b", "Yes, I think I understand it.", None),
                ("a", "Good. Can you help your classmate?", None),
                ("b", "Yes, I will help him now.", None),
                ("a", "Let me check if everyone is ready.", None),
                ("b", "The class is ready, teacher.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Vy, did you understand the homework instructions?", None),
                ("b", "I understood most of it, but I have one question.", None),
                ("a", "Of course. Ask your question.", None),
                ("b", "Should we write the answers in full sentences?", None),
                ("a", "Yes, always write in full sentences.", None),
                ("b", "Thank you. Now I understand completely.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Can you explain the meaning of this vocabulary item to the class?", None),
                ("b", "It means we must cooperate to complete the group task.", None),
                ("a", "Excellent explanation. You are making great progress.", None),
                ("b", "Thank you, teacher. I appreciate your feedback.", None),
                ("a", "If anyone has a question, please raise your hand.", None),
                ("b", "I'd like to ask about the grammar in sentence three.", None),
                ("a", "Of course. I will explain it again slowly.", None),
                ("b", "Thank you. Now I understand the pattern clearly.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "Let's check if everyone understood the listening exercise.", None),
                ("b", "I followed the main idea, but missed some details.", None),
                ("a", "That is fine for now. What was the main topic?", None),
                ("b", "The speakers were discussing a school event.", None),
                ("a", "Correct. You should try to improve your note-taking skills.", None),
                ("b", "If I practised more often, would my listening improve?", None),
                ("a", "Definitely. Regular practice makes a big difference.", None),
                ("b", "I will start practising every day from now on.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_praise_correction": {
        "starters": [
            [   # Variant A — 4 lines
                ("a", "Good job, Nam! Very good!", "(thumbs up)"),
                ("b", "Thank you, teacher! I am happy.", None),
                ("a", "Look at this. That is correct.", None),
                ("b", "Great! I like this lesson.", None),
            ],
            [   # Variant B — 5 lines
                ("a", "Excellent, Vy! That is a good answer.", None),
                ("b", "Thank you, teacher.", None),
                ("a", "He is a good student too.", None),
                ("b", "Thank you. I try hard every day.", None),
                ("a", "Well done, class!", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "That is a great answer, Lan!", None),
                ("b", "Thank you. I prepared it last night.", None),
                ("a", "You did a great job on your homework.", None),
                ("b", "I made one small mistake, I think.", None),
                ("a", "It is okay. Mistakes help us learn.", None),
                ("b", "Yes, I will correct it now.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Well done, Khang! Your writing is very neat.", None),
                ("b", "Thank you, teacher. I tried my best.", None),
                ("a", "But I see a small spelling mistake here.", None),
                ("b", "Oh, I see it. I am sorry.", None),
                ("a", "Do not worry. Please correct it.", None),
                ("b", "Yes, I will fix it right now.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "You have made excellent progress in your writing this month.", None),
                ("b", "Thank you. I practised a lot during the weekend.", None),
                ("a", "Your paragraph structure is clear and logical.", None),
                ("b", "However, I think I used the wrong tense in one sentence.", None),
                ("a", "You are right. Let's look at it together.", None),
                ("b", "I apologise for the careless mistake.", None),
                ("a", "There is no need to apologise. It is part of learning.", None),
                ("b", "If I reviewed my work more carefully, I would make fewer errors.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "Your presentation today was very confident and clear.", None),
                ("b", "Thank you, teacher. I was nervous at first.", None),
                ("a", "It did not show at all. Your vocabulary was varied.", None),
                ("b", "I would like to improve my pronunciation, though.", None),
                ("a", "I suggest you record yourself and listen back each day.", None),
                ("b", "That is a practical idea. I will try it.", None),
                ("a", "Furthermore, the grammar in your report was nearly perfect.", None),
                ("b", "I appreciate your encouraging and constructive feedback.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_school_communication": {
        "starters": [
            [   # Variant A — 4 lines (teacher + parent)
                ("a", "Good morning, Mrs. Cuc! How is Nam today?", "(smiling)"),
                ("b", "Good morning, teacher! He is good.", None),
                ("a", "Nam is a very good student.", None),
                ("b", "Thank you. I am very happy.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Hello! I am Ms. Lan. I am Nam's teacher.", None),
                ("b", "Hello! I am Mrs. Cuc. Nice to meet you.", None),
                ("a", "Nice to meet you too.", None),
                ("b", "Thank you for teaching Nam.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines (teacher calls parent)
                ("a", "Hello, I am calling because An is absent today.", None),
                ("b", "Oh yes, she had a bad cold yesterday.", None),
                ("a", "Please help her complete the homework on page twenty.", None),
                ("b", "I will. When will she return to class?", None),
                ("a", "She can return on Thursday if she feels better.", None),
                ("b", "Thank you for calling. We appreciate it.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Good afternoon. I am Duy's teacher.", None),
                ("b", "Hello, teacher. How is Duy doing in class?", None),
                ("a", "He is doing well. But he was absent yesterday.", None),
                ("b", "I am sorry. He was sick at home.", None),
                ("a", "Please tell him to complete the reading task.", None),
                ("b", "I will tell him today. Thank you for calling.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines (teacher + colleague)
                ("a", "I finished writing the student progress reports for this term.", None),
                ("b", "Did you send the reports to the parents yet?", None),
                ("a", "Yes, I sent them by email yesterday afternoon.", None),
                ("b", "We should also schedule a parent-teacher meeting soon.", None),
                ("a", "I suggest we hold it next Friday morning.", None),
                ("b", "Furthermore, we need to confirm the school hall availability.", None),
                ("a", "I will check with the administration office today.", None),
                ("b", "Thank you. Consistent communication helps everyone.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I'd like to discuss the feedback from last week's parent meeting.", None),
                ("b", "Yes, several parents raised concerns about homework volume.", None),
                ("a", "I understand. We should adjust our policy accordingly.", None),
                ("b", "I have drafted a new homework schedule for your review.", None),
                ("a", "Thank you. I will review it and reply by Wednesday.", None),
                ("b", "Furthermore, the principal has asked for a formal report.", None),
                ("a", "I will prepare the report and submit it by Friday.", None),
                ("b", "If we address the concerns early, we can avoid bigger issues.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_market": {
        "starters": [
            [   # Variant A — 4 lines (buyer + seller)
                ("a", "Hello! I want to buy rice, please.", "(pointing at stall)"),
                ("b", "Hello! Here is fresh rice.", None),
                ("a", "I like rice. How much is it?", None),
                ("b", "It is very cheap. Here you go.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Good morning! I go to the market every day.", None),
                ("b", "Good morning! What do you want today?", None),
                ("a", "I want some water and rice.", None),
                ("b", "Okay! Here is your order.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "I want to buy some fruit, please.", None),
                ("b", "The fruit is very fresh. I bought it this morning.", None),
                ("a", "How much is the mango?", None),
                ("b", "It is thirty thousand dong per kilo.", None),
                ("a", "Okay, I will buy two kilos.", None),
                ("b", "Here you are. Thank you!", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Hello! I bought some rice yesterday, but I need more.", None),
                ("b", "Welcome back! How much do you need today?", None),
                ("a", "I want three kilos of rice and some vegetables.", None),
                ("b", "I have very fresh vegetables today.", None),
                ("a", "That is great. I will take them all.", None),
                ("b", "Thank you. Come back again!", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Could I see the price list for these items, please?", None),
                ("b", "Of course. Here is today's price list.", None),
                ("a", "The price for organic vegetables is quite high.", None),
                ("b", "I apologise, but the quality is excellent.", None),
                ("a", "I always bargain at the market. Can we negotiate?", None),
                ("b", "If you buy five kilos, I will give you a ten percent discount.", None),
                ("a", "That sounds fair. I will take five kilos.", None),
                ("b", "Thank you. Here is your bill and your change.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I made a complaint yesterday about the fish I bought.", None),
                ("b", "I apologise for that. Was there a problem with the quality?", None),
                ("a", "Yes, it did not seem fresh. I had to throw it away.", None),
                ("b", "I understand. I will replace it at no charge today.", None),
                ("a", "I appreciate that. I always prefer to shop here.", None),
                ("b", "If the price were lower, would you buy more regularly?", None),
                ("a", "Yes, price and quality are both very important to me.", None),
                ("b", "I will try to offer you a loyal customer discount.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_restaurant": {
        "starters": [
            [   # Variant A — 4 lines (customer + waiter)
                ("a", "Hello! Water, please.", "(smiling)"),
                ("b", "Yes. Here is your water.", None),
                ("a", "I want rice, please.", None),
                ("b", "Okay. Coming right up.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Good morning! I like rice.", None),
                ("b", "Good morning! We have fresh rice today.", None),
                ("a", "I want rice and water, please.", None),
                ("b", "Here you go. Enjoy your meal.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "I am hungry. I want chicken and rice.", None),
                ("b", "Of course. Would you like a drink?", None),
                ("a", "Yes, clean water, please.", None),
                ("b", "I will bring everything right away.", None),
                ("a", "Thank you. The food here is very good.", None),
                ("b", "Thank you! Please come again.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Hello! I came to this restaurant yesterday.", None),
                ("b", "Welcome back! What would you like today?", None),
                ("a", "I want the same as yesterday — soup and rice.", None),
                ("b", "Of course. Would you like extra vegetables?", None),
                ("a", "Yes, please. And a bottle of water.", None),
                ("b", "I will bring your order very soon.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Good evening. Could I see the menu, please?", None),
                ("b", "Of course. I recommend our daily special.", None),
                ("a", "I prefer vegetarian dishes. Do you have any?", None),
                ("b", "Yes, our stir-fried tofu is very popular.", None),
                ("a", "Excellent. I will have that and a pot of green tea.", None),
                ("b", "Would you like to make a reservation for tomorrow as well?", None),
                ("a", "Yes, I'd like to book a table for four at seven o'clock.", None),
                ("b", "I have confirmed your reservation. See you tomorrow!", None),
            ],
            [   # Variant B — 8 lines
                ("a", "Good afternoon. Could we have the bill, please?", None),
                ("b", "Of course. Was everything satisfactory today?", None),
                ("a", "The food was excellent, but the service was a bit slow.", None),
                ("b", "I apologise for that. We were very busy this evening.", None),
                ("a", "I understand. The quality makes up for it.", None),
                ("b", "If you sign up for our membership, you will receive a discount.", None),
                ("a", "That sounds worthwhile. I often dine here.", None),
                ("b", "Wonderful. I will bring you the application form.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_travel": {
        "starters": [
            [   # Variant A — 4 lines (traveler + agent)
                ("a", "Hello! I want to go to the market.", "(looking at map)"),
                ("b", "The market is very near here.", None),
                ("a", "Thank you! I go there every morning.", None),
                ("b", "Have a good trip. Goodbye!", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Good morning! Is this the bus to school?", None),
                ("b", "Yes, this bus goes to the school.", None),
                ("a", "I go to school every day.", None),
                ("b", "Goodbye! Have a nice day.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Yesterday I went to school by bicycle.", None),
                ("b", "Really? Did you travel far?", None),
                ("a", "Yes, I went about three kilometres.", None),
                ("b", "Can you help me buy a bus ticket to the city centre?", None),
                ("a", "Yes, let's buy it at that counter.", None),
                ("b", "Thank you. You are very helpful!", None),
            ],
            [   # Variant B — 6 lines
                ("a", "I bought a train ticket last week.", None),
                ("b", "Where did you travel to?", None),
                ("a", "I went to Da Nang with my family.", None),
                ("b", "That is wonderful! How was the trip?", None),
                ("a", "It was very nice. I want to go again.", None),
                ("b", "Me too. Let's plan a trip together.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "I would like to buy a train ticket to Hue, please.", None),
                ("b", "Certainly. When would you like to travel?", None),
                ("a", "This Saturday morning, if possible.", None),
                ("b", "There is a train at eight thirty that arrives at noon.", None),
                ("a", "Could you recommend a good hotel near the old city?", None),
                ("b", "Yes, the Heritage Hotel is close to all the attractions.", None),
                ("a", "I will confirm my hotel reservation tonight.", None),
                ("b", "Safe travels. Enjoy your visit to Hue!", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I am sorry to inform you that Flight 204 is delayed.", None),
                ("b", "How long is the delay?", None),
                ("a", "Approximately two hours due to bad weather.", None),
                ("b", "If the flight were on time, I would arrive before dinner.", None),
                ("a", "I understand your frustration. We sincerely apologise.", None),
                ("b", "Could you help me contact my hotel about the late arrival?", None),
                ("a", "Of course. I will call the hotel on your behalf.", None),
                ("b", "Thank you. I appreciate your professional assistance.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_phone": {
        "starters": [
            [   # Variant A — 4 lines (caller + receiver)
                ("a", "Hello! Can you hear me?", "(on the phone)"),
                ("b", "Hello! Yes, I can hear you.", None),
                ("a", "Good morning! Listen to me, please.", None),
                ("b", "Good morning! I am listening.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Hello! How are you?", None),
                ("b", "I am fine, thank you. Who is calling?", None),
                ("a", "I am Ms. Lan from the school.", None),
                ("b", "Oh, hello, Ms. Lan. What is the news?", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "Hello! This is Ms. Hoa calling from the school.", None),
                ("b", "Hello, Ms. Hoa! What happened?", None),
                ("a", "Nam was absent yesterday. Is he better today?", None),
                ("b", "Yes, he is better. He will come to school tomorrow.", None),
                ("a", "Please tell him to bring his homework.", None),
                ("b", "I will. Thank you for calling.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Hello, this is Mr. Minh. Can I speak to the principal?", None),
                ("b", "Sorry, the principal is busy right now.", None),
                ("a", "Can I leave a message, please?", None),
                ("b", "Of course. What is the message?", None),
                ("a", "Please tell her to call me about Friday's meeting.", None),
                ("b", "I will pass on the message. Goodbye!", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Good afternoon. This is Ms. Trang. I have an urgent matter.", None),
                ("b", "Please tell me. What is the urgent matter?", None),
                ("a", "I need to confirm the session time for tomorrow afternoon.", None),
                ("b", "Let me check. The session starts at two o'clock.", None),
                ("a", "Thank you. Please also leave a message for the vice-principal.", None),
                ("b", "Certainly. I will send an email confirmation as well.", None),
                ("a", "I would have called earlier, but I was in a meeting.", None),
                ("b", "No problem at all. I appreciate your quick follow-up.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I am calling to apologise for the delay in sending the report.", None),
                ("b", "No problem. I understand you were very busy last week.", None),
                ("a", "I will submit the completed report by tomorrow morning.", None),
                ("b", "Thank you. Could you also send a digital copy by email?", None),
                ("a", "Of course. I will attach it to my email tonight.", None),
                ("b", "If you had called earlier, I would have helped you.", None),
                ("a", "I understand. I should have contacted you sooner.", None),
                ("b", "No need to worry. I look forward to receiving the report.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_health": {
        "starters": [
            [   # Variant A — 4 lines (patient + doctor)
                ("a", "Hello, doctor! I feel bad today.", "(touching forehead)"),
                ("b", "Hello! How are you?", None),
                ("a", "I am not fine. I have a headache.", None),
                ("b", "Take this medicine and rest at home.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Good morning, doctor. I am not fine.", None),
                ("b", "Good morning! What is the problem?", None),
                ("a", "I am very tired.", None),
                ("b", "Okay. Drink water and rest well.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "He is sick today. He has a fever.", None),
                ("b", "I understand. When did the fever start?", None),
                ("a", "It started yesterday afternoon.", None),
                ("b", "He should stay at home and drink warm water.", None),
                ("a", "Should I bring him to the clinic tomorrow?", None),
                ("b", "Yes, bring him if the fever does not go down.", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Good morning, doctor. I have a stomach ache.", None),
                ("b", "I am sorry to hear that. How long have you had it?", None),
                ("a", "I had it since this morning.", None),
                ("b", "Did you eat breakfast today?", None),
                ("a", "Yes, but I ate too quickly.", None),
                ("b", "Drink warm water and rest. I will give you some medicine.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Good morning. I have a terrible headache and a high fever.", None),
                ("b", "I am sorry to hear that. How long have you had these symptoms?", None),
                ("a", "The fever started two days ago and has not improved.", None),
                ("b", "I see. I will write a prescription for you.", None),
                ("a", "Should I describe any other symptoms?", None),
                ("b", "Yes, do you have a sore throat or difficulty breathing?", None),
                ("a", "No, just the headache and fever.", None),
                ("b", "Please take the medicine after meals and rest completely.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "I need to confirm my medical appointment for this afternoon.", None),
                ("b", "Of course. Your appointment is at three thirty.", None),
                ("a", "I also need to pick up my prescription from last week.", None),
                ("b", "The doctor wrote a prescription for your ongoing condition.", None),
                ("a", "Thank you. Should I describe my current symptoms again?", None),
                ("b", "Yes, please. The doctor will review everything today.", None),
                ("a", "If I had rested more, I would have recovered faster.", None),
                ("b", "Please take better care of your health from now on.", None),
            ]
        ]
    },

    # ──────────────────────────────────────────────────────────────────
    "topic_social": {
        "starters": [
            [   # Variant A — 5 lines (friend + friend)
                ("a", "Hello! How are you today?", "(waving)"),
                ("b", "Hello! I am fine, thank you.", None),
                ("a", "I am good too. The morning is very nice.", None),
                ("b", "Yes! I like mornings. Goodbye!", None),
                ("a", "Goodbye! See you tomorrow.", None),
            ],
            [   # Variant B — 4 lines
                ("a", "Good morning! I am fine today.", None),
                ("b", "Good morning! I am happy too.", None),
                ("a", "I like this weather. It is very good.", None),
                ("b", "Yes! Goodbye, see you later.", None),
            ]
        ],
        "movers": [
            [   # Variant A — 6 lines
                ("a", "The weather is very nice today, isn't it?", None),
                ("b", "Yes! Yesterday I walked to school in the rain.", None),
                ("a", "Really? I stayed home and read a book.", None),
                ("b", "Can you help me plan our picnic for Saturday?", None),
                ("a", "Sure! I want to buy fruit and sandwiches.", None),
                ("b", "That sounds great. See you on Saturday!", None),
            ],
            [   # Variant B — 6 lines
                ("a", "Hello! How was your weekend?", None),
                ("b", "It was great! I went to the park with my family.", None),
                ("a", "That is wonderful. The weather was very nice on Sunday.", None),
                ("b", "Yes! I also helped my mother clean the house.", None),
                ("a", "I stayed home and watched an English film.", None),
                ("b", "Good idea! Let's meet for a walk next Saturday.", None),
            ]
        ],
        "advanced": [
            [   # Variant A — 8 lines
                ("a", "Gardening is my favourite hobby. What about you?", None),
                ("b", "I prefer reading and discussing ideas with friends.", None),
                ("a", "That is a great hobby. What topics do you enjoy?", None),
                ("b", "I enjoy books about history and social issues.", None),
                ("a", "I suggest we meet on Friday for a book club session.", None),
                ("b", "That is a wonderful idea. I look forward to it.", None),
                ("a", "Furthermore, we could invite some colleagues to join.", None),
                ("b", "If we had more time, we could meet every week.", None),
            ],
            [   # Variant B — 8 lines
                ("a", "What a lovely afternoon! How have you been lately?", None),
                ("b", "Very well, thank you. I have been quite busy with school.", None),
                ("a", "I understand. I have been working on a new project.", None),
                ("b", "What kind of project? It sounds interesting.", None),
                ("a", "I am developing new English activities for the students.", None),
                ("b", "Furthermore, a social event for teachers would be a great idea.", None),
                ("a", "I agree completely. Let's discuss the details over coffee.", None),
                ("b", "If I had known earlier, I would have planned something already.", None),
            ]
        ]
    },
}
```

---

## Task 4 — Viết lại `get_topic_content()`

Thay thế toàn bộ hàm `get_topic_content()` hiện tại:

```python
# Mapping topic → characters và settings
TOPIC_CONFIG = {
    "topic_before_class":         ("teacher", "colleague", "Teachers room"),
    "topic_in_class":             ("teacher", "student",   "Classroom"),
    "topic_giving_instructions":  ("teacher", "student",   "Classroom"),
    "topic_checking_understanding":("teacher","student",   "English lab"),
    "topic_praise_correction":    ("teacher", "student",   "Front of classroom"),
    "topic_school_communication": ("teacher", "parent",    "School meeting room"),
    "topic_market":               ("buyer",   "seller",    "Local market stall"),
    "topic_restaurant":           ("customer","waiter",    "Local restaurant"),
    "topic_travel":               ("traveler","agent",     "Bus terminal"),
    "topic_phone":                ("caller",  "receiver",  "Office, on the phone"),
    "topic_health":               ("patient", "doctor",    "School clinic"),
    "topic_social":               ("friend",  "friend",    "Park, sunny afternoon"),
}

CHAR_NAMES = {
    "teacher":   ["Ms. Lan", "Ms. Hoa", "Mr. Minh", "Ms. Trang", "Ms. Linh", "Mr. Binh", "Ms. Huong", "Mr. Duc"],
    "colleague": ["Mr. Minh", "Ms. Hoa", "Mr. Binh", "Ms. Trang"],
    "student":   ["Nam", "Lan", "An", "Vy", "Duy", "Khang", "Phong", "Trang"],
    "parent":    ["Mrs. Cuc", "Mr. Dung", "Mrs. Mai", "Mr. Hung"],
    "buyer":     ["Nam", "Lan", "An", "Vy"],
    "seller":    ["Seller"],
    "customer":  ["Nam", "Lan", "An"],
    "waiter":    ["Waiter"],
    "traveler":  ["Nam", "Lan", "An"],
    "agent":     ["Agent"],
    "caller":    ["Ms. Lan", "Ms. Hoa", "Mr. Minh", "Ms. Trang"],
    "receiver":  ["Partner"],
    "patient":   ["Nam", "Lan", "An", "Vy"],
    "doctor":    ["Doctor"],
    "friend":    ["Nam", "Lan", "An", "Vy"],
}

AI_CONFIG = {
    "topic_before_class":          ("colleague", "Talk about class preparation before the lesson starts."),
    "topic_in_class":              ("student",   "Ask questions during class about the lesson."),
    "topic_giving_instructions":   ("student",   "Ask for clarification about task instructions."),
    "topic_checking_understanding":("student",   "Confirm comprehension of the classroom rules."),
    "topic_praise_correction":     ("student",   "Receive feedback and correct a spelling error."),
    "topic_school_communication":  ("parent",    "Ask about student progress at parent-teacher meeting."),
    "topic_market":                ("seller",    "Bargain with a buyer at the market stall."),
    "topic_restaurant":            ("waiter",    "Take an order from a diner at a restaurant."),
    "topic_travel":                ("agent",     "Help a traveler book tickets and find directions."),
    "topic_phone":                 ("colleague", "Coordinate plans over the phone."),
    "topic_health":                ("doctor",    "Diagnose a patient's symptoms at the clinic."),
    "topic_social":                ("colleague", "Have casual chat about weekend plans."),
}

AI_OPENING = {
    "topic_before_class":          "Good morning! Have you finished the lesson preparation?",
    "topic_in_class":              "Teacher, can you help me? I don't understand the task.",
    "topic_giving_instructions":   "Teacher, should we open our books or start writing?",
    "topic_checking_understanding":"Teacher, are we supposed to explain or just write it?",
    "topic_praise_correction":     "Teacher, did I do a good job on my homework?",
    "topic_school_communication":  "Hello, teacher. I wanted to ask about my child's progress.",
    "topic_market":                "Fresh vegetables here! Would you like to buy some?",
    "topic_restaurant":            "Welcome! What would you like to order today?",
    "topic_travel":                "Hello! Where are you traveling to today?",
    "topic_phone":                 "Hello! This is Minh calling. Can we confirm the schedule?",
    "topic_health":                "Hello. Please sit down. What are your symptoms today?",
    "topic_social":                "Hi! What a nice day. What are your plans for the weekend?",
}

SUCCESS_CRITERIA = {
    "topic_before_class":          "Learner answers appropriately and describes a classroom preparation task.",
    "topic_in_class":              "Learner explains the task clearly using simple English.",
    "topic_giving_instructions":   "Learner gives clear, polite instructions using imperatives or modal verbs.",
    "topic_checking_understanding":"Learner checks understanding and gently clarifies rules.",
    "topic_praise_correction":     "Learner praises the student and guides correction of the mistake.",
    "topic_school_communication":  "Learner discusses student progress and provides constructive advice.",
    "topic_market":                "Learner asks for prices and negotiates politely.",
    "topic_restaurant":            "Learner orders food, states preferences, and asks for the bill.",
    "topic_travel":                "Learner asks for directions and travel booking help politely.",
    "topic_phone":                 "Learner coordinates plans and leaves a phone message successfully.",
    "topic_health":                "Learner describes symptoms clearly and asks for medical advice.",
    "topic_social":                "Learner makes friendly small talk and discusses personal hobbies.",
}

TOPIC_TITLE = {
    "topic_before_class":          "Preparing for class",
    "topic_in_class":              "Learning in the classroom",
    "topic_giving_instructions":   "Giving instructions",
    "topic_checking_understanding":"Checking understanding",
    "topic_praise_correction":     "Praise and correction",
    "topic_school_communication":  "School communication",
    "topic_market":                "At the market",
    "topic_restaurant":            "At the restaurant",
    "topic_travel":                "Travel and directions",
    "topic_phone":                 "Making a phone call",
    "topic_health":                "Health and the doctor",
    "topic_social":                "Social conversations",
}


def get_topic_content(lvl, topic_id, order, teacher, student, parent, vocab_items, grammar_items):
    import random as rnd

    # Xác định level group để chọn đúng template
    if lvl == "starters":
        level_group = "starters"
    elif lvl == "movers":
        level_group = "movers"
    else:
        level_group = "advanced"

    # Chọn variant A hoặc B theo thứ tự bài học
    variant_index = (order - 1) % 2

    # Lấy template từ DIALOGUE_BANK
    topic_templates = DIALOGUE_BANK.get(topic_id, {})
    group_templates = topic_templates.get(level_group, [])

    if not group_templates:
        # Fallback nếu topic chưa có trong bank
        group_templates = [[
            ("a", "Good morning! How are you today?", None),
            ("b", "I am fine, thank you.", None),
            ("a", "Let's start the lesson.", None),
            ("b", "Yes, I am ready.", None),
        ]]
    variant = group_templates[variant_index % len(group_templates)]

    # Lấy role của nhân vật từ TOPIC_CONFIG
    role_a, role_b, default_setting = TOPIC_CONFIG.get(topic_id, ("teacher", "student", "School"))

    # Gán tên nhân vật ngẫu nhiên từ pool
    name_a = rnd.choice(CHAR_NAMES.get(role_a, [teacher]))
    name_b_pool = [n for n in CHAR_NAMES.get(role_b, [student]) if n != name_a]
    name_b = rnd.choice(name_b_pool) if name_b_pool else student

    char_a = {"id": "char_a", "name": name_a, "role": role_a}
    char_b = {"id": "char_b", "name": name_b, "role": role_b}

    # Build dialogue lines
    lines = []
    for (char_key, text, note) in variant:
        char_id = "char_a" if char_key == "a" else "char_b"
        line = {"character_id": char_id, "text": text}
        if note:
            line["note"] = note
        lines.append(line)

    # Giờ settings
    time_of_day = ["Monday morning", "Tuesday morning", "Wednesday afternoon",
                   "Thursday morning", "Friday afternoon"]
    setting = f"{default_setting}, {time_of_day[(order - 1) % len(time_of_day)]}"

    # Title, scenario từ mapping + order number để tránh giống nhau
    title = TOPIC_TITLE.get(topic_id, topic_id.replace("topic_", "").replace("_", " ").title())
    scenario = f"You are in a {role_a.replace('_', ' ')} role. Use English naturally in this {topic_id.replace('topic_', '').replace('_', ' ')} situation."

    # AI conversation
    ai_role, ai_scenario_text = AI_CONFIG.get(topic_id, ("colleague", "Have a short English conversation."))
    ai_opening = AI_OPENING.get(topic_id, "Hello! How are you?")
    success = SUCCESS_CRITERIA.get(topic_id, "Learner completes the exchange successfully.")

    return title, scenario, setting, [char_a, char_b], lines, ai_role, ai_scenario_text, ai_opening, success
```

---

## Task 5 — HTML Pipeline: `update_html_portal()`

Thêm hàm sau vào cuối file, **trước** `if __name__ == "__main__":`:

```python
LEVEL_META = {
    "starters": {
        "title":    "Starters Level Lessons",
        "badge":    "Pre-A1 Starters",
        "subtitle": "Bản duyệt giáo án cấp độ Starters — Pre-A1 Cambridge.",
        "page_title": "Starters Lesson Review - TinySteps",
    },
    "movers": {
        "title":    "A1 Movers Level Lessons",
        "badge":    "A1 Movers",
        "subtitle": "Bản duyệt giáo án cấp độ Movers — A1 Cambridge.",
        "page_title": "Movers Lesson Review - TinySteps",
    },
    "flyers": {
        "title":    "A2 Flyers Level Lessons",
        "badge":    "A2 Flyers",
        "subtitle": "Bản duyệt giáo án cấp độ Flyers — A2 Cambridge.",
        "page_title": "Flyers Lesson Review - TinySteps",
    },
    "ket": {
        "title":    "B1 KET Level Lessons",
        "badge":    "B1 KET",
        "subtitle": "Bản duyệt giáo án cấp độ KET — B1 Cambridge.",
        "page_title": "KET Lesson Review - TinySteps",
    },
    "pet": {
        "title":    "B2 PET Level Lessons",
        "badge":    "B2 PET",
        "subtitle": "Bản duyệt giáo án cấp độ PET — B2 Cambridge.",
        "page_title": "PET Lesson Review - TinySteps",
    },
}


def update_html_portal(level, lessons, data_dir):
    """Inject lesson data vào HTML review portal cho một level."""
    import json as _json

    # Đọc template từ lessons-starters.html (có đầy đủ CSS + JS renderer)
    template_path = os.path.join(data_dir, "exports/lessons-starters.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    meta = LEVEL_META[level]

    # --- Thay thế level-specific text strings ---
    starters_meta = LEVEL_META["starters"]
    html = html.replace(starters_meta["page_title"], meta["page_title"])
    html = html.replace(starters_meta["title"],      meta["title"])
    html = html.replace(starters_meta["badge"],      meta["badge"])
    html = html.replace(starters_meta["subtitle"],   meta["subtitle"])
    # Fix badge trong JS template literal (dùng trong loadLessonContent)
    html = html.replace(
        "Pre-A1 Starters &bull; Order",
        f"{meta['badge']} &bull; Order"
    )

    # --- Inject lesson data ---
    data_json = _json.dumps(lessons, indent=2, ensure_ascii=False)

    # Tìm block "const lessonsData = [..." và "let currentLessonIndex"
    start_marker = "const lessonsData = ["
    end_marker   = "\n    let currentLessonIndex"

    start_pos = html.find(start_marker)
    end_pos   = html.find(end_marker, start_pos)

    if start_pos == -1 or end_pos == -1:
        print(f"  [WARNING] Không tìm thấy data markers trong HTML template cho level {level}")
        return

    new_data_block = f"const lessonsData = {data_json};"
    html = html[:start_pos] + new_data_block + html[end_pos:]

    # --- Ghi ra file output ---
    out_path = os.path.join(data_dir, f"exports/lessons-{level}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] {out_path} → {len(lessons)} lessons")


def load_all_lessons(level, data_dir):
    """Đọc tất cả file lesson JSON của một level theo thứ tự."""
    import json as _json
    lessons_dir = os.path.join(data_dir, f"lessons/{level}")
    if not os.path.isdir(lessons_dir):
        return []
    lesson_files = sorted(
        [f for f in os.listdir(lessons_dir) if f.startswith("lesson-") and f.endswith(".json")]
    )
    lessons = []
    for fname in lesson_files:
        with open(os.path.join(lessons_dir, fname), "r", encoding="utf-8") as f:
            lessons.append(_json.load(f))
    return lessons
```

---

## Task 6 — Cập nhật `main()`

Thay thế hàm `main()` hiện tại bằng:

```python
def main():
    print("=" * 60)
    print("TinySteps Automation Engine v2")
    print("=" * 60)

    # 1. Load registries
    with open(os.path.join(DATA_DIR, "topics/topics.json"), "r", encoding="utf-8") as f:
        topics_data = json.load(f)
    topics = topics_data["topics"]

    levels = ["starters", "movers", "flyers", "ket", "pet"]
    vocab   = {}
    grammar = {}

    for lvl in levels:
        with open(os.path.join(DATA_DIR, f"vocabulary/{lvl}.json"), "r", encoding="utf-8") as f:
            vocab[lvl] = json.load(f)["words"]
        with open(os.path.join(DATA_DIR, f"grammar/{lvl}.json"), "r", encoding="utf-8") as f:
            grammar[lvl] = json.load(f)["grammar_points"]

    teachers = ["Ms. Lan", "Ms. Hoa", "Mr. Minh", "Ms. Trang", "Ms. Linh", "Mr. Binh", "Ms. Huong", "Mr. Duc"]
    students = ["Nam", "Lan", "An", "Vy", "Duy", "Khang", "Phong", "Binh", "Trang"]
    parents  = ["Mrs. Cuc", "Mr. Dung", "Mrs. Mai", "Mr. Hung", "Mrs. Phuong", "Mr. Thanh"]

    lesson_quantities = {
        "starters": 30,
        "movers":   30,
        "flyers":   40,
        "ket":      35,
        "pet":      40
    }

    # 2. Generate lesson JSON files
    print("\n[PHASE 1] Generating lesson JSON files...")
    for lvl in levels:
        lvl_vocab   = vocab[lvl]
        lvl_grammar = grammar[lvl]
        target_count = lesson_quantities[lvl]
        start_order  = 6 if lvl == "starters" else 1

        os.makedirs(os.path.join(DATA_DIR, f"lessons/{lvl}"), exist_ok=True)

        generated = 0
        for order in range(start_order, target_count + 1):
            topic_index = (order - 1) % len(topics)
            topic = topics[topic_index]
            topic_id = topic["id"]

            matching_vocab   = [v for v in lvl_vocab if topic_id in v.get("topic_ids", [])]
            matching_grammar = [g for g in lvl_grammar if topic_id in g.get("topic_ids", [])]

            if not matching_vocab:
                matching_vocab = lvl_vocab[:6]
            if not matching_grammar:
                matching_grammar = [lvl_grammar[0]]

            # Đảm bảo đủ 6 vocab items
            lesson_vocab = matching_vocab[:8]
            if len(lesson_vocab) < 6:
                extras = [v for v in lvl_vocab if v not in lesson_vocab]
                lesson_vocab += extras[:6 - len(lesson_vocab)]

            lesson_grammar = matching_grammar[:2]
            vocab_ids      = [v["id"] for v in lesson_vocab]
            grammar_ids    = [g["id"] for g in lesson_grammar]

            import random as rnd
            char_teacher = rnd.choice(teachers)
            char_student = rnd.choice(students)
            char_parent  = rnd.choice(parents)

            estimated_minutes = {"starters": 4, "movers": 6, "flyers": 8, "ket": 10, "pet": 12}[lvl]
            max_sentence_length = {"starters": 6, "movers": 8, "flyers": 10, "ket": 12, "pet": 15}[lvl]

            title, scenario, setting, characters, lines, ai_role, ai_scenario, ai_opening, success_criteria = \
                get_topic_content(lvl, topic_id, order, char_teacher, char_student, char_parent, lesson_vocab, lesson_grammar)

            exercises     = generate_exercises(lvl, lesson_vocab, lesson_grammar)
            ai_conversation = {
                "role": ai_role,
                "scenario": ai_scenario,
                "opening_line": ai_opening,
                "level_constraints": {
                    "max_sentence_length": max_sentence_length,
                    "allowed_grammar":     grammar_ids,
                    "target_vocabulary":   vocab_ids[:3]
                },
                "success_criteria": success_criteria
            }

            lesson_data = {
                "id":               f"{lvl}_lesson_{order:03d}",
                "level":            lvl,
                "topic_id":         topic_id,
                "order":            order,
                "title":            title,
                "scenario":         scenario,
                "estimated_minutes": estimated_minutes,
                "dialogue": {
                    "setting":    setting,
                    "characters": characters,
                    "lines":      lines
                },
                "vocabulary_ids": vocab_ids,
                "grammar_ids":    grammar_ids,
                "exercises":      exercises,
                "ai_conversation": ai_conversation
            }

            filename = os.path.join(DATA_DIR, f"lessons/{lvl}/lesson-{order:03d}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(lesson_data, f, indent=2, ensure_ascii=False)
            generated += 1

        print(f"  [OK] {lvl}: {generated} new lessons generated")

    # 3. Update HTML portal
    print("\n[PHASE 2] Updating HTML Review Portal...")
    for lvl in levels:
        lessons = load_all_lessons(lvl, DATA_DIR)
        if lessons:
            update_html_portal(lvl, lessons, DATA_DIR)
        else:
            print(f"  [SKIP] {lvl}: no lesson files found")

    print("\n[DONE] All tasks completed successfully!")
    print("Open tinysteps-data/exports/index.html to review.")
```

---

## Validation Checklist

Sau khi chạy script, kiểm tra các mục sau:

### Kiểm tra tự động (chạy trên terminal)
```bash
# 1. Đếm số file JSON đã tạo
find tinysteps-data/lessons -name "*.json" | sort | wc -l
# Kết quả mong đợi: 180

# 2. Kiểm tra cross-references không bị hỏng
python3 - <<'EOF'
import json, os

DATA = "tinysteps-data"
all_vocab, all_grammar = set(), set()
for lvl in ["starters","movers","flyers","ket","pet"]:
    all_vocab   |= {w["id"] for w in json.load(open(f"{DATA}/vocabulary/{lvl}.json"))["words"]}
    all_grammar |= {g["id"] for g in json.load(open(f"{DATA}/grammar/{lvl}.json"))["grammar_points"]}

broken = []
for root, _, files in os.walk(f"{DATA}/lessons"):
    for fname in files:
        if not fname.endswith(".json"): continue
        lesson = json.load(open(os.path.join(root, fname)))
        for vid in lesson["vocabulary_ids"]:
            if vid not in all_vocab:
                broken.append((fname, "vocab", vid))
        for gid in lesson["grammar_ids"]:
            if gid not in all_grammar:
                broken.append((fname, "grammar", gid))

print(f"Broken refs: {len(broken)}")
for b in broken[:10]: print(" ", b)
EOF

# 3. Kiểm tra tất cả 5 loại exercise có đủ không
python3 - <<'EOF'
import json, os

REQUIRED = {"match","arrange","listen_choose","fill_blank","multiple_choice"}
missing = []
for root, _, files in os.walk("tinysteps-data/lessons"):
    for fname in sorted(files):
        if not fname.endswith(".json"): continue
        lesson = json.load(open(os.path.join(root, fname)))
        types = {e["type"] for e in lesson["exercises"]}
        if types != REQUIRED:
            missing.append((fname, REQUIRED - types))

print(f"Lessons missing exercise types: {len(missing)}")
for m in missing[:5]: print(" ", m)
EOF

# 4. Kiểm tra HTML files đã được cập nhật
for lvl in starters movers flyers ket pet; do
    count=$(python3 -c "
import re, sys
html = open('tinysteps-data/exports/lessons-${lvl}.html').read()
m = re.findall(r'\"order\":', html)
print(len(m))
")
    echo "lessons-${lvl}.html: ${count} lessons embedded"
done
```

### Kiểm tra thủ công trên trình duyệt
1. Mở `tinysteps-data/exports/index.html` — kiểm tra navigation links
2. Mở `tinysteps-data/exports/lessons-starters.html` — kiểm tra:
   - Tab navigation hiển thị đúng số lượng bài học
   - Dialogue lines không chứa văn bản vô nghĩa (kiểm tra 3-4 bài ngẫu nhiên)
   - Exercise items không chứa `not_`, `bad_`, hoặc câu bị cắt đứt
   - Nút "Show Answers" / "Hide Answers" hoạt động
   - In trang (`Ctrl+P`) hiển thị layout sạch
3. Lặp lại bước 2 cho `lessons-movers.html`
