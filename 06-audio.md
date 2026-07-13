# Workflow 06 — Audio Agent (Edge TTS)

## Vai trò
Generate toàn bộ audio files cho TinySteps app: phát âm từ vựng, câu ví dụ, dialogue lines, và exercise audio. Sử dụng Edge TTS (miễn phí, không cần API key).

## Trigger
Human nói: "Tạo audio" hoặc "Run Agent 6"

## Prerequisite
- Agent 1-4 đã hoàn thành
- Tồn tại: `tinysteps-data/vocabulary/*.json` (5 files)
- Tồn tại: `tinysteps-data/lessons/**/*.json` (175 files)
- Python 3.8+ đã cài trên máy

## Dependency
```bash
pip install edge-tts
```

Kiểm tra cài thành công:
```bash
edge-tts --list-voices | grep "en-"
```

---

## Voice Selection

Edge TTS có nhiều giọng English chất lượng cao. Chọn 2 giọng chính:

| Mục đích | Voice ID | Giọng | Lý do |
|----------|----------|-------|-------|
| **Vocabulary + Sentences** | `en-GB-SoniaNeural` | Nữ, Anh-Anh | Rõ ràng, tốc độ chuẩn, phù hợp cho người mới học |
| **Dialogue Character A** | `en-GB-SoniaNeural` | Nữ, Anh-Anh | Nhân vật chính (teacher/buyer/patient) |
| **Dialogue Character B** | `en-GB-RyanNeural` | Nam, Anh-Anh | Nhân vật phụ (student/seller/doctor) |

> Dùng giọng Anh-Anh (British) vì Cambridge framework dùng British English.
> Nếu muốn đổi sang Anh-Mỹ: `en-US-JennyNeural` (nữ) và `en-US-GuyNeural` (nam).

**Tốc độ nói:** Điều chỉnh theo level để phù hợp trình độ người học.

| Level | Rate parameter | Lý do |
|-------|---------------|-------|
| Starters | `"-20%"` | Nói chậm hơn bình thường 20%, dễ nghe |
| Movers | `"-10%"` | Chậm hơn một chút |
| Flyers | `"+0%"` | Tốc độ bình thường |
| KET | `"+0%"` | Tốc độ bình thường |
| PET | `"+5%"` | Nhanh hơn một chút, gần thực tế |

---

## Cấu trúc thư mục output

```
tinysteps-data/audio/
├── vocabulary/
│   ├── starters/
│   │   ├── starters_vocab_001_word.mp3          ← phát âm từ "hello"
│   │   ├── starters_vocab_001_sentence.mp3      ← câu "Hello! How are you today?"
│   │   ├── starters_vocab_002_word.mp3
│   │   ├── starters_vocab_002_sentence.mp3
│   │   └── ...
│   ├── movers/
│   ├── flyers/
│   ├── ket/
│   └── pet/
├── lessons/
│   ├── starters/
│   │   ├── starters_lesson_001_dialogue_full.mp3    ← toàn bộ dialogue
│   │   ├── starters_lesson_001_line_01.mp3          ← từng line riêng
│   │   ├── starters_lesson_001_line_02.mp3
│   │   ├── starters_lesson_001_exercise_listen_01.mp3  ← audio cho listen_choose
│   │   ├── starters_lesson_001_exercise_listen_02.mp3
│   │   └── ...
│   ├── movers/
│   ├── flyers/
│   ├── ket/
│   └── pet/
└── manifest.json    ← mapping: vocab_id / lesson_id → audio file paths
```

---

## Các bước thực hiện

### Bước 1: Tạo utility script `generate_audio.py`
**Làm gì:** Viết Python script tổng hợp, chạy 1 lệnh duy nhất trên máy local.
**Chi tiết:**

File: `tinysteps-data/generate_audio.py`

Script cần có các thành phần sau:

```python
import edge_tts
import asyncio
import json
import os

# ── CONFIG ─────────────────────────────────────────────────
WORKSPACE_DIR = "/home/hoang-xuyen/Projects/tinysteps-concept"
DATA_DIR = os.path.join(WORKSPACE_DIR, "tinysteps-data")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

VOICE_FEMALE = "en-GB-SoniaNeural"    # Character A, vocabulary
VOICE_MALE   = "en-GB-RyanNeural"     # Character B

RATE_BY_LEVEL = {
    "starters": "-20%",
    "movers":   "-10%",
    "flyers":   "+0%",
    "ket":      "+0%",
    "pet":      "+5%",
}

LEVELS = ["starters", "movers", "flyers", "ket", "pet"]
```

