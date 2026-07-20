#!/usr/bin/env python3
"""
Kiểm tra nội dung bài học (lessons/) và điểm ngữ pháp (grammar/) — phần dữ liệu học
viên đọc nhiều nhất nhưng trước đây không được validate gì cả.

Ba nhóm kiểm tra:

1. TOÀN VẸN BÀI TẬP — lỗi làm học viên bị chấm sai dù tiếng Anh đúng:
   - match: đáp án phải là từ vựng của đúng cấp độ (bắt được cả từ sai chính tả lọt
     vào làm từ vựng, như 'guideliness' — nếu vocab đã được sửa mà bài học chưa sửa theo)
   - arrange: các mảnh từ phải ghép lại đúng thành đáp án
   - multiple_choice / listen_choose: đáp án phải nằm trong lựa chọn, lựa chọn không trùng
   - listen_choose: audio_text phải trùng đáp án (học viên nghe gì chọn nấy)
   - fill_blank: prompt phải có chỗ trống "___"

2. THAM CHIẾU — vocabulary_ids và grammar_ids của bài học phải tồn tại thật.

3. VĂN BẢN — artifact của bộ sinh dữ liệu từng gặp ở phần từ vựng, quét trên hội thoại,
   bài tập và ví dụ ngữ pháp: động từ bất quy tắc bị chia -ed ("thinked"), đuôi "eed"
   vô nghĩa ("motivateed"), trợ động từ + -ing ("shoulding"), hậu tố ghép "-new",
   khoảng trắng đôi, từ lặp liền kề. Riêng grammar: soi examples và common_mistakes
   "correct" — KHÔNG soi "correct_mistakes "wrong" vì đó là câu cố tình sai để dạy.
"""

import re
import shutil
import subprocess

from vocabulary_grammar_checks import IRREGULAR

# "She thinked yesterday." — bộ sinh chia -ed cho động từ bất quy tắc.
BAD_IRREGULAR_ED = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in IRREGULAR) + r")ed\b", re.IGNORECASE
)

# "motivateed" — nối "ed" vào từ tận cùng bằng e. Các từ tiếng Anh thật có đuôi
# -eed nằm trong allowlist.
EED_TOKEN = re.compile(r"\b[a-z]+eed\b", re.IGNORECASE)
EED_REAL_WORDS = {
    "need", "needed", "exceed", "exceeded", "succeed", "succeeded", "proceed",
    "proceeded", "agreed", "freed", "speed", "feed", "seed", "deed", "greed",
    "indeed", "guaranteed", "breed", "bleed",
}

MODAL_ING = re.compile(r"\b(must|should|can|may|shall|will)ing\b", re.IGNORECASE)
DOUBLED_WORD = re.compile(r"\b(\w+) \1\b", re.IGNORECASE)
TOKEN = re.compile(r"[\w']+")


def scan_text(location: str, text: str) -> list:
    """Soi một chuỗi văn bản học viên nhìn thấy. Trả về danh sách lỗi."""
    issues = []
    if not isinstance(text, str) or not text:
        return issues

    for match in BAD_IRREGULAR_ED.finditer(text):
        base = match.group(1).lower()
        issues.append(
            f"{location}: '{match.group(0)}' sai — quá khứ của '{base}' là "
            f"'{IRREGULAR[base][0]}': \"{text}\""
        )
    for match in EED_TOKEN.finditer(text):
        if match.group(0).lower() not in EED_REAL_WORDS:
            issues.append(f"{location}: '{match.group(0)}' không phải từ tiếng Anh: \"{text}\"")
    if MODAL_ING.search(text):
        issues.append(f"{location}: trợ động từ khuyết thiếu bị gắn -ing: \"{text}\"")
    if "-new " in text or text.endswith("-new"):
        issues.append(f"{location}: hậu tố ghép '-new' của bộ sinh: \"{text}\"")
    if "  " in text:
        issues.append(f"{location}: khoảng trắng đôi: \"{text}\"")
    doubled = DOUBLED_WORD.search(text)
    # "had had" và "that that" là tiếng Anh hợp lệ; còn lại gần như chắc chắn là lỗi dán.
    if doubled and doubled.group(1).lower() not in {"had", "that", "very"}:
        issues.append(f"{location}: từ lặp liền kề '{doubled.group(0)}': \"{text}\"")
    return issues


def _norm_tokens(text: str) -> list:
    return sorted(t.lower() for t in TOKEN.findall(text))


