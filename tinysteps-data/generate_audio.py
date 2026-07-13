import asyncio
import json
import os
from datetime import datetime

try:
    import edge_tts
except ModuleNotFoundError:
    edge_tts = None


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DATA_DIR)
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

VOICE_FEMALE = "en-GB-SoniaNeural"
VOICE_MALE = "en-GB-RyanNeural"

RATE_BY_LEVEL = {
    "starters": "-20%",
    "movers": "-10%",
    "flyers": "+0%",
    "ket": "+0%",
    "pet": "+5%",
}

LEVELS = ["starters", "movers", "flyers", "ket", "pet"]
MIN_VALID_MP3_BYTES = 1024


def log(message: str) -> None:
    print(message, flush=True)


def should_generate(output_path: str) -> bool:
    if not os.path.exists(output_path):
        return True
    return os.path.getsize(output_path) < MIN_VALID_MP3_BYTES


async def generate_tts(text: str, output_path: str, voice: str, rate: str) -> None:
    if edge_tts is None:
        raise ModuleNotFoundError("edge_tts")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
    await asyncio.sleep(0.25)


def load_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


async def generate_vocabulary_audio() -> int:
    log("\n[PHASE 1] Generating vocabulary audio...")
    total_files = 0

    for level in LEVELS:
        rate = RATE_BY_LEVEL[level]
        out_dir = os.path.join(AUDIO_DIR, "vocabulary", level)
        os.makedirs(out_dir, exist_ok=True)

        vocab_path = os.path.join(DATA_DIR, "vocabulary", f"{level}.json")
        vocab_data = load_json(vocab_path)
        words = vocab_data.get("words", [])
        log(f"  [{level}] Processing {len(words)} words...")

        for index, word_entry in enumerate(words, start=1):
            word_id = word_entry["id"]
            word_text = word_entry["word"].strip()
            sentence = word_entry.get("example_sentence", "").strip()

            word_path = os.path.join(out_dir, f"{word_id}_word.mp3")
            if should_generate(word_path):
                await generate_tts(f"{word_text} ... {word_text}", word_path, VOICE_FEMALE, rate)
                total_files += 1

            if sentence:
                sentence_path = os.path.join(out_dir, f"{word_id}_sentence.mp3")
                if should_generate(sentence_path):
                    await generate_tts(sentence, sentence_path, VOICE_FEMALE, rate)
                    total_files += 1

            if index % 25 == 0 or index == len(words):
                log(f"    [{level}] {index}/{len(words)} words checked")

        log(f"  [{level}] Done")

    log(f"  [TOTAL] Vocabulary audio: {total_files} files generated or refreshed")
    return total_files