**Core TTS function:**

```python
async def generate_tts(text, output_path, voice=VOICE_FEMALE, rate="+0%"):
    """Generate một file MP3 từ text."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
```

**Quan trọng:** Edge TTS là async, phải dùng `asyncio.run()` hoặc `await` trong async context.

---

### Bước 2: Generate vocabulary audio
**Làm gì:** Cho mỗi từ vựng, tạo 2 file: phát âm từ đơn + câu ví dụ.
**Chi tiết:**

```python
async def generate_vocabulary_audio():
    """Generate audio cho tất cả vocabulary entries."""
    print("\n[PHASE 1] Generating vocabulary audio...")
    total_files = 0

    for level in LEVELS:
        rate = RATE_BY_LEVEL[level]
        out_dir = os.path.join(AUDIO_DIR, f"vocabulary/{level}")
        os.makedirs(out_dir, exist_ok=True)

        vocab_path = os.path.join(DATA_DIR, f"vocabulary/{level}.json")
        with open(vocab_path, "r", encoding="utf-8") as f:
            vocab_data = json.load(f)

        words = vocab_data["words"]
        print(f"  [{level}] Generating audio for {len(words)} words...")

        for word_entry in words:
            word_id = word_entry["id"]
            word_text = word_entry["word"]
            sentence = word_entry.get("example_sentence", "")

            # File 1: Phát âm từ đơn (nói chậm hơn bình thường thêm 10%)
            word_path = os.path.join(out_dir, f"{word_id}_word.mp3")
            if not os.path.exists(word_path):
                # Nói từ 2 lần, cách nhau 1 giây silence
                # Edge TTS không hỗ trợ pause, nên nói: "word ... word"
                word_with_repeat = f"{word_text} ... {word_text}"
                await generate_tts(word_with_repeat, word_path, VOICE_FEMALE, rate)
                total_files += 1

            # File 2: Câu ví dụ
            if sentence:
                sentence_path = os.path.join(out_dir, f"{word_id}_sentence.mp3")
                if not os.path.exists(sentence_path):
                    await generate_tts(sentence, sentence_path, VOICE_FEMALE, rate)
                    total_files += 1

        print(f"  [{level}] Done: {len(words)} words processed")

    print(f"  [TOTAL] Vocabulary audio: {total_files} new files generated")
    return total_files
```

**Lưu ý quan trọng:**
- Check `if not os.path.exists()` trước khi generate → cho phép chạy lại mà không tạo trùng
- Từ đơn được nói 2 lần (cách nhau bởi "...") để người học nghe rõ hơn
- Dùng giọng nữ (Sonia) cho tất cả vocabulary vì rõ ràng hơn

---

### Bước 3: Generate lesson dialogue audio
**Làm gì:** Cho mỗi lesson, tạo audio cho từng line + 1 file full dialogue.
**Chi tiết:**

