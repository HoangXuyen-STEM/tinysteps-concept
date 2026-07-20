#!/usr/bin/env python3
"""
Kiểm tra từ loại và dạng chia của từ có khớp với câu ví dụ hay không.

Vì sao cần: dữ liệu từ vựng được sinh bằng cách ghép từ vào mẫu câu. Bộ sinh không xét
từ loại nên mẫu dành cho danh từ nhận cả động từ ("Look at the help."), và nối thẳng
đuôi "ed" vào mọi động từ ("She has already builded."). Cấu trúc, số lượng và độ dài
câu đều hợp lệ nên các kiểm tra cũ không thấy gì bất thường.

Nguyên tắc thiết kế: chỉ nhìn từ đứng NGAY TRƯỚC và NGAY SAU ô trống để suy ra từ loại
bắt buộc — ngữ pháp thuần, không phụ thuộc phân bố dữ liệu hiện tại nên rule không mục
theo thời gian. Ngữ cảnh nào không khớp luật nào thì im lặng: thà bỏ sót còn hơn báo
nhầm, vì validator hay báo nhầm sẽ bị tắt đi và mất tác dụng.
"""

import re

# Từ hạn định: sau nó phải là một danh ngữ.
DETERMINERS = {
    "the", "a", "an", "my", "your", "his", "her", "their", "our",
    "this", "that", "these", "those",
}

# Trợ động từ khuyết thiếu: sau nó phải là động từ nguyên thể. Cố tình KHÔNG có "to":
# "to" còn là giới từ ("Go to platform 3.") nên dùng nó làm dấu hiệu sẽ báo nhầm.
VERB_CUES = {"should", "would", "could", "can", "may", "might", "must", "will", "please"}

COPULAS = {"is", "was", "am", "are", "were", "be"}

# Hô ngữ: "Hello, {W}!" chỉ nhận danh từ (tên người, chức danh).
VOCATIVE_LEAD = re.compile(r"\b(hello|hi|goodbye|bye|how are you)\s*,\s*$", re.IGNORECASE)

# Trợ động từ khuyết thiếu không có dạng -ing.
MODAL_ING = re.compile(r"^(must|should|can|may|shall)ing$", re.IGNORECASE)

# Số nhiều của danh từ tận cùng phụ âm + y phải là -ies (hobby → hobbies).
BAD_PLURAL_Y = re.compile(r"^[a-z]+[bcdfghjklmnpqrstvwxz]ys$", re.IGNORECASE)

# Bao gồm cả gạch nối và chữ có dấu để không cắt nhầm "eco-friendly" hay "communiqué"
# thành nhiều mảnh rồi báo là câu thiếu từ.
TOKEN = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)

# Động từ bất quy tắc hay gặp ở trình độ A1-B1: (quá khứ, quá khứ phân từ). Dùng cho hai
# việc — chấp nhận dạng chia đúng trong câu, và bắt trường hợp bộ sinh nối "ed" vào động
# từ vốn không chia theo quy tắc ("builded" thay vì "built").
IRREGULAR = {
    "be": ("was", "been"), "begin": ("began", "begun"), "break": ("broke", "broken"),
    "bring": ("brought", "brought"), "build": ("built", "built"),
    "buy": ("bought", "bought"), "catch": ("caught", "caught"),
    "choose": ("chose", "chosen"), "come": ("came", "come"),
    "deal": ("dealt", "dealt"), "draw": ("drew", "drawn"),
    "drink": ("drank", "drunk"), "drive": ("drove", "driven"),
    "eat": ("ate", "eaten"), "fall": ("fell", "fallen"), "feel": ("felt", "felt"),
    "find": ("found", "found"), "forget": ("forgot", "forgotten"),
    "get": ("got", "got"), "give": ("gave", "given"), "go": ("went", "gone"),
    "grow": ("grew", "grown"), "have": ("had", "had"), "hear": ("heard", "heard"),
    "hold": ("held", "held"), "keep": ("kept", "kept"), "know": ("knew", "known"),
    "leave": ("left", "left"), "lose": ("lost", "lost"), "make": ("made", "made"),
    "mean": ("meant", "meant"), "meet": ("met", "met"), "pay": ("paid", "paid"),
    "put": ("put", "put"), "read": ("read", "read"), "ride": ("rode", "ridden"),
    "run": ("ran", "run"), "say": ("said", "said"), "see": ("saw", "seen"),
    "sell": ("sold", "sold"), "send": ("sent", "sent"), "sing": ("sang", "sung"),
    "sit": ("sat", "sat"), "sleep": ("slept", "slept"), "speak": ("spoke", "spoken"),
    "spend": ("spent", "spent"), "stand": ("stood", "stood"),
    "swim": ("swam", "swum"), "take": ("took", "taken"), "teach": ("taught", "taught"),
    "tell": ("told", "told"), "think": ("thought", "thought"),
    "understand": ("understood", "understood"), "wear": ("wore", "worn"),
    "win": ("won", "won"), "write": ("wrote", "written"),
}

# Đuôi hợp lệ khi từ được chia trong câu ví dụ. "ly" để chấp nhận dạng trạng từ
# ("critical" → "Think critically.").
INFLECTION_SUFFIXES = ("s", "es", "ed", "d", "ing", "ies", "ly")


def _tokens(text: str):
    return [t.lower() for t in TOKEN.findall(text)]


