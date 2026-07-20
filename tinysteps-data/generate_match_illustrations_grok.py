import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from io import BytesIO

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DATA_DIR)
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "docs", "generated-illustrations")

API_URL = "https://api.x.ai/v1/images/generations"
MODEL_NAME = "grok-imagine-image-quality"
OUTPUT_SIZE = 1024
REQUEST_DELAY_SECONDS = 2.0
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 10.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

VISUAL_DIRECTION = """\
Create a warm, polished, child-friendly editorial illustration for the \
TinySteps English-learning app. Use clean shapes, gentle texture, soft \
daylight, and a warm consistent palette. The target concept must be the \
single largest and clearest visual element. For a simple concrete object, \
show only that object on a plain or minimal surface. Include people only \
when the concept requires them. Keep the composition square, centered, \
mobile-readable, culturally neutral, and free of frames or borders.

Do not include readable text, letters, words, numbers, labels, signage, UI \
text, handwriting-like marks, logos, watermarks, brand marks, QR codes, \
collages, split screens, infographics, or multiple panels. Do not add \
decorative recognizable objects that could become answer distractors. If \
the scene normally contains writing, replace it with a clear non-text visual \
metaphor or leave the surface blank."""


def log(message: str) -> None:
    print(message, flush=True)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_prompt(item: dict) -> str:
    siblings = ", ".join(item["siblingAnswers"]) if item["siblingAnswers"] else "none"
    return f"""{VISUAL_DIRECTION}

Scene: {item['imageHint']}
Depict only the concept "{item['correctAnswer']}". Make that meaning \
immediately obvious without using written language. Do not depict, suggest, \
or include these other answer concepts anywhere: {siblings}."""


def parse_error_message(body: bytes, fallback: str) -> str:
    try:
        payload = json.loads(body.decode("utf-8", errors="replace"))
        error = payload.get("error", payload)
        if isinstance(error, dict):
            return str(error.get("message") or error.get("code") or fallback)
        return str(error)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return fallback


def redact_error(message: str) -> str:
    return re.sub(
        r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
        "<redacted-id>",
        message,
        flags=re.IGNORECASE,
    )


def post_generation(api_key: str, prompt: str) -> dict:
    payload = json.dumps(
        {
            "model": MODEL_NAME,
            "prompt": prompt,
            "n": 1,
            "response_format": "b64_json",
            "aspect_ratio": "1:1",
            "resolution": "1k",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def download_image(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "TinySteps/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def extract_image_bytes(response: dict) -> bytes:
    data = response.get("data") or []
    if not data:
        raise RuntimeError("response contained no image data")

    image = data[0]
    encoded = image.get("b64_json")
    if encoded:
        return base64.b64decode(encoded, validate=True)

    url = image.get("url")
    if url:
        return download_image(url)

    raise RuntimeError("response contained neither b64_json nor image URL")


def generate_one(api_key: str, item: dict) -> tuple[bytes, float | None]:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = post_generation(api_key, build_prompt(item))
            image_bytes = extract_image_bytes(response)
            cost_ticks = (response.get("usage") or {}).get("cost_in_usd_ticks")
            cost_usd = cost_ticks / 1e10 if isinstance(cost_ticks, int | float) else None
            return image_bytes, cost_usd
        except urllib.error.HTTPError as error:
            body = error.read()
            message = redact_error(parse_error_message(body, f"HTTP {error.code}"))
            last_error = RuntimeError(f"HTTP {error.code}: {message}")
            if error.code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES:
                raise last_error from error
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
            if attempt == MAX_RETRIES:
                raise

        backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
        log(f"  [RETRY] {last_error}; retry {attempt}/{MAX_RETRIES} in {backoff:.0f}s")
        time.sleep(backoff)

    raise last_error


def save_square_webp(image_bytes: bytes, output_path: str) -> None:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    side = min(image.width, image.height)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image = image.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
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


def run_batch(api_key: str, batch_path: str, limit: int | None) -> None:
    batch = load_json(batch_path)
    batch_id = batch["batch"]
    level = batch["level"]
    pending = [item for item in batch["items"] if not item["generated"]]
    if limit is not None:
        pending = pending[:limit]

    log(f"Batch {batch_id} ({level}): {len(pending)} pending item(s)")
    if pending:
        log("Asset keys to process:")
        for item in pending:
            log(f"  - {item['assetKey']}")

    total_cost = 0.0
    for index, item in enumerate(pending, start=1):
        asset_key = item["assetKey"]
        output_path = os.path.join(WORKSPACE_DIR, item["outputPath"])
        log(f"[{index}/{len(pending)}] {asset_key} — {item['imageHint']}")

        try:
            image_bytes, cost_usd = generate_one(api_key, item)
            save_square_webp(image_bytes, output_path)
            append_report_row(batch_id, level, item, "Generated")
            if cost_usd is not None:
                total_cost += cost_usd
                log(f"  -> saved {item['outputPath']} (${cost_usd:.4f})")
            else:
                log(f"  -> saved {item['outputPath']}")
        except Exception as error:  # noqa: BLE001 — report failure and keep batch resumable
            append_report_row(batch_id, level, item, "Failed", note=str(error)[:120])
            log(f"  [FAILED] {error}")

        time.sleep(REQUEST_DELAY_SECONDS)

    if total_cost:
        log(f"Reported Grok cost for this run: ${total_cost:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Match illustrations via the xAI Grok image API.")
    parser.add_argument(
        "batch_path",
        help="Path to a batch JSON file, e.g. tinysteps-data/match-illustration-batches/batch-06-movers.json",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N pending items (recommended for pilot runs).",
    )
    args = parser.parse_args()

    if Image is None:
        sys.exit("Missing dependency. Run: .venv/bin/pip install pillow")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        sys.exit(
            "XAI_API_KEY not set. Add it to tinysteps-data/.env, then run:\n"
            "  set -a; source tinysteps-data/.env; set +a\n"
            "before invoking this script."
        )

    log(f"Model: {MODEL_NAME}")
    log(f"Started {datetime.now().isoformat(timespec='seconds')}")
    run_batch(api_key, args.batch_path, args.limit)


if __name__ == "__main__":
    main()