```python
async def generate_lesson_audio():
    """Generate audio cho tất cả lesson dialogues và exercises."""
    print("\n[PHASE 2] Generating lesson audio...")
    total_files = 0

    for level in LEVELS:
        rate = RATE_BY_LEVEL[level]
        lessons_dir = os.path.join(DATA_DIR, f"lessons/{level}")
        audio_out_dir = os.path.join(AUDIO_DIR, f"lessons/{level}")
        os.makedirs(audio_out_dir, exist_ok=True)

        if not os.path.isdir(lessons_dir):
            print(f"  [SKIP] {level}: no lessons directory")
            continue

        lesson_files = sorted([
            f for f in os.listdir(lessons_dir)
            if f.startswith("lesson-") and f.endswith(".json")
        ])
        print(f"  [{level}] Processing {len(lesson_files)} lessons...")

        for fname in lesson_files:
            with open(os.path.join(lessons_dir, fname), "r", encoding="utf-8") as f:
                lesson = json.load(f)

            lesson_id = lesson["id"]
            dialogue = lesson.get("dialogue", {})
            characters = {c["id"]: c for c in dialogue.get("characters", [])}
            lines = dialogue.get("lines", [])

            # ── Dialogue: từng line riêng ──
            for i, line in enumerate(lines, 1):
                line_path = os.path.join(audio_out_dir, f"{lesson_id}_line_{i:02d}.mp3")
                if os.path.exists(line_path):
                    continue

                text = line["text"]
                char_id = line.get("character_id", "char_a")

                # Chọn voice theo character: char_a = nữ, char_b = nam
                if char_id == "char_b":
                    voice = VOICE_MALE
                else:
                    voice = VOICE_FEMALE

                await generate_tts(text, line_path, voice, rate)
                total_files += 1

            # ── Dialogue: full (tất cả lines nối liền) ──
            full_path = os.path.join(audio_out_dir, f"{lesson_id}_dialogue_full.mp3")
            if not os.path.exists(full_path) and lines:
                # Nối tất cả lines với pause ngắn (dùng "..." cho natural gap)
                full_text_parts = []
                for line in lines:
                    char_id = line.get("character_id", "char_a")
                    char_name = characters.get(char_id, {}).get("name", "Speaker")
                    full_text_parts.append(line["text"])

                full_text = " ... ".join(full_text_parts)
                # Full dialogue dùng voice nữ (narrator mode)
                await generate_tts(full_text, full_path, VOICE_FEMALE, rate)
                total_files += 1

            # ── Exercise audio: listen_choose items ──
            exercises = lesson.get("exercises", [])
            for ex in exercises:
                if ex["type"] != "listen_choose":
                    continue
                for j, item in enumerate(ex.get("items", []), 1):
                    audio_text = item.get("audio_text", "")
                    if not audio_text:
                        continue
                    ex_path = os.path.join(audio_out_dir, f"{lesson_id}_exercise_listen_{j:02d}.mp3")
                    if not os.path.exists(ex_path):
                        await generate_tts(audio_text, ex_path, VOICE_FEMALE, rate)
                        total_files += 1

        print(f"  [{level}] Done")

    print(f"  [TOTAL] Lesson audio: {total_files} new files generated")
    return total_files
```

**Lưu ý:**
- Character A → giọng nữ (Sonia), Character B → giọng nam (Ryan) → dialogue nghe realistic hơn
- Full dialogue nối tất cả lines bằng "..." để tạo pause tự nhiên giữa các lượt thoại
- Exercise listen_choose: chỉ generate audio cho `audio_text` field, không generate cho options

---

### Bước 4: Generate manifest.json
**Làm gì:** Tạo file mapping từ vocab_id / lesson_id → đường dẫn audio files.
**Chi tiết:**

