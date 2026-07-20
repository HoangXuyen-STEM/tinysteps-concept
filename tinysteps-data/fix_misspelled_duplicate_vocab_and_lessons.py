#!/usr/bin/env python3
"""
Sửa hai mục từ vựng Movers sai chính tả và mọi bài học đang dùng chúng.

Bối cảnh: `progresss` (movers_vocab_014) và `guideliness` (movers_vocab_019) là bản
sai chính tả của `progress` (movers_vocab_021) và `guidelines` (movers_vocab_022) —
các từ đúng ĐÃ tồn tại cùng cấp. Vì mỗi từ chỉ được xuất hiện một lần trên toàn bộ
5 cấp độ, không thể sửa chính tả tại chỗ; phải thay bằng từ mới, giữ nguyên id để
không mồ côi srs_cards của người đang học.

Từ thay được chọn theo chủ đề của mục cũ và phải vẽ minh họa Match được mà KHÔNG cần
chữ trong tranh (ràng buộc của prompt pack ảnh):
- movers_vocab_014 (topic_praise_correction)  → sticker (hình dán khen thưởng)
- movers_vocab_019 (topic_giving_instructions) → arrow  (mũi tên chỉ dẫn)

Script sửa cả vocabulary/movers.json lẫn 6 file bài học tham chiếu từ cũ trong bài tập
match/multiple_choice, để đáp án bài tập luôn khớp từ vựng của cấp.

Chạy: python3 tinysteps-data/fix_misspelled_duplicate_vocab_and_lessons.py [--apply]
"""

import glob
import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

VOCAB_FIXES = {
    "movers_vocab_014": {
        "word": "sticker",
        "ipa": "/ˈstɪk.ər/",
        "pos": "noun",
        "example_sentence": "You get a sticker today!",
        "image_hint": "a shiny gold star sticker on a notebook page",
    },
    "movers_vocab_019": {
        "word": "arrow",
        "ipa": "/ˈær.əʊ/",
        "pos": "noun",
        "example_sentence": "Follow the arrow, please.",
        "image_hint": "a large bold arrow pointing to the right",
    },
}

# từ cũ → (từ mới, image_hint mới cho bài tập match)
WORD_MAP = {
    "progresss": ("sticker", "a shiny gold star sticker on a notebook page"),
    "guideliness": ("arrow", "a large bold arrow pointing to the right"),
}

# Prompt của multiple_choice nhúng nguyên văn image_hint cũ ("Look at the picture
# (a clean graphic illustration of a progress)...") nên phải thay cả cụm mô tả,
# không chỉ thay từ đáp án.
HINT_TEXT_MAP = {
    "a clean graphic illustration of a progress": "a shiny gold star sticker on a notebook page",
    "a clean graphic illustration of a guidelines": "a large bold arrow pointing to the right",
}


def fix_lesson(data: dict) -> list[str]:
    """Thay từ sai trong mọi bài tập của một bài học. Trả về mô tả thay đổi."""
    changes = []
    for exercise in data.get("exercises", []):
        for item in exercise.get("items", []):
            answer = item.get("correct_answer")
            if answer in WORD_MAP:
                new_word, new_hint = WORD_MAP[answer]
                item["correct_answer"] = new_word
                changes.append(f"{exercise['type']}.correct_answer: {answer} → {new_word}")
                # match dùng image_hint mô tả đáp án — hint cũ mô tả khái niệm cũ.
                if exercise["type"] == "match" and "image_hint" in item:
                    item["image_hint"] = new_hint
                    changes.append(f"match.image_hint → {new_hint!r}")
            options = item.get("options")
            if options:
                for i, opt in enumerate(options):
                    if opt in WORD_MAP:
                        options[i] = WORD_MAP[opt][0]
                        changes.append(f"{exercise['type']}.options[{i}]: {opt} → {options[i]}")
            prompt = item.get("prompt")
            if prompt:
                for old_hint, new_hint in HINT_TEXT_MAP.items():
                    if old_hint in prompt:
                        item["prompt"] = prompt.replace(old_hint, new_hint)
                        changes.append(f"{exercise['type']}.prompt: hint cũ → {new_hint!r}")
    return changes


def main() -> int:
    apply = "--apply" in sys.argv

    vocab_path = os.path.join(DATA_DIR, "vocabulary", "movers.json")
    with open(vocab_path, encoding="utf-8") as fh:
        vocab = json.load(fh)
    for entry in vocab["words"]:
        fixes = VOCAB_FIXES.get(entry["id"])
        if fixes:
            for field, value in fixes.items():
                print(f"  {entry['id']}.{field}: {entry.get(field)!r} → {value!r}")
                entry[field] = value
    if apply:
        with open(vocab_path, "w", encoding="utf-8") as fh:
            json.dump(vocab, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"  → đã ghi {vocab_path}")

    for lesson_path in sorted(glob.glob(os.path.join(DATA_DIR, "lessons", "*", "*.json"))):
        with open(lesson_path, encoding="utf-8") as fh:
            data = json.load(fh)
        changes = fix_lesson(data)
        if not changes:
            continue
        print(f"  {data['id']}:")
        for change in changes:
            print(f"    {change}")
        if apply:
            with open(lesson_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")

    print()
    print("ĐÃ GHI." if apply else "DRY RUN — chạy lại với --apply để ghi.")
    if apply:
        print("Việc tiếp theo bắt buộc:")
        print("  1. Xoá 4 file audio của movers_vocab_014/019 rồi chạy generate_audio.py")
        print("  2. Chạy generate_match_illustration_queue.py để queue ảnh dùng từ mới")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
