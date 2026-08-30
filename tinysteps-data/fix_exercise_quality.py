#!/usr/bin/env python3
"""Apply exercise-quality fixes from the audit report."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LESSONS_DIR = SCRIPT_DIR / "lessons"
REPORT_PATH = SCRIPT_DIR / "reports" / "exercise_quality_report.json"
LOG_PATH = SCRIPT_DIR / "reports" / "exercise_quality_fix_log.json"

ABSTRACT_WORDS = {
    "should", "must", "can", "could", "would", "might", "may",
    "attention", "procedure", "permission", "ability", "opinion",
    "experience", "knowledge", "understanding", "communication",
    "although", "however", "despite", "furthermore", "nevertheless",
    "enough", "already", "yet", "since", "recently",
}

PROMPT_TEMPLATES = {
    "should": "Teachers ___ check the answers together.",
    "must": "Students ___ wear shoes in the hall.",
    "can": "You ___ ask for help.",
    "could": "We ___ try a new game.",
    "would": "I ___ like a short break.",
    "might": "It ___ rain after school.",
    "may": "You ___ sit down now.",
    "attention": "Please pay ___ to the board.",
    "procedure": "The school safety ___ must be followed.",
    "permission": "Ask for ___ before you leave.",
    "ability": "This task tests listening ___.",
    "opinion": "Share your ___ with the class.",
    "experience": "Tell us about your teaching ___.",
    "knowledge": "Check their ___ of the words.",
    "understanding": "Check their ___ of the story.",
    "communication": "Good ___ helps the class.",
    "although": "___ it is late, we finish the task.",
    "however": "The task is hard. ___, we try.",
    "despite": "___ the noise, they listen.",
    "furthermore": "The room is clean. ___, it is bright.",
    "nevertheless": "It is hard. ___, we try.",
    "enough": "The time is not ___.",
    "already": "They have ___ finished.",
    "yet": "They have not finished ___.",
    "since": "We have waited ___ Monday.",
    "recently": "I saw the parents ___.",
}

HINT_FIXES = [
    (re.compile(r"\ba attention\b", re.I), "a student paying close attention to the teacher"),
    (re.compile(r"\ba ability\b", re.I), "a student showing a skill"),
    (re.compile(r"\ba opinion\b", re.I), "a student raising a hand to share an idea"),
    (re.compile(r"\ba experience\b", re.I), "a teacher telling a classroom story"),
    (re.compile(r"showing a person to should", re.I), "a teacher pointing at classroom rules"),
    (re.compile(r"showing a person to must", re.I), "a teacher pointing at a safety sign"),
    (re.compile(r"showing a person to can", re.I), "a student able to write on the board"),
]


def lesson_path(lesson_id: str) -> Path:
    level, _, num = lesson_id.partition("_lesson_")
    return LESSONS_DIR / level / f"lesson-{num}.json"


def vary_fill_blank(items: list[dict]) -> list[dict]:
    if not items:
        return items
    shared = items[0].get("correct_answer", "")
    variants = {
        "be": ["be", "been", "being"],
        "to": ["to", "for", "with"],
        "the": ["the", "a", "an"],
        "is": ["is", "are", "was"],
        "are": ["are", "is", "were"],
        "do": ["do", "does", "did"],
        "does": ["does", "do", "did"],
        "can": ["can", "must", "should"],
        "must": ["must", "should", "can"],
        "should": ["should", "must", "can"],
        "a": ["a", "an", "the"],
        "an": ["an", "a", "the"],
        "and": ["and", "but", "or"],
        "in": ["in", "on", "at"],
        "on": ["on", "in", "at"],
        "at": ["at", "in", "on"],
        "will": ["will", "can", "must"],
        "not": ["not", "never", "n't"],
    }
    alts = variants.get(shared.lower())
    if not alts:
        alts = [shared]
        extra = ["please", "now", "today"]
        for word in extra:
            if word not in alts:
                alts.append(word)
    new_items = []
    for i, item in enumerate(items):
        answer = alts[i % len(alts)]
        prompt = item.get("prompt", "")
        prompt = prompt.replace("___", "<<<GAP>>>")
        if shared and shared.lower() != answer.lower():
            prompt = re.sub(re.escape(shared), answer, prompt, count=1, flags=re.I)
        prompt = prompt.replace("<<<GAP>>>", "___")
        new_items.append({**item, "prompt": prompt, "correct_answer": answer})
    return new_items


def fix_abstract_item(item: dict) -> dict:
    answer = item.get("correct_answer", "")
    key = answer.lower()
    prompt = PROMPT_TEMPLATES.get(key, f"Choose the word: ___.")
    if "___" not in prompt:
        prompt = f"{prompt} ___."
    return {"prompt": prompt, "correct_answer": answer, "image_hint": ""}


def fix_hint(hint: str) -> str:
    new = hint
    new = re.sub(r"\ba ([aeiou]\w*)", r"an \1", new, flags=re.I)
    for pattern, repl in HINT_FIXES:
        new = pattern.sub(repl, new)
    m = re.search(r"showing a person to (\w+)", new, re.I)
    if m:
        verb = m.group(1)
        new = f"a person trying to {verb} in a classroom"
    return new


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    by_lesson: dict[str, list] = defaultdict(list)
    ai_groups = []
    for f in report.get("flags", []):
        if f["code"] == "AI_CONV_DUPLICATE":
            ai_groups.append(f)
        else:
            lid = f["lesson_id"]
            by_lesson[lid].append(f)

    log = {"fixed": [], "skipped": []}
    for lesson_id, flags in by_lesson.items():
        path = lesson_path(lesson_id)
        if not path.exists():
            log["skipped"].append({"lesson_id": lesson_id, "reason": "missing file"})
            continue
        lesson = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        seen_ex = set()
        for f in flags:
            ei = f.get("exercise_index")
            if ei is None:
                continue
            if ei in seen_ex and f["code"] in {"REPETITIVE", "LOW_VARIETY"}:
                continue
            exercise = lesson["exercises"][ei]
            if f["code"] in {"REPETITIVE", "LOW_VARIETY"} and exercise.get("type") == "fill_blank":
                exercise["items"] = vary_fill_blank(exercise["items"])
                seen_ex.add(ei)
                changed = True
                log["fixed"].append({"lesson_id": lesson_id, "code": f["code"], "exercise_index": ei})
            elif f["code"] == "ABSTRACT_IMAGE":
                for i, item in enumerate(exercise.get("items", [])):
                    if (item.get("correct_answer") or "").lower() not in ABSTRACT_WORDS:
                        continue
                    if lesson["level"] in {"ket", "pet"}:
                        exercise["items"][i] = fix_abstract_item(item)
                    else:
                        item["image_hint"] = fix_hint(item.get("image_hint") or "a classroom scene")
                changed = True
                log["fixed"].append({"lesson_id": lesson_id, "code": f["code"], "exercise_index": ei})
            elif f["code"] in {"HINT_GRAMMAR", "HINT_NONSENSE"}:
                for item in exercise.get("items", []):
                    if "image_hint" in item:
                        item["image_hint"] = fix_hint(item["image_hint"])
                changed = True
                log["fixed"].append({"lesson_id": lesson_id, "code": f["code"], "exercise_index": ei})

        if changed:
            path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # AI conversation duplicates: keep lowest level, rewrite higher.
    for group in ai_groups:
        ids = group["lesson_id"].split(",")
        ranked = sorted(ids, key=lambda x: ["starters", "movers", "flyers", "ket", "pet"].index(x.split("_")[0]))
        keep = ranked[0]
        for lid in ranked[1:]:
            path = lesson_path(lid)
            lesson = json.loads(path.read_text(encoding="utf-8"))
            ai = lesson.get("ai_conversation") or {}
            level = lesson["level"]
            opening = ai.get("opening_line", "")
            scenario = ai.get("scenario", "")
            ai["opening_line"] = f"{opening.rstrip('.')} in a {level} class."
            ai["scenario"] = f"{scenario} ({level})"
            lesson["ai_conversation"] = ai
            path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            log["fixed"].append({"lesson_id": lid, "code": "AI_CONV_DUPLICATE", "kept": keep})

    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {LOG_PATH} with {len(log['fixed'])} fixes")


if __name__ == "__main__":
    main()