```python
def generate_manifest():
    """Tạo manifest.json — mapping ID → audio file paths."""
    print("\n[PHASE 3] Generating audio manifest...")
    manifest = {
        "generated_at": "",    # sẽ fill timestamp
        "voice_female": VOICE_FEMALE,
        "voice_male": VOICE_MALE,
        "vocabulary": {},
        "lessons": {}
    }

    from datetime import datetime
    manifest["generated_at"] = datetime.now().isoformat()

    # Vocabulary manifest
    for level in LEVELS:
        vocab_dir = os.path.join(AUDIO_DIR, f"vocabulary/{level}")
        if not os.path.isdir(vocab_dir):
            continue
        for fname in sorted(os.listdir(vocab_dir)):
            if not fname.endswith(".mp3"):
                continue
            # Parse: starters_vocab_001_word.mp3
            parts = fname.replace(".mp3", "").rsplit("_", 1)
            if len(parts) == 2:
                vocab_id = parts[0]           # starters_vocab_001
                audio_type = parts[1]         # word hoặc sentence
                if vocab_id not in manifest["vocabulary"]:
                    manifest["vocabulary"][vocab_id] = {}
                manifest["vocabulary"][vocab_id][audio_type] = f"audio/vocabulary/{level}/{fname}"

    # Lessons manifest
    for level in LEVELS:
        lessons_audio_dir = os.path.join(AUDIO_DIR, f"lessons/{level}")
        if not os.path.isdir(lessons_audio_dir):
            continue
        for fname in sorted(os.listdir(lessons_audio_dir)):
            if not fname.endswith(".mp3"):
                continue
            # Parse: starters_lesson_001_line_01.mp3
            # hoặc: starters_lesson_001_dialogue_full.mp3
            # hoặc: starters_lesson_001_exercise_listen_01.mp3
            lesson_id_parts = fname.split("_lesson_")
            if len(lesson_id_parts) < 2:
                continue
            level_prefix = lesson_id_parts[0]
            rest = lesson_id_parts[1].replace(".mp3", "")
            # rest = "001_line_01" hoặc "001_dialogue_full"
            order_and_type = rest.split("_", 1)
            order = order_and_type[0]
            audio_type = order_and_type[1] if len(order_and_type) > 1 else "unknown"
            lesson_id = f"{level_prefix}_lesson_{order}"

            if lesson_id not in manifest["lessons"]:
                manifest["lessons"][lesson_id] = {}
            manifest["lessons"][lesson_id][audio_type] = f"audio/lessons/{level}/{fname}"

    # Save
    manifest_path = os.path.join(AUDIO_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    vocab_count = len(manifest["vocabulary"])
    lesson_count = len(manifest["lessons"])
    print(f"  Manifest: {vocab_count} vocabulary entries, {lesson_count} lesson entries")
    print(f"  Saved: {manifest_path}")
    return manifest_path
```

---

### Bước 5: Main function
**Làm gì:** Kết nối tất cả phases, in summary cuối cùng.

```python
async def main():
    print("=" * 60)
    print("TinySteps Audio Generator (Edge TTS)")
    print("=" * 60)

    # Kiểm tra edge-tts đã cài chưa
    try:
        import edge_tts
    except ImportError:
        print("[ERROR] edge-tts chưa được cài đặt.")
        print("Chạy: pip install edge-tts")
        return

    # Phase 1: Vocabulary audio
    vocab_count = await generate_vocabulary_audio()

    # Phase 2: Lesson audio
    lesson_count = await generate_lesson_audio()

    # Phase 3: Manifest
    generate_manifest()

    # Summary
    print("\n" + "=" * 60)
    print("[DONE] Audio generation complete!")
    print(f"  New vocabulary audio files: {vocab_count}")
    print(f"  New lesson audio files: {lesson_count}")
    print(f"  Total new files: {vocab_count + lesson_count}")
    print(f"  Output: {AUDIO_DIR}/")
    print(f"  Manifest: {AUDIO_DIR}/manifest.json")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Chạy trên máy local

```bash
cd ~/Projects/tinysteps-concept

# Cài edge-tts (chỉ cần lần đầu)
pip install edge-tts

# Chạy generate audio
python3 tinysteps-data/generate_audio.py
```

**Thời gian ước tính:**
- 75 từ × 2 files = ~150 files vocabulary → khoảng 2-3 phút
- 175 lessons × ~10 files = ~1750 files lessons → khoảng 15-20 phút
- Tổng: ~20-25 phút cho lần chạy đầu tiên
- Lần chạy lại (bổ sung): nhanh hơn vì skip files đã tồn tại

**Khi vocabulary được bổ sung lên 2100 từ:**
- 2100 × 2 = ~4200 files vocabulary → khoảng 30-40 phút
- Chỉ generate files mới (skip existing), không mất thời gian lại từ đầu

---

## Validation

### Kiểm tra tự động
```bash
# 1. Đếm tổng số file MP3
find tinysteps-data/audio -name "*.mp3" | wc -l

# 2. Kiểm tra kích thước — file MP3 hợp lệ phải > 1KB
find tinysteps-data/audio -name "*.mp3" -size -1k
# Kỳ vọng: không có file nào (output rỗng)

# 3. Kiểm tra manifest coverage
python3 - <<'EOF'
import json

manifest = json.load(open("tinysteps-data/audio/manifest.json"))
print(f"Vocabulary entries in manifest: {len(manifest['vocabulary'])}")
print(f"Lesson entries in manifest: {len(manifest['lessons'])}")

