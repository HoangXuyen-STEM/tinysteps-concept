#!/usr/bin/env python3
"""
Sửa lỗi do lớp soi chính tả (aspell) phát hiện — các lỗi mà soi từ loại và soi artifact
đều bỏ sót vì từ nằm đúng ô ngữ pháp, chỉ sai cách viết:

1. Ba từ vựng hỏng, thay bằng từ mới (từ đúng chưa ai dùng, giữ nguyên id):
   - ket_vocab_151  'maitre'     → 'buffet'    (thiếu dấu và cụt của "maître d'")
   - ket_vocab_277  'satisf'     → 'photocopy' (từ bị cụt của "satisfy")
   - flyers_vocab_497 'operabilty' → 'whisper' (viết sai "operability" — mà từ đó cũng
     không hợp làm từ vựng A2 trong lớp học)

2. Mười bốn câu ví dụ chia động từ sai — sửa xác định theo luật chính tả tiếng Anh:
   carryed→carried (y→ied), claped→clapped (gấp đôi phụ âm), fryed→fried,
   hited→hit (bất quy tắc), stired→stirred, proofreaded→proofread,
   submited→submitted, và 8 dạng V-ing không bỏ e: authenticateing→authenticating…

Chạy: python3 tinysteps-data/fix_spelling_and_inflection_in_examples.py [--apply]
"""

import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(DATA_DIR, "vocabulary")

WORD_FIXES = {
    "ket_vocab_151": {
        "word": "buffet",
        "ipa": "/ˈbʊf.eɪ/",
        "pos": "noun",
        "example_sentence": "The hotel serves a breakfast buffet.",
        "image_hint": "a long table with covered dishes at a hotel breakfast",
    },
    "ket_vocab_277": {
        "word": "photocopy",
        "ipa": "/ˈfəʊ.təʊˌkɒp.i/",
        "pos": "verb",
        "example_sentence": "Could you photocopy this worksheet for me?",
        "image_hint": "a copy machine with a page coming out",
    },
    "flyers_vocab_497": {
        "word": "whisper",
        "ipa": "/ˈwɪs.pər/",
        "pos": "verb",
        "example_sentence": "Please don't whisper during the test.",
        "image_hint": "two pupils leaning close, one hand cupped to an ear",
    },
}

# Câu ví dụ mới cho các mục chia động từ sai. Câu gốc kiểu "She carryed yesterday."
# ngoài chia sai còn thiếu tân ngữ cho động từ cần tân ngữ — viết lại trọn câu.
SENTENCE_FIXES = {
    # movers (tối đa 7 từ)
    "carryed": "She carried my bag yesterday.",
    "claped": "She clapped for the winner.",
    "fryed": "She fried eggs this morning.",
    "hited": "She hit the ball hard.",
    "stired": "She stirred the soup slowly.",
    # flyers (tối đa 10 từ)
    "proofreaded": "She has already proofread the essay.",
    "submited": "She has already submitted the form.",
    # ket (tối đa 12 từ) — giữ khung "I have been Xing since Monday."
    "authenticateing": "I have been authenticating since Monday.",
    "differentiateing": "I have been differentiating since Monday.",
    "incorporateing": "I have been incorporating since Monday.",
    "integrateing": "I have been integrating since Monday.",
    "mediateing": "I have been mediating since Monday.",
    "overcomeing": "I have been overcoming since Monday.",
    "sequenceing": "I have been sequencing since Monday.",
    "synchroniseing": "I have been synchronising since Monday.",
}


def main() -> int:
    apply = "--apply" in sys.argv
    changed = []

    for filename in sorted(os.listdir(VOCAB_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(VOCAB_DIR, filename)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        touched = False
        for entry in data["words"]:
            if entry["id"] in WORD_FIXES:
                for field, value in WORD_FIXES[entry["id"]].items():
                    if entry.get(field) != value:
                        print(f"  {entry['id']}.{field}: {entry.get(field)!r} → {value!r}")
                        entry[field] = value
                        touched = True
                changed.append((entry["id"], "word+sentence"))
                continue
            for broken, fixed_sentence in SENTENCE_FIXES.items():
                if broken in entry["example_sentence"]:
                    print(f"  {entry['id']}: {entry['example_sentence']!r} → {fixed_sentence!r}")
                    entry["example_sentence"] = fixed_sentence
                    changed.append((entry["id"], "sentence"))
                    touched = True

        if touched and apply:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            print(f"  → đã ghi {path}")

    print()
    print(f"{'ĐÃ SỬA' if apply else 'DRY RUN'}: {len(changed)} mục.")
    if apply:
        print("Audio cần xoá rồi sinh lại:")
        for vocab_id, kind in changed:
            level = vocab_id.split("_")[0]
            print(f"  audio/vocabulary/{level}/{vocab_id}_sentence.mp3")
            if kind == "word+sentence":
                print(f"  audio/vocabulary/{level}/{vocab_id}_word.mp3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
