#!/usr/bin/env python3
"""
Test cho lesson_content_checks — cùng triết lý với test_vocabulary_grammar_checks:
nửa "phải bắt" là lỗi thật đã từng gặp trong dữ liệu, nửa "phải bỏ qua" là nội dung
hợp lệ mà một rule cẩu thả sẽ báo nhầm.

Chạy: python3 tinysteps-data/test_lesson_content_checks.py
"""

from lesson_content_checks import check_lesson, check_grammar_point, scan_text

LEVEL_WORDS = {"hello", "morning", "teacher", "sticker", "arrow"}
VOCAB_IDS = {"movers_vocab_001"}
GRAMMAR_IDS = {"movers_grammar_001"}


def lesson(**overrides):
    """Bài học hợp lệ tối thiểu; overrides tiêm lỗi cần test."""
    base = {
        "id": "test_lesson",
        "vocabulary_ids": ["movers_vocab_001"],
        "grammar_ids": ["movers_grammar_001"],
        "dialogue": {"lines": [{"text": "Good morning! How are you?"}]},
        "exercises": [
            {
                "type": "match",
                "instruction": "Match the picture with the correct word.",
                "items": [{"image_hint": "a gold star sticker", "correct_answer": "sticker"}],
            },
            {
                "type": "arrange",
                "instruction": "Put the words in the correct order.",
                "items": [{"words": ["I", "am", "a", "teacher", "."],
                           "correct_answer": "I am a teacher."}],
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the best answer.",
                "items": [{"prompt": "What is this?", "options": ["hello", "arrow"],
                           "correct_answer": "arrow"}],
            },
            {
                "type": "listen_choose",
                "instruction": "Listen and choose.",
                "items": [{"audio_text": "Good morning!", "options": ["Good morning!", "Hello!"],
                           "correct_answer": "Good morning!"}],
            },
            {
                "type": "fill_blank",
                "instruction": "Fill in the missing word.",
                "items": [{"prompt": "I ___ a teacher.", "correct_answer": "am"}],
            },
        ],
    }
    base.update(overrides)
    return base


def run_lesson(data):
    return check_lesson(data, LEVEL_WORDS, VOCAB_IDS, GRAMMAR_IDS)


def main() -> int:
    failures = []

    # ---------- Phải KHÔNG có lỗi ----------
    clean = run_lesson(lesson())
    if clean:
        failures.append(f"bài học hợp lệ bị báo lỗi: {clean[0]}")

    ok_grammar = check_grammar_point({
        "id": "g1",
        "examples": [{"sentence": "Open your book."}],
        # Vế "wrong" cố tình sai — không được soi.
        "common_mistakes": [{"wrong": "You open book.", "correct": "Open your book."}],
    })
    if ok_grammar:
        failures.append(f"grammar hợp lệ bị báo lỗi: {ok_grammar[0]}")

    # "had had" là tiếng Anh đúng — không được báo từ lặp.
    if scan_text("t", "She had had lunch already."):
        failures.append("báo nhầm 'had had'")
    # "succeeded" là từ thật — không được dính luật -eed.
    if scan_text("t", "She succeeded in the exam."):
        failures.append("báo nhầm 'succeeded'")

    # ---------- Phải BẮT được ----------
    must_flag = [
        # (mô tả, lesson bị tiêm lỗi)
        ("match dùng từ ngoài cấp (guideliness)", lesson(exercises=[{
            "type": "match", "instruction": "Match.",
            "items": [{"image_hint": "x", "correct_answer": "guideliness"}]}])),
        ("arrange thiếu mảnh từ", lesson(exercises=[{
            "type": "arrange", "instruction": "Arrange.",
            "items": [{"words": ["I", "am"], "correct_answer": "I am a teacher."}]}])),
        ("đáp án MC ngoài lựa chọn", lesson(exercises=[{
            "type": "multiple_choice", "instruction": "Choose.",
            "items": [{"prompt": "?", "options": ["a", "b"], "correct_answer": "c"}]}])),
        ("lựa chọn trùng nhau", lesson(exercises=[{
            "type": "multiple_choice", "instruction": "Choose.",
            "items": [{"prompt": "?", "options": ["a", "a"], "correct_answer": "a"}]}])),
        ("audio_text khác đáp án", lesson(exercises=[{
            "type": "listen_choose", "instruction": "Listen.",
            "items": [{"audio_text": "Hello!", "options": ["Hi!"], "correct_answer": "Hi!"}]}])),
        ("fill_blank không có chỗ trống", lesson(exercises=[{
            "type": "fill_blank", "instruction": "Fill.",
            "items": [{"prompt": "I am a teacher.", "correct_answer": "am"}]}])),
        ("vocabulary_id không tồn tại", lesson(vocabulary_ids=["movers_vocab_999"])),
        ("hội thoại chứa 'thinked'", lesson(
            dialogue={"lines": [{"text": "She thinked about it."}]})),
        ("hội thoại chứa 'motivateed'", lesson(
            dialogue={"lines": [{"text": "She has already motivateed."}]})),
    ]
    for description, bad_lesson in must_flag:
        if not run_lesson(bad_lesson):
            failures.append(f"BỎ SÓT: {description}")

    bad_grammar = check_grammar_point({
        "id": "g2",
        "examples": [{"sentence": "She singed a song."}],
        "common_mistakes": [{"wrong": "Same.", "correct": "Same."}],
    })
    if len(bad_grammar) < 2:
        failures.append("BỎ SÓT: grammar 'singed' hoặc wrong==correct")

    total = 4 + len(must_flag) + 1
    if failures:
        print(f"❌ {len(failures)}/{total} trường hợp sai:")
        for line in failures:
            print(f"   {line}")
        return 1
    print(f"✓ {total} trường hợp đúng (bắt đủ lỗi tiêm vào, không báo nhầm nội dung hợp lệ).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