# Kiểm tra mỗi vocab entry có cả word + sentence
missing_sentence = 0
for vid, files in manifest["vocabulary"].items():
    if "sentence" not in files:
        missing_sentence += 1
print(f"Vocab entries missing sentence audio: {missing_sentence}")

# Kiểm tra mỗi lesson entry có dialogue_full
missing_dialogue = 0
for lid, files in manifest["lessons"].items():
    if "dialogue_full" not in files:
        missing_dialogue += 1
print(f"Lessons missing full dialogue audio: {missing_dialogue}")
EOF

# 4. Nghe thử file đầu tiên
# (Mở bằng media player mặc định)
xdg-open tinysteps-data/audio/vocabulary/starters/starters_vocab_001_word.mp3
```

### Kiểm tra thủ công (quan trọng)
1. Nghe 3 file vocabulary ngẫu nhiên → phát âm có rõ ràng không?
2. Nghe 1 full dialogue ở Starters → tốc độ có chậm hơn bình thường không?
3. Nghe 1 full dialogue ở PET → tốc độ có nhanh hơn Starters không?
4. Nghe 1 exercise listen audio → rõ ràng, đủ để chọn đáp án không?

---

## Khi gặp vấn đề

| Vấn đề | Nguyên nhân | Cách sửa |
|--------|-------------|----------|
| `ModuleNotFoundError: edge_tts` | Chưa cài package | `pip install edge-tts` |
| File MP3 = 0 bytes | Mất kết nối internet | Edge TTS cần internet lần đầu. Kiểm tra mạng rồi chạy lại |
| Giọng đọc quá nhanh/chậm | Rate parameter chưa phù hợp | Chỉnh `RATE_BY_LEVEL` trong config |
| Timeout hoặc rate limit | Quá nhiều requests liên tiếp | Thêm `await asyncio.sleep(0.3)` sau mỗi `generate_tts()` |
| Ký tự đặc biệt bị đọc sai | TTS đọc "..." thành "dot dot dot" | Thay "..." bằng SSML pause hoặc dấu phẩy "," |

**Nếu "..." bị đọc thành "dot dot dot":**
Thay cách tạo pause trong dialogue:
```python
# Thay vì:
full_text = " ... ".join(full_text_parts)
# Dùng:
full_text = " , ".join(full_text_parts)
# Hoặc thêm delay bằng cách generate từng line rồi nối MP3 files
```

---

## Báo cáo khi hoàn thành

```
✅ Agent 6 (Audio) hoàn thành
- Vocabulary audio:
  - Starters: {n} word files + {n} sentence files
  - Movers: {n} + {n}
  - Flyers: {n} + {n}
  - KET: {n} + {n}
  - PET: {n} + {n}
- Lesson audio:
  - Dialogue lines: {n} files
  - Full dialogues: {n} files
  - Exercise listen: {n} files
- Tổng: {n} MP3 files
- Manifest: tinysteps-data/audio/manifest.json
- Voice: {VOICE_FEMALE} + {VOICE_MALE}
- Validation: PASSED / FAILED
```

---

## Mở rộng sau này

**Nếu muốn nâng cấp chất lượng audio:**

1. **Nối MP3 thay vì nối text cho full dialogue:** Dùng `pydub` để nối từng line MP3 (đã có giọng khác nhau cho char_a / char_b) thành 1 file duy nhất, thêm 1 giây silence giữa các lượt. Cách này realistic hơn nhiều vì mỗi nhân vật giữ giọng riêng trong full dialogue.

```bash
pip install pydub
```

```python
from pydub import AudioSegment

silence = AudioSegment.silent(duration=1000)  # 1 giây
combined = AudioSegment.empty()
for i, line in enumerate(lines, 1):
    line_audio = AudioSegment.from_mp3(f"{lesson_id}_line_{i:02d}.mp3")
    combined += line_audio + silence
combined.export(f"{lesson_id}_dialogue_full.mp3", format="mp3")
```

2. **Thêm giọng đa dạng hơn:** Dùng giọng khác cho vai parent, doctor, waiter để dialogue phong phú. Map thêm voices theo `role` field trong characters.

3. **Chuyển sang offline TTS:** Nếu không muốn phụ thuộc internet, dùng `piper-tts` (offline, chất lượng tốt, miễn phí).
