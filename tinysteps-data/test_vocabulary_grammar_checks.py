#!/usr/bin/env python3
"""
Test cho vocabulary_grammar_checks.

Hai nửa quan trọng ngang nhau:
- MUST_FLAG: các lỗi có thật đã từng lọt vào dữ liệu. Nếu một trong số này ngừng bị bắt
  nghĩa là guard đã thủng.
- MUST_PASS: tiếng Anh đúng. Nếu một trong số này bị báo lỗi thì validator báo nhầm, và
  một validator hay báo nhầm sẽ bị tắt đi — mất luôn tác dụng bảo vệ.

Chạy: python3 tinysteps-data/test_vocabulary_grammar_checks.py
"""

from vocabulary_grammar_checks import check_entry

# (từ, từ loại, câu ví dụ) — đều là lỗi thật lấy từ dữ liệu trước khi sửa.
MUST_FLAG = [
    ("help", "verb", "Look at the help."),          # mẫu danh từ nhận động từ
    ("hear", "verb", "Answer the hear."),
    ("translate", "verb", "This is a translate."),
    ("quietly", "adverb", "Point to the quietly."),
    ("sentence", "noun", "If they didn't understand, I would sentence."),  # sau modal
    ("confused", "adjective", "If they didn't understand, I would confused."),
    ("walk", "verb", "Goodbye, walk!"),             # hô ngữ
    ("cold", "adjective", "Goodbye, cold!"),
    ("musting", "verb", "Close your musting."),     # trợ động từ + -ing
    ("hobbys", "noun", "I like my hobbys."),        # số nhiều sai
    ("motivate", "verb", "She has already motivateed."),  # thừa chữ e
    ("build", "verb", "She has already builded."),  # bất quy tắc
    ("think", "verb", "She thinked yesterday."),
    ("leave", "verb", "She leaveed yesterday."),    # vừa tận cùng e vừa bất quy tắc
    ("eraser", "noun", "I cleaned the board."),     # câu không chứa từ
]

# Tiếng Anh đúng — không được báo lỗi.
MUST_PASS = [
    ("sit", "verb", "Please sit down."),
    ("wait", "verb", "Please wait for me."),
    ("new", "adjective", "This is new."),           # tính từ vị ngữ
    ("easy", "adjective", "The lesson was so easy."),
    ("good", "adjective", "He is such a good student."),  # tính từ bổ nghĩa trước danh từ
    ("welcome", "phrase", "Hello, welcome!"),       # cụm cố định ở vị trí hô ngữ
    ("platform", "noun", "Go to platform 3."),      # "to" là giới từ, không phải dấu hiệu động từ
    ("inform", "verb", "She informed the staff."),  # dạng chia đúng
    ("instruction", "noun", "Read the instructions."),  # số nhiều
    ("ride", "verb", "He rode a bicycle."),         # bất quy tắc đúng
    ("critical", "adjective", "Think critically."), # dạng trạng từ
    ("garden", "noun", "I love gardening."),
    ("eco-friendly", "adjective", "The lesson was so eco-friendly."),  # có gạch nối
    ("communiqué", "noun", "If I had a better communiqué, I would use it."),  # có dấu
    ("must not", "phrase", "You must not run."),    # mục từ nhiều chữ
    ("gluten", "noun", "Is it gluten-free?"),       # thành phần của từ ghép
    ("standing", "verb", "He is standing beside the whiteboard."),
    ("checking", "verb", "I am checking the homework this evening."),
    # dạng chia có biến đổi gốc — chính tả chuẩn, không được báo "câu không chứa từ"
    ("incorporate", "verb", "I have been incorporating since Monday."),  # bỏ e + ing
    ("clap", "verb", "She clapped for the winner."),                     # gấp đôi phụ âm
    ("stir", "verb", "She stirred the soup slowly."),
    ("carry", "verb", "She carried my bag yesterday."),                  # y → ied
]


def main() -> int:
    failures = []

    for word, pos, sentence in MUST_FLAG:
        if not check_entry(word, pos, sentence):
            failures.append(f"BỎ SÓT lỗi: {word!r} ({pos}) — \"{sentence}\"")

    for word, pos, sentence in MUST_PASS:
        issues = check_entry(word, pos, sentence)
        if issues:
            failures.append(f"BÁO NHẦM: {word!r} ({pos}) — \"{sentence}\" → {issues[0]}")

    total = len(MUST_FLAG) + len(MUST_PASS)
    if failures:
        print(f"❌ {len(failures)}/{total} trường hợp sai:")
        for line in failures:
            print(f"   {line}")
        return 1

    print(f"✓ {total} trường hợp đúng ({len(MUST_FLAG)} phải bắt, {len(MUST_PASS)} phải bỏ qua).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