def check_lesson(lesson: dict, level_vocab_words: set,
                 valid_vocab_ids: set, valid_grammar_ids: set) -> list:
    """Kiểm tra một bài học. Trả về danh sách lỗi đã gắn nhãn vị trí."""
    errors = []
    lid = lesson.get("id", "?")

    for vocab_id in lesson.get("vocabulary_ids", []):
        if vocab_id not in valid_vocab_ids:
            errors.append(f"{lid}: vocabulary_id '{vocab_id}' không tồn tại")
    for grammar_id in lesson.get("grammar_ids", []):
        if grammar_id not in valid_grammar_ids:
            errors.append(f"{lid}: grammar_id '{grammar_id}' không tồn tại")

    for line_index, line in enumerate(lesson.get("dialogue", {}).get("lines", [])):
        errors.extend(scan_text(f"{lid}/dialogue[{line_index}]", line.get("text", "")))

    for ex_index, exercise in enumerate(lesson.get("exercises", [])):
        ex_type = exercise.get("type", "?")
        where = f"{lid}/exercise[{ex_index}:{ex_type}]"
        errors.extend(scan_text(where + "/instruction", exercise.get("instruction", "")))

        for item_index, item in enumerate(exercise.get("items", [])):
            loc = f"{where}/item[{item_index}]"
            answer = item.get("correct_answer", "")

            for field in ("prompt", "audio_text", "correct_answer"):
                errors.extend(scan_text(f"{loc}/{field}", item.get(field, "")))
            for opt in item.get("options", []) or []:
                errors.extend(scan_text(f"{loc}/option", opt))

            if ex_type == "match":
                if answer not in level_vocab_words:
                    errors.append(
                        f"{loc}: đáp án match '{answer}' không phải từ vựng của cấp này"
                    )
            elif ex_type == "arrange":
                if _norm_tokens(" ".join(item.get("words", []))) != _norm_tokens(answer):
                    errors.append(
                        f"{loc}: mảnh từ {item.get('words')} không ghép được thành "
                        f"\"{answer}\""
                    )
            elif ex_type in ("multiple_choice", "listen_choose"):
                options = item.get("options", [])
                if answer not in options:
                    errors.append(f"{loc}: đáp án '{answer}' không nằm trong lựa chọn {options}")
                if len(set(options)) != len(options):
                    errors.append(f"{loc}: lựa chọn trùng nhau {options}")
                if ex_type == "listen_choose" and item.get("audio_text") != answer:
                    errors.append(
                        f"{loc}: audio_text \"{item.get('audio_text')}\" khác đáp án \"{answer}\""
                    )
            elif ex_type == "fill_blank":
                if "___" not in item.get("prompt", ""):
                    errors.append(f"{loc}: prompt không có chỗ trống '___'")

    return errors


# Từ hợp lệ mà aspell (en_GB) không nhận: tên riêng Việt Nam trong hội thoại, và chính tả
# Mỹ được dùng nhất quán trong dữ liệu. So sánh ở dạng lowercase.
SPELL_ALLOWLIST = {
    # tên riêng
    "nam", "nam's", "lan", "minh", "duy", "duy's", "cuc", "vy", "mr", "mrs",
    # chính tả Mỹ được dùng nhất quán trong dữ liệu
    "apologize", "apologized", "apologizing", "behavior", "color", "colorful",
    "coloring", "customize", "dialing", "emphasize", "favorite", "memorize",
    "organize", "organizing", "specialty", "traveling", "visualization",
    "installment",  # US spelling of "instalment", used consistently in data
    # cụm ghép quen thuộc trong tài liệu ELT, không nằm trong từ điển aspell
    "appetizer", "groupwork", "pairwork", "roleplay",
    "airplanes", "barcode", "checkbox", "checkboxes", "checkmark", "lightbulb",
    # từ thật nhưng ngoài từ điển aspell en_GB
    # aspell tự tách từ ghép tại gạch nối nên "eco-friendly" trả về mảnh "eco"
    "eco", "ambiance", "communiqué", "cybersecurity", "eco-friendly", "gamification",
    "scalable", "sommelier", "summative", "praxis", "degustation",
    "gastroenterology", "student-centred", "task-based", "gluten-free",
    # thuật ngữ hàn lâm trong dữ liệu KET/PET — hợp lệ về chính tả; việc chúng có
    # NÊN là từ vựng A2-B1 hay không là câu hỏi sản phẩm còn treo, xem báo cáo.
    "axiology", "cognitivism", "consequentialism", "constructivism",
    "constructivist", "deontology", "digitalisation", "essentialism",
    "exploitability", "falsifiability", "generalisability", "hermeneutics",
    "hierarchisation", "instrumentalisation", "interconnectedness",
    "interpretability", "interrelatedness", "measurability",
    "multidimensionality", "multifacetedness", "multilayeredness", "nominalism",
    "operationalisation", "operationalise", "personalisation", "perspicuousness",
    "poststructuralism", "problematisation", "problematise",
    "recontextualisation", "recontextualise", "reductionism", "replicability",
    "reproducibility", "sagaciousness", "sequentialisation", "systematisability",
    "theorisability", "theorisation", "transferability", "verifiability",
}


def spell_check_words(words: set) -> list:
    """Soi chính tả qua aspell. Trả về cảnh báo (không phải lỗi chặn build) — chính tả
    là lớp duy nhất từng phát hiện được 'guideliness'/'progresss', nhưng phụ thuộc môi
    trường nên chỉ cảnh báo, và bỏ qua êm nếu máy không có aspell."""
    if shutil.which("aspell") is None:
        return ["aspell không có trên máy — bỏ qua kiểm tra chính tả"]
    result = subprocess.run(
        ["aspell", "list", "--lang=en_GB", "--encoding=utf-8"],
        input="\n".join(sorted(words)), capture_output=True, text=True,
    )
    misses = {w for w in result.stdout.split() if w.lower() not in SPELL_ALLOWLIST}
    return [f"[SPELLING] aspell không nhận từ '{w}'" for w in sorted(misses)]


def check_grammar_point(grammar_point: dict) -> list:
    """Kiểm tra một điểm ngữ pháp: ví dụ + cặp wrong/correct."""
    errors = []
    gid = grammar_point.get("id", "?")

    for ex_index, example in enumerate(grammar_point.get("examples", [])):
        errors.extend(scan_text(f"{gid}/example[{ex_index}]", example.get("sentence", "")))

    for cm_index, pair in enumerate(grammar_point.get("common_mistakes", [])):
        wrong = (pair.get("wrong") or "").strip()
        correct = (pair.get("correct") or "").strip()
        loc = f"{gid}/common_mistakes[{cm_index}]"
        if not wrong or not correct:
            errors.append(f"{loc}: thiếu vế wrong hoặc correct")
        elif wrong.lower() == correct.lower():
            errors.append(f"{loc}: wrong trùng correct: \"{wrong}\"")
        # Chỉ soi vế "correct" — vế "wrong" là câu cố tình sai để dạy.
        errors.extend(scan_text(f"{loc}/correct", correct))

    return errors
