import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DATA_DIR)
APP_PUBLIC_DIR = os.path.join(WORKSPACE_DIR, "tinysteps-app", "public", "illustrations")
BATCHES_DIR = os.path.join(DATA_DIR, "match-illustration-batches")
QUEUE_PATH = os.path.join(DATA_DIR, "match-illustration-queue.json")

LEVELS = ["starters", "movers", "flyers", "ket", "pet"]
BATCH_SIZE = 25


def log(message: str) -> None:
    print(message, flush=True)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def collect_match_items() -> dict[str, list[dict]]:
    """Walk every lesson JSON and flatten its match items in deterministic order.

    exercise_index is the item's position in lesson['exercises'] (the SAME index the
    app itself uses everywhere else, e.g. ExerciseAnswer.exerciseIndex) — not a
    match-only counter. This avoids introducing yet another "local vs global index"
    ambiguity on top of the one already found and fixed for listen_choose audio.
    """
    by_level: dict[str, list[dict]] = {level: [] for level in LEVELS}

    for level in LEVELS:
        lessons_dir = os.path.join(DATA_DIR, "lessons", level)
        lesson_files = sorted(
            name
            for name in os.listdir(lessons_dir)
            if name.startswith("lesson-") and name.endswith(".json")
        )
        for lesson_file in lesson_files:
            lesson = load_json(os.path.join(lessons_dir, lesson_file))
            lesson_id = lesson["id"]
            for exercise_index, exercise in enumerate(lesson.get("exercises", [])):
                if exercise.get("type") != "match":
                    continue
                items = exercise.get("items", [])
                sibling_answers = [item["correct_answer"] for item in items]
                for item_index, item in enumerate(items):
                    asset_key = f"match/{lesson_id}/exercise-{exercise_index}/item-{item_index}"
                    output_path = os.path.join(
                        "tinysteps-app",
                        "public",
                        "illustrations",
                        "match",
                        lesson_id,
                        f"exercise-{exercise_index}",
                        f"item-{item_index}.webp",
                    )
                    by_level[level].append(
                        {
                            "assetKey": asset_key,
                            "level": level,
                            "lessonId": lesson_id,
                            "exerciseIndex": exercise_index,
                            "itemIndex": item_index,
                            "imageHint": item["image_hint"],
                            "correctAnswer": item["correct_answer"],
                            # Other answers in the SAME exercise — the illustration must
                            # not depict any of these, so the correct one stays unambiguous.
                            "siblingAnswers": [a for a in sibling_answers if a != item["correct_answer"]],
                            "outputPath": output_path.replace("\\", "/"),
                            "generated": os.path.isfile(os.path.join(WORKSPACE_DIR, output_path)),
                        }
                    )
    return by_level


def chunk(items: list[dict], size: int) -> list[list[dict]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def write_batches(by_level: dict[str, list[dict]]) -> list[dict]:
    os.makedirs(BATCHES_DIR, exist_ok=True)
    for stale in os.listdir(BATCHES_DIR):
        os.remove(os.path.join(BATCHES_DIR, stale))

    batch_index = 0
    batch_summaries = []
    for level in LEVELS:
        for batch_items in chunk(by_level[level], BATCH_SIZE):
            batch_index += 1
            batch_id = f"{batch_index:02d}"
            batch_path = os.path.join(BATCHES_DIR, f"batch-{batch_id}-{level}.json")
            with open(batch_path, "w", encoding="utf-8") as file:
                json.dump(
                    {"batch": batch_id, "level": level, "items": batch_items},
                    file,
                    indent=2,
                    ensure_ascii=False,
                )
            pending = sum(1 for item in batch_items if not item["generated"])
            batch_summaries.append(
                {
                    "batch": batch_id,
                    "level": level,
                    "itemCount": len(batch_items),
                    "pending": pending,
                    "path": os.path.relpath(batch_path, WORKSPACE_DIR).replace("\\", "/"),
                }
            )
    return batch_summaries


def main() -> None:
    log("=" * 60)
    log("TinySteps Match Illustration Queue Generator")
    log("=" * 60)

    by_level = collect_match_items()
    total_items = sum(len(items) for items in by_level.values())

    all_items = [item for level in LEVELS for item in by_level[level]]
    with open(QUEUE_PATH, "w", encoding="utf-8") as file:
        json.dump({"totalItems": total_items, "items": all_items}, file, indent=2, ensure_ascii=False)

    batch_summaries = write_batches(by_level)

    for level in LEVELS:
        log(f"  [{level}] {len(by_level[level])} match items")
    log(f"  Total: {total_items} items across {len(batch_summaries)} batches")
    log(f"  Queue: {os.path.relpath(QUEUE_PATH, WORKSPACE_DIR)}")
    log(f"  Batches: {os.path.relpath(BATCHES_DIR, WORKSPACE_DIR)}/")

    pending_batches = [b for b in batch_summaries if b["pending"] > 0]
    log(f"  {len(pending_batches)} of {len(batch_summaries)} batches have pending (ungenerated) items.")
    if pending_batches:
        next_batch = pending_batches[0]
        log(f"  Next batch to run: batch-{next_batch['batch']}-{next_batch['level']} ({next_batch['pending']} pending)")


if __name__ == "__main__":
    main()
