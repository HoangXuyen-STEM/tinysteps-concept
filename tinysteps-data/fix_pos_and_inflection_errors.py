#!/usr/bin/env python3
"""
Sửa các mục từ vựng do vocabulary_grammar_checks.py phát hiện: câu ví dụ đặt từ vào sai
vị trí ngữ pháp, và dạng chia động từ bị bộ sinh tạo sai.

Hai nhóm được xử lý khác nhau:

1. Chia động từ sai ("motivateed", "builded") — sửa TỰ ĐỘNG được, vì dạng đúng tra ra từ
   bảng IRREGULAR hoặc luật "từ tận cùng bằng e thì chỉ thêm d". Đây là tra bảng chứ
   không phải đoán, khác hẳn bộ sinh ban đầu.

2. Sai từ loại theo vị trí ("Answer the hear.") — không có phép biến đổi máy móc nào
   đúng được, nên mọi câu thay thế bên dưới đều viết tay, bám ngữ cảnh lớp học và tuân
   thủ giới hạn số từ theo cấp (starters 5, movers 7, flyers 10, ket 12, pet 15).

Chạy: python3 tinysteps-data/fix_pos_and_inflection_errors.py [--apply]
"""

import json
import os
import re
import sys

from vocabulary_grammar_checks import IRREGULAR

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(DATA_DIR, "vocabulary")

# Câu viết tay cho các mục sai từ loại. id -> câu ví dụ mới.
SENTENCE_FIXES = {
    # ----- STARTERS (tối đa 5 từ) -----
    "starters_vocab_025": "We walk to school.",
    "starters_vocab_038": "Please repeat after me.",
    "starters_vocab_045": "I can hear you.",
    "starters_vocab_047": "Please talk to me.",
    "starters_vocab_051": "Please work quietly.",
    "starters_vocab_055": "The water is cold.",
    "starters_vocab_061": "Please contact the school.",
    "starters_vocab_073": "Can you translate this?",
    "starters_vocab_075": "She is helping me.",
    "starters_vocab_079": "We travel by bus.",
    "starters_vocab_080": "Please call the doctor.",
    "starters_vocab_086": "I want to improve.",
    "starters_vocab_105": "Can you pronounce this?",
    "starters_vocab_107": "I am not sure.",
    "starters_vocab_112": "I drive to school.",
    "starters_vocab_114": "She is walking home.",
    "starters_vocab_116": "He is suggesting something.",
    "starters_vocab_120": "They are talking now.",
    "starters_vocab_125": "I am contacting her.",
    "starters_vocab_130": "We are traveling today.",

    # ----- MOVERS (tối đa 7 từ) -----
    # "urgent-new" và "official-new" là rác do bộ sinh ghép thêm hậu tố "-new".
    "movers_vocab_013": "Answer the urgent call now.",
    "movers_vocab_015": "I prepared the official report.",

    # ----- PET (tối đa 15 từ) -----
    "pet_vocab_014": "You should review the lesson plan before class.",
    "pet_vocab_028": "I could not find the register this morning.",
    "pet_vocab_029": "Press the button to start the recording.",
    "pet_vocab_034": "Please underline the key words in each sentence.",
    "pet_vocab_036": "I will share the handout with the whole department.",
    "pet_vocab_041": "We meet every Monday to plan the week.",
    "pet_vocab_043": "She is explaining the task to a small group.",
    "pet_vocab_044": "Please stand near the board so everyone can see.",
    "pet_vocab_064": "Write one sentence about your favourite subject.",
    "pet_vocab_065": "Match each word with the correct picture.",
    "pet_vocab_066": "The students looked confused after the first explanation.",
    "pet_vocab_067": "Please be careful with the laboratory equipment.",
    "pet_vocab_071": "We fly to the conference on Sunday morning.",
    "pet_vocab_090": "We chat briefly in the staff room each morning.",
    "pet_vocab_092": "Bring a pencil and a notebook to the exam.",
    "pet_vocab_093": "Please copy the diagram into your notebook.",
    "pet_vocab_094": "Decide whether each statement is true or false.",
    "pet_vocab_101": "The children laugh whenever I mispronounce a word.",
    "pet_vocab_105": "Please check your answers before you hand them in.",
    "pet_vocab_109": "I am finding it easier to speak in English.",
    "pet_vocab_115": "He is standing beside the whiteboard.",
    "pet_vocab_116": "She is matching the words with the pictures.",
    "pet_vocab_118": "I am relaxing after a long teaching day.",
    "pet_vocab_123": "The pupils are copying the notes into their books.",
    "pet_vocab_124": "The whole class is laughing at my joke.",
    "pet_vocab_126": "I am checking the homework this evening.",
}

# Mục cần sửa cả chính tả của từ, không chỉ câu ví dụ.
WORD_FIXES = {
    # Số nhiều của danh từ tận cùng phụ âm + y phải là -ies.
    "pet_vocab_062": {
        "word": "hobbies",
        "ipa": "/ˈhɒb.iz/",
        "example_sentence": "We talked about our hobbies during the break.",
    },
}


def correct_past_form(word: str) -> str | None:
    """Dạng quá khứ đúng cho một động từ bị bộ sinh chia thành word + 'ed'."""
    word_l = word.lower()
    if word_l in IRREGULAR:
        return IRREGULAR[word_l][0]
    if word_l.endswith("e"):
        return word_l + "d"
    return None


def main() -> int:
    apply = "--apply" in sys.argv
    changed = 0

    for filename in sorted(os.listdir(VOCAB_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(VOCAB_DIR, filename)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        touched = False
        for entry in data["words"]:
            entry_id = entry["id"]

            if entry_id in WORD_FIXES:
                for field, value in WORD_FIXES[entry_id].items():
                    if entry.get(field) != value:
                        print(f"  {entry_id}.{field}: {entry.get(field)!r} → {value!r}")
                        entry[field] = value
                        touched = True
                changed += 1
                continue

            if entry_id in SENTENCE_FIXES:
                new_sentence = SENTENCE_FIXES[entry_id]
                if entry["example_sentence"] != new_sentence:
                    print(f"  {entry_id}: {entry['example_sentence']!r} → {new_sentence!r}")
                    entry["example_sentence"] = new_sentence
                    touched = True
                changed += 1
                continue

            # Chia động từ sai: thay dạng "word+ed" bằng dạng đúng tra từ bảng.
            broken = entry["word"].lower() + "ed"
            if re.search(rf"\b{re.escape(broken)}\b", entry["example_sentence"], re.IGNORECASE):
                fixed = correct_past_form(entry["word"])
                if fixed:
                    new_sentence = re.sub(
                        rf"\b{re.escape(broken)}\b", fixed,
                        entry["example_sentence"], flags=re.IGNORECASE,
                    )
                    print(f"  {entry_id}: {entry['example_sentence']!r} → {new_sentence!r}")
                    entry["example_sentence"] = new_sentence
                    touched = True
                    changed += 1

        if touched and apply:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            print(f"  → đã ghi {path}")

    print()
    print(f"{'ĐÃ SỬA' if apply else 'DRY RUN'}: {changed} mục.")
    if not apply:
        print("Chạy lại với --apply để ghi thay đổi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
