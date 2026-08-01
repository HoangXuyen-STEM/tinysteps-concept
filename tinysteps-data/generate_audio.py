import asyncio
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

try:
    import edge_tts
except ModuleNotFoundError:
    edge_tts = None


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DATA_DIR)
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

FFMPEG_BIN = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or os.path.expanduser("~/bin/ffmpeg")
DIALOGUE_SILENCE_MS = 600

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


def concat_dialogue_lines(line_paths: list, output_path: str, silence_ms: int = DIALOGUE_SILENCE_MS) -> bool:
    """Concatenate per-line MP3s (each keeps its own character voice) into one
    dialogue_full.mp3, inserting a short silence between turns.

    Uses ffmpeg's filter_complex concat so codecs/sample rates are normalised
    even if individual lines were generated at slightly different times.
    Returns True on success, False if ffmpeg is unavailable or the run fails.
    """
    if not line_paths:
        return False
    if not FFMPEG_BIN or not os.path.exists(FFMPEG_BIN):
        log("  [WARN] ffmpeg binary not found; skipping dialogue_full concat")
        return False

    with tempfile.TemporaryDirectory() as tmp_dir:
        silence_path = os.path.join(tmp_dir, "silence.mp3")
        subprocess.run(
            [
                FFMPEG_BIN, "-y", "-f", "lavfi",
                "-i", "anullsrc=r=24000:cl=mono",
                "-t", str(silence_ms / 1000.0),
                "-q:a", "9",
                silence_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        inputs = []
        for line_path in line_paths:
            inputs.append(line_path)
            inputs.append(silence_path)
        # Drop the trailing silence after the last line.
        inputs = inputs[:-1]

        cmd = [FFMPEG_BIN, "-y"]
        for path in inputs:
            cmd += ["-i", path]
        filter_parts = "".join(f"[{i}:a]" for i in range(len(inputs)))
        filter_complex = f"{filter_parts}concat=n={len(inputs)}:v=0:a=1[out]"
        cmd += ["-filter_complex", filter_complex, "-map", "[out]", "-q:a", "3", output_path]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode != 0:
            log(f"  [ERROR] ffmpeg concat failed for {output_path}: {result.stderr.decode(errors='ignore')[:300]}")
            return False
        return True


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

            line_paths = []
            for index, line in enumerate(lines, start=1):
                line_path = os.path.join(out_dir, f"{lesson_id}_line_{index:02d}.mp3")
                if should_generate(line_path):
                    voice = VOICE_MALE if line.get("character_id") == "char_b" else VOICE_FEMALE
                    await generate_tts(line["text"].strip(), line_path, voice, rate)
                    total_files += 1
                if line.get("text", "").strip():
                    line_paths.append(line_path)

            # Full dialogue: concat the already-generated per-line MP3s so each
            # character keeps its own voice (char_a = female, char_b = male),
            # instead of re-synthesizing the whole text with a single voice.
            full_path = os.path.join(out_dir, f"{lesson_id}_dialogue_full.mp3")
            if line_paths and should_generate(full_path):
                if concat_dialogue_lines(line_paths, full_path):
                    total_files += 1
                else:
                    log(f"  [FALLBACK] {lesson_id}: dialogue_full concat failed, skipping")

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


async def generate_listening_audio() -> int:
    log("\n[PHASE 2b] Generating listening practice audio...")
    total_files = 0
    listening_dir = os.path.join(DATA_DIR, "listening")

    for level in LEVELS:
        rate = RATE_BY_LEVEL[level]
        doc_path = os.path.join(listening_dir, f"{level}.json")
        if not os.path.exists(doc_path):
            log(f"  [{level}] Skipped: no listening/{level}.json")
            continue

        document = load_json(doc_path)
        exercises = document.get("exercises", [])
        out_dir = os.path.join(AUDIO_DIR, "listening", level)
        os.makedirs(out_dir, exist_ok=True)
        log(f"  [{level}] Processing {len(exercises)} listening exercises...")

        for exercise in exercises:
            exercise_id = exercise["id"]
            audio_text = exercise.get("audio_text", "").strip()
            if not audio_text:
                log(f"  [WARN] {exercise_id} has no audio_text; skipping")
                continue
            out_path = os.path.join(out_dir, f"{exercise_id}.mp3")
            if should_generate(out_path):
                await generate_tts(audio_text, out_path, VOICE_FEMALE, rate)
                total_files += 1

        log(f"  [{level}] Done")

    log(f"  [TOTAL] Listening audio: {total_files} files generated or refreshed")
    return total_files


def generate_manifest() -> str:
    log("\n[PHASE 3] Generating audio manifest...")
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "voice_female": VOICE_FEMALE,
        "voice_male": VOICE_MALE,
        "vocabulary": {},
        "lessons": {},
        "listening": {},
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

        listening_dir = os.path.join(AUDIO_DIR, "listening", level)
        if os.path.isdir(listening_dir):
            for file_name in sorted(os.listdir(listening_dir)):
                if not file_name.endswith(".mp3"):
                    continue
                exercise_id = file_name[:-4]
                manifest["listening"][exercise_id] = f"audio/listening/{level}/{file_name}"

    os.makedirs(AUDIO_DIR, exist_ok=True)
    manifest_path = os.path.join(AUDIO_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    log(
        f"  Manifest: {len(manifest['vocabulary'])} vocabulary entries, "
        f"{len(manifest['lessons'])} lesson entries, {len(manifest['listening'])} listening entries"
    )
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
    listening_count = await generate_listening_audio()
    manifest_path = generate_manifest()

    log("\n" + "=" * 60)
    log("[DONE] Audio generation complete!")
    log(f"  New vocabulary audio files: {vocab_count}")
    log(f"  New lesson audio files: {lesson_count}")
    log(f"  New listening audio files: {listening_count}")
    log(f"  Total new files: {vocab_count + lesson_count + listening_count}")
    log(f"  Output: {AUDIO_DIR}/")
    log(f"  Manifest: {manifest_path}")
    log("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())