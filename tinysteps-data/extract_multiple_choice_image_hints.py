"""Split the picture description out of multiple_choice prompts.

Every multiple_choice item ships a prompt of the form
    "Look at the picture (DESCRIPTION). QUESTION"
but the prompt was rendered as plain text with no image, so the description
leaked on screen and "What is this?" had no referent. This moves DESCRIPTION into
a dedicated `image_hint` field (image-generation source + alt text, mirroring
match items) and leaves `prompt` as the residual QUESTION only.

Idempotent: an item that already has `image_hint` is skipped, so re-running after
a partial pass is safe.
"""

import glob
import json
import os
import re

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATTERN = re.compile(r"^look at the picture \((.+?)\)\.\s*(.*)$", re.IGNORECASE)


def migrate_item(item: dict) -> bool:
    """Return True if the item was changed."""
    if item.get("image_hint"):
        return False
    match = PROMPT_PATTERN.match(item["prompt"].strip())
    if not match:
        return False
    description, question = match.group(1).strip(), match.group(2).strip()
    item["image_hint"] = description
    item["prompt"] = question
    return True


def main() -> None:
    changed_files = 0
    changed_items = 0
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "lessons", "*", "*.json"))):
        with open(path, "r", encoding="utf-8") as file:
            lesson = json.load(file)

        file_changed = False
        for exercise in lesson.get("exercises", []):
            if exercise.get("type") != "multiple_choice":
                continue
            for item in exercise["items"]:
                if migrate_item(item):
                    changed_items += 1
                    file_changed = True

        if file_changed:
            changed_files += 1
            with open(path, "w", encoding="utf-8") as file:
                # Source files carry no trailing newline; match that to keep diffs
                # limited to the actual field changes.
                file.write(json.dumps(lesson, ensure_ascii=False, indent=2))

    print(f"Updated {changed_items} multiple_choice items across {changed_files} files.")


if __name__ == "__main__":
    main()