def _find_form(sentence: str, word: str):
    """Tìm token trong câu là chính từ đó hoặc một dạng chia hợp lệ. None nếu không có."""
    word_l = word.lower()

    # Mục từ gồm nhiều chữ ("must not") không phải một token nên đối chiếu trực tiếp.
    if " " in word_l:
        return word_l if word_l in sentence.lower() else None

    # Các dạng chia có biến đổi gốc từ — đều là chính tả tiếng Anh chuẩn:
    derived = set()
    if word_l.endswith("e"):
        derived.add(word_l[:-1] + "ing")            # incorporate → incorporating
    if word_l.endswith("y"):
        derived.add(word_l[:-1] + "ies")            # hobby → hobbies
        derived.add(word_l[:-1] + "ied")            # carry → carried
    if re.search(r"[aeiou][bdglmnprt]$", word_l):
        derived.add(word_l + word_l[-1] + "ed")     # clap → clapped
        derived.add(word_l + word_l[-1] + "ing")    # stir → stirring

    for token in _tokens(sentence):
        if token == word_l:
            return token
        if token.startswith(word_l) and token[len(word_l):] in INFLECTION_SUFFIXES:
            return token
        if token in derived:
            return token
        # ride → rode/ridden
        if token in IRREGULAR.get(word_l, ()):
            return token
        # "gluten" xuất hiện trong "gluten-free" vẫn tính là có mặt.
        if "-" in token and word_l in token.split("-"):
            return token
    return None


def _check_inflection(word: str, form: str):
    """Bắt các dạng chia bộ sinh tạo sai. Chỉ xét đuôi -ed vì đó là chỗ nó hay sai."""
    word_l = word.lower()
    if form != word_l + "ed":
        return None
    # Xét bất quy tắc TRƯỚC: nhiều động từ bất quy tắc cũng tận cùng bằng "e"
    # (leave, choose), nếu xét luật "thừa chữ e" trước sẽ gợi ý sai thành "leaved".
    if word_l in IRREGULAR:
        return (f"'{form}' sai — '{word_l}' là động từ bất quy tắc, "
                f"quá khứ là '{IRREGULAR[word_l][0]}'")
    if word_l.endswith("e"):
        return f"'{form}' thừa một chữ e, đúng là '{word_l}d'"
    return None


def _slot_context(sentence: str, form: str):
    """Trả về (từ liền trước, có dấu kết câu ngay sau ô trống không)."""
    match = re.search(rf"\b{re.escape(form)}\b", sentence, re.IGNORECASE)
    if match is None:
        return None, False
    before = TOKEN.findall(sentence[: match.start()])
    ends_here = bool(re.match(r"^\s*[.?!]", sentence[match.end():]))
    return (before[-1].lower() if before else None), ends_here


def check_entry(word: str, pos: str, sentence: str):
    """Trả về danh sách mô tả lỗi cho một mục từ vựng (rỗng nếu không có lỗi)."""
    issues = []
    word_l = word.lower()

    if MODAL_ING.match(word_l):
        issues.append(f"'{word}' không phải từ tiếng Anh (dạng -ing của trợ động từ khuyết thiếu)")

    if BAD_PLURAL_Y.match(word_l):
        issues.append(f"'{word}' sai chính tả số nhiều, đúng là '{word_l[:-2]}ies'")

    form = _find_form(sentence, word)
    if form is None:
        issues.append(f"câu ví dụ không chứa từ '{word}': \"{sentence}\"")
        return issues

    inflection_issue = _check_inflection(word, form)
    if inflection_issue:
        issues.append(f'{inflection_issue}: "{sentence}"')

    # Chỉ xét từ loại khi câu dùng đúng dạng nguyên thể — dạng đã chia thì vai trò ngữ
    # pháp có thể khác hẳn từ loại gốc ("I love gardening." với từ gốc là danh từ).
    if form != word_l:
        return issues

    prev_word, ends_here = _slot_context(sentence, form)

    if prev_word in DETERMINERS:
        # "a {W} student" thì {W} có thể là tính từ bổ nghĩa; "the {W}." thì {W} là
        # trung tâm danh ngữ nên bắt buộc danh từ.
        allowed = {"noun"} if ends_here else {"noun", "adjective"}
        if pos not in allowed:
            issues.append(
                f"sau '{prev_word}' cần {' hoặc '.join(sorted(allowed))}, "
                f"nhưng '{word}' là {pos}: \"{sentence}\""
            )
    elif prev_word in VERB_CUES and pos != "verb":
        issues.append(f"sau '{prev_word}' cần động từ, nhưng '{word}' là {pos}: \"{sentence}\"")
    elif prev_word in COPULAS and ends_here and pos not in {"adjective", "noun"}:
        issues.append(f"sau '{prev_word}' cần tính từ, nhưng '{word}' là {pos}: \"{sentence}\"")
    elif (VOCATIVE_LEAD.search(sentence[: sentence.lower().find(word_l)])
          # "Hello, welcome!" hợp lệ nên chấp nhận cả thán từ và cụm cố định.
          and pos not in {"noun", "phrase", "interjection"}):
        issues.append(f"vị trí hô ngữ cần danh từ, nhưng '{word}' là {pos}: \"{sentence}\"")

    return issues


def check_vocabulary_file(level: str, words: list) -> list:
    """Trả về danh sách lỗi đã gắn nhãn cấp độ và ID, dùng cho validate_data.py."""
    errors = []
    for entry in words:
        word = entry.get("word", "")
        pos = entry.get("pos", "")
        sentence = entry.get("example_sentence", "")
        if not (word and pos and sentence):
            continue
        for issue in check_entry(word, pos, sentence):
            errors.append(f"[{level.upper()} GRAMMAR-FIT] ID {entry.get('id')}: {issue}")
    return errors
