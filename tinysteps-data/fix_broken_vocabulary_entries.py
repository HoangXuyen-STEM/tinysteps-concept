#!/usr/bin/env python3
"""
Sửa các mục từ vựng sai được sinh tự động.

Nguyên nhân gốc: bộ sinh dữ liệu ghép từ vào mẫu câu mà không xét từ loại, tạo ra
câu sai ngữ pháp ("Look at the help.") và cả từ không tồn tại ("musting" từ modal "must").

Mỗi bản sửa dưới đây được viết tay, không sinh tự động — sinh tự động chính là nguyên
nhân ban đầu. Câu thay thế tuân thủ giới hạn số từ theo cấp độ trong validate_data.py
(starters 5, movers 7, pet 15) và đúng từ loại của mục từ.

Chạy: python3 tinysteps-data/fix_broken_vocabulary_entries.py [--apply]
Không có --apply thì chỉ in ra thay đổi dự kiến (dry run).
"""

import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(DATA_DIR, "vocabulary")

# id -> các trường cần ghi đè. Chỉ ghi đè trường có mặt, các trường khác giữ nguyên.
FIXES = {
    # ---------- STARTERS: câu ví dụ sai từ loại (tối đa 5 từ) ----------
    "starters_vocab_016": {"example_sentence": "Can you help me?"},
    "starters_vocab_018": {"example_sentence": "I comprehend the lesson."},
    "starters_vocab_019": {"example_sentence": "That is very nice!"},
    "starters_vocab_021": {"example_sentence": "I want to buy rice."},
    "starters_vocab_028": {"example_sentence": "Can I suggest something?"},
    "starters_vocab_039": {"example_sentence": "That is true."},
    "starters_vocab_050": {"example_sentence": "Turn to page ten."},
    "starters_vocab_074": {"example_sentence": "Circle the correct answer."},
    "starters_vocab_085": {"example_sentence": "Please sit down."},
    "starters_vocab_091": {"example_sentence": "We must cancel class."},
    "starters_vocab_096": {"example_sentence": "Please verify your answer."},
    "starters_vocab_106": {"example_sentence": "Color the picture, please."},
    "starters_vocab_119": {"example_sentence": "She is repeating the word."},
    "starters_vocab_121": {"example_sentence": "He is turning the page."},
    "starters_vocab_135": {"example_sentence": "I am verifying the answers."},
    "starters_vocab_137": {"example_sentence": "They are coloring the picture."},

    # ---------- STARTERS: từ không tồn tại, thay bằng từ lớp học thật sự dùng ----------
    # Từ thay thế phải chưa xuất hiện ở BẤT KỲ cấp độ nào — validate_data.py bắt buộc
    # mỗi từ chỉ thuộc một cấp duy nhất.
    # "musting" sinh ra do gắn đuôi -ing vào modal "must".
    "starters_vocab_123": {
        "word": "wait",
        "ipa": "/weɪt/",
        "pos": "verb",
        "example_sentence": "Please wait for me.",
        "image_hint": "a pupil sitting patiently with hands folded on a desk",
    },
    # "siting" là lỗi chính tả của "sitting", mà "sit" thì đã có rồi.
    "starters_vocab_132": {
        "word": "spell",
        "ipa": "/spel/",
        "pos": "verb",
        "example_sentence": "Spell your name, please.",
        "image_hint": "a hand writing letters of a name on a blackboard",
    },

    # ---------- Câu ví dụ không chứa chính từ đang dạy ----------
    # "I cleaned the board." không hề nhắc tới eraser; "Submit by the deadline." dùng
    # động từ submit thay cho danh từ submission.
    "movers_vocab_026": {"example_sentence": "The eraser is on the desk."},
    "ket_vocab_033": {"example_sentence": "Your submission arrived before the deadline."},

    # ---------- MOVERS: giới từ bị nhét vào mẫu danh từ (tối đa 7 từ) ----------
    "movers_vocab_335": {"example_sentence": "The bag is below the desk."},
    "movers_vocab_336": {"example_sentence": "Sit between Nam and Lan."},
    "movers_vocab_338": {"example_sentence": "She sits beside the window."},
    "movers_vocab_339": {"example_sentence": "We sat around the table."},
    "movers_vocab_341": {"example_sentence": "Walk along this road."},
    "movers_vocab_344": {"example_sentence": "Wait until the bell rings."},
    "movers_vocab_345": {"example_sentence": "I have taught since 2010."},
    "movers_vocab_346": {"example_sentence": "He walked towards the door."},

    # ---------- PET: từ không tồn tại / sai chính tả (tối đa 15 từ) ----------
    # Cùng ràng buộc duy nhất toàn cấp như phần Starters ở trên.
    # "prefering" thiếu một chữ r, và "prefer" đã nằm ở cấp KET.
    "pet_vocab_086": {
        "word": "assign",
        "ipa": "/əˈsaɪn/",
        "pos": "verb",
        "example_sentence": "I assign homework at the end of each lesson.",
        "image_hint": "a teacher handing worksheets to pupils",
    },
    # "shoulding" sinh ra do gắn -ing vào modal "should".
    "pet_vocab_107": {
        "word": "convey",
        "ipa": "/kənˈveɪ/",
        "pos": "verb",
        "example_sentence": "Try to convey the main idea in simple words.",
        "image_hint": "a teacher explaining with open hands to a listening class",
    },
    # "runing" thiếu một chữ n; "run" đã có sẵn.
    "pet_vocab_121": {
        "word": "emphasize",
        "ipa": "/ˈem.fə.saɪz/",
        "pos": "verb",
        "example_sentence": "I emphasize pronunciation during every speaking activity.",
        "image_hint": "a teacher underlining a word on the whiteboard",
    },
    # "chating" thiếu một chữ t; "chat" đã có sẵn.
    "pet_vocab_122": {
        "word": "workload",
        "ipa": "/ˈwɜːk.ləʊd/",
        "pos": "noun",
        "example_sentence": "My workload increases at the end of the term.",
        "image_hint": "a tall stack of exercise books on a teacher's desk",
    },
}


def main() -> int:
    apply = "--apply" in sys.argv
    by_level: dict[str, list[str]] = {}
    for vocab_id in FIXES:
        by_level.setdefault(vocab_id.split("_")[0], []).append(vocab_id)

    changed_ids: list[str] = []
    for level, ids in sorted(by_level.items()):
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        index = {w["id"]: w for w in data["words"]}
        for vocab_id in ids:
            entry = index.get(vocab_id)
            if entry is None:
                print(f"  ! {vocab_id} không tồn tại — bỏ qua")
                continue
            for field, value in FIXES[vocab_id].items():
                before = entry.get(field)
                if before == value:
                    continue
                print(f"  {vocab_id}.{field}\n      cũ:  {before}\n      mới: {value}")
                entry[field] = value
            changed_ids.append(vocab_id)

        if apply:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            print(f"  → đã ghi {path}")

    print()
    print(f"{'ĐÃ SỬA' if apply else 'DRY RUN'}: {len(changed_ids)} mục.")
    if not apply:
        print("Chạy lại với --apply để ghi thay đổi.")
    else:
        print("Cần sinh lại audio cho các id trên (word + sentence):")
        print("  python3 tinysteps-data/generate_audio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