async def generate_lesson_audio() -> int:
    log("\n[PHASE 2] Generating lesson audio...")
    total_files = 0

    for level in LEVELS:
        rate = RATE_BY_LEVEL[level]
        lessons_dir = os.path.join(DATA_DIR, "lessons", level)
        out_dir = os.path.join(AUDIO_DIR, "lessons", level)
        os.makedirs(out_dir, exist_ok=True)

        if not os.path.isdir(lessons_dir):
            log(f"  [{level}] Skipped: no lessons directory")
            continue

        lesson_files = sorted(
            file_name
            for file_name in os.listdir(lessons_dir)
            if file_name.startswith("lesson-") and file_name.endswith(".json")
        )
        log(f"  [{level}] Processing {len(lesson_files)} lessons...")

        for lesson_index, lesson_file in enumerate(lesson_files, start=1):
            lesson = load_json(os.path.join(lessons_dir, lesson_file))
            lesson_id = lesson["id"]
            dialogue = lesson.get("dialogue", {})
            lines = dialogue.get("lines", [])
            exercises = lesson.get("exercises", [])

            for index, line in enumerate(lines, start=1):
                line_path = os.path.join(out_dir, f"{lesson_id}_line_{index:02d}.mp3")
                if should_generate(line_path):
                    voice = VOICE_MALE if line.get("character_id") == "char_b" else VOICE_FEMALE
                    await generate_tts(line["text"].strip(), line_path, voice, rate)
                    total_files += 1

            full_path = os.path.join(out_dir, f"{lesson_id}_dialogue_full.mp3")
            if lines and should_generate(full_path):
                # Commas yield a natural pause; Edge TTS may read ellipses out loud.
                full_text = " , ".join(line["text"].strip() for line in lines if line.get("text"))
                await generate_tts(full_text, full_path, VOICE_FEMALE, rate)
                total_files += 1

            listen_index = 0
            for exercise in exercises:
                if exercise.get("type") != "listen_choose":
                    continue
                for item in exercise.get("items", []):
                    audio_text = item.get("audio_text", "").strip()
                    if not audio_text:
                        continue
                    listen_index += 1
                    listen_path = os.path.join(
                        out_dir,
                        f"{lesson_id}_exercise_listen_{listen_index:02d}.mp3",
                    )
                    if should_generate(listen_path):
                        await generate_tts(audio_text, listen_path, VOICE_FEMALE, rate)
                        total_files += 1

            if lesson_index % 5 == 0 or lesson_index == len(lesson_files):
                log(f"    [{level}] {lesson_index}/{len(lesson_files)} lessons checked")

        log(f"  [{level}] Done")

    log(f"  [TOTAL] Lesson audio: {total_files} files generated or refreshed")
    return total_files


def generate_manifest() -> str:
    log("\n[PHASE 3] Generating audio manifest...")
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "voice_female": VOICE_FEMALE,
        "voice_male": VOICE_MALE,
        "vocabulary": {},
        "lessons": {},
    }

    for level in LEVELS:
        vocab_dir = os.path.join(AUDIO_DIR, "vocabulary", level)
        if os.path.isdir(vocab_dir):
            for file_name in sorted(os.listdir(vocab_dir)):
                if not file_name.endswith(".mp3"):
                    continue
                stem = file_name[:-4]
                vocab_id, audio_type = stem.rsplit("_", 1)
                manifest["vocabulary"].setdefault(vocab_id, {})[audio_type] = (
                    f"audio/vocabulary/{level}/{file_name}"
                )

        lessons_dir = os.path.join(AUDIO_DIR, "lessons", level)
        if os.path.isdir(lessons_dir):
            for file_name in sorted(os.listdir(lessons_dir)):
                if not file_name.endswith(".mp3") or "_lesson_" not in file_name:
                    continue
                stem = file_name[:-4]
                level_prefix, remainder = stem.split("_lesson_", 1)
                order, audio_type = remainder.split("_", 1)
                lesson_id = f"{level_prefix}_lesson_{order}"
                manifest["lessons"].setdefault(lesson_id, {})[audio_type] = (
                    f"audio/lessons/{level}/{file_name}"
                )

    os.makedirs(AUDIO_DIR, exist_ok=True)
    manifest_path = os.path.join(AUDIO_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    log(f"  Manifest: {len(manifest['vocabulary'])} vocabulary entries, {len(manifest['lessons'])} lesson entries")
    log(f"  Saved: {manifest_path}")
    return manifest_path


async def main() -> None:
    log("=" * 60)
    log("TinySteps Audio Generator (Edge TTS)")
    log("=" * 60)

    if edge_tts is None:
        log("[ERROR] edge-tts is not installed.")
        log("Run: pip install edge-tts")
        return

    vocab_count = await generate_vocabulary_audio()
    lesson_count = await generate_lesson_audio()
    manifest_path = generate_manifest()

    log("\n" + "=" * 60)
    log("[DONE] Audio generation complete!")
    log(f"  New vocabulary audio files: {vocab_count}")
    log(f"  New lesson audio files: {lesson_count}")
    log(f"  Total new files: {vocab_count + lesson_count}")
    log(f"  Output: {AUDIO_DIR}/")
    log(f"  Manifest: {manifest_path}")
    log("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())