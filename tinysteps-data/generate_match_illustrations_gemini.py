import argparse
import json
import mimetypes
import os
import sys
import time
from datetime import datetime
from io import BytesIO

try:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types as genai_types
except ModuleNotFoundError:
    genai = None
    genai_errors = None
    genai_types = None

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DATA_DIR)
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "docs", "generated-illustrations")

MODEL_NAME = "gemini-3.1-flash-image"
OUTPUT_SIZE = 1024
REQUEST_DELAY_SECONDS = 2.0
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 10.0

# Approved Batch 01 outputs — used as style-reference images so new generations
# match the warm, editorial look already accepted for Starters, instead of
# drifting to a different visual style now that the producer changed.
STYLE_REFERENCE_PATHS = [
    "tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-1.webp",
    "tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-1.webp",
]

VISUAL_DIRECTION = """\
Warm, polished, child-friendly editorial illustration; clean shapes, gentle \
texture, soft daylight, consistent palette. The target concept must be the \
single largest and clearest visual element. For a simple concrete-object hint \
(book, pen, marker, etc.): render ONLY that object on a plain/minimal surface. \
Do not add decorative page illustrations, animals, plants, trees, or other \
iconography onto or around it. Diverse people where people are necessary; \
age-appropriate and culturally neutral classroom context. Square 1:1 \
composition; no frame, no border, no text area.

Hard restrictions: no readable text, letters, words, numbers, labels, \
signage, UI text, worksheets with readable writing, logos, watermarks, brand \
marks, or QR/bar codes — this includes abstract squiggles that closely mimic \
handwriting. No collage, split-screen, infographic, diagram, or \
multiple-panel layout unless the scene genuinely requires a single \
unambiguous visual symbol. When the brief implies a text card, calendar, \
agenda, ticket, chart, checklist, phone screen, menu, receipt, or board: \
replace readable content with abstract, non-readable marks or a clear \
non-text visual metaphor."""


def log(message: str) -> None:
    print(message, flush=True)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_prompt(item: dict) -> str:
    siblings = ", ".join(item["siblingAnswers"]) if item["siblingAnswers"] else "none"
    return f"""{VISUAL_DIRECTION}

Scene brief: {item['imageHint']}
The image must depict ONLY the concept "{item['correctAnswer']}". Do not \
depict, hint at, or include any of these other answer options from the same \
exercise: {siblings}."""


def load_reference_images() -> list:
    images = []
    for rel_path in STYLE_REFERENCE_PATHS:
        abs_path = os.path.join(WORKSPACE_DIR, rel_path)
        if os.path.isfile(abs_path):
            images.append(Image.open(abs_path))
        else:
            log(f"  [WARN] style reference missing, skipping: {rel_path}")
    return images


def extract_image_bytes(response) -> bytes | None:
    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.inline_data is not None:
                return part.inline_data.data
    return None


def generate_one(client, item: dict, reference_images: list) -> bytes:
    prompt_parts = [*reference_images, build_prompt(item)]
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt_parts,
            )
            image_bytes = extract_image_bytes(response)
            if image_bytes is None:
                raise RuntimeError("response contained no image part")
            return image_bytes
        except genai_errors.ClientError as error:
            last_error = error
            is_rate_limited = getattr(error, "code", None) == 429
            if not is_rate_limited or attempt == MAX_RETRIES:
                raise
            backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
            log(f"  [429] rate limited, retry {attempt}/{MAX_RETRIES} in {backoff:.0f}s")
            time.sleep(backoff)
    raise last_error


def save_square_webp(image_bytes: bytes, output_path: str) -> None:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    side = min(image.width, image.height)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image = image.resize((OUTPUT_SIZE, OUTPUT_SIZE))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path, "WEBP", quality=90)


def append_report_row(batch_id: str, level: str, item: dict, status: str, note: str = "") -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f"batch-{batch_id}-report.md")
    is_new = not os.path.isfile(report_path)
    with open(report_path, "a", encoding="utf-8") as file:
        if is_new:
            file.write(f"# Batch {batch_id} ({level.capitalize()})\n\n")
            file.write("| Asset Key | Description | File Path | Status | Validation |\n")
            file.write("| :--- | :--- | :--- | :--- | :--- |\n")
        status_text = f"{status} ({note})" if note else status
        file.write(
            f"| {item['assetKey']} | {item['imageHint']} | {item['outputPath']} | "
            f"{status_text} | Pending |\n"
        )


def run_batch(client, batch_path: str, reference_images: list, limit: int | None) -> None:
    batch = load_json(batch_path)
    batch_id = batch["batch"]
    level = batch["level"]
    pending = [item for item in batch["items"] if not item["generated"]]
    if limit is not None:
        pending = pending[:limit]

    log(f"Batch {batch_id} ({level}): {len(pending)} pending item(s)")

    for index, item in enumerate(pending, start=1):
        asset_key = item["assetKey"]
        output_path = os.path.join(WORKSPACE_DIR, item["outputPath"])
        log(f"[{index}/{len(pending)}] {asset_key} — {item['imageHint']}")

        try:
            image_bytes = generate_one(client, item, reference_images)
            save_square_webp(image_bytes, output_path)
            append_report_row(batch_id, level, item, "Generated")
            log(f"  -> saved {item['outputPath']}")
        except Exception as error:  # noqa: BLE001 — log and continue with next item
            append_report_row(batch_id, level, item, "Failed", note=str(error)[:120])
            log(f"  [FAILED] {error}")

        time.sleep(REQUEST_DELAY_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Match illustrations via Gemini API.")
    parser.add_argument("batch_path", help="Path to a batch JSON file, e.g. tinysteps-data/match-illustration-batches/batch-05-movers.json")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N pending items (for pilot runs).")
    args = parser.parse_args()

    if genai is None or Image is None:
        sys.exit("Missing dependencies. Run: .venv/bin/pip install google-genai pillow")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "GEMINI_API_KEY not set. Run:\n"
            "  set -a; source tinysteps-data/.env; set +a\n"
            "before invoking this script."
        )

    client = genai.Client(api_key=api_key)
    reference_images = load_reference_images()
    log(f"Loaded {len(reference_images)} style-reference image(s).")
    log(f"Started {datetime.now().isoformat(timespec='seconds')}")

    run_batch(client, args.batch_path, reference_images, args.limit)


if __name__ == "__main__":
    main()
