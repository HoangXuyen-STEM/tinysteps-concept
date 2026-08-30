#!/usr/bin/env python3
"""Audit exercise quality issues across 175 lessons."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from cefr_grammar import GRAMMAR_DETECTORS, LEVEL_ORDER, detect_grammar_structures

SCRIPT_DIR = Path(__file__).resolve().parent
LESSONS_DIR = SCRIPT_DIR / "lessons"
GRAMMAR_DIR = SCRIPT_DIR / "grammar"
REPORT_PATH = SCRIPT_DIR / "reports" / "exercise_quality_report.json"

ABSTRACT_WORDS = {
    "should", "must", "can", "could", "would", "might", "may",
    "attention", "procedure", "permission", "ability", "opinion",
    "experience", "knowledge", "understanding", "communication",
    "although", "however", "despite", "furthermore", "nevertheless",
    "enough", "already", "yet", "since", "recently",
}


def load_grammar_names() -> dict[str, str]:
    mapping = {}
    for level in LEVEL_ORDER:
        data = json.loads((GRAMMAR_DIR / f"{level}.json").read_text(encoding="utf-8"))
        for point in data.get("grammar_points", []):
            mapping[point["id"]] = point["name"]
    return mapping


def load_lessons() -> list[dict]:
    lessons = []
    for level in LEVEL_ORDER:
        for path in sorted((LESSONS_DIR / level).glob("lesson-*.json")):
            lessons.append(json.loads(path.read_text(encoding="utf-8")))
    return lessons


def flag(flags: list, code: str, lesson_id: str, detail: str, exercise_index: int | None = None) -> None:
    flags.append(
        {
            "code": code,
            "lesson_id": lesson_id,
            "exercise_index": exercise_index,
            "detail": detail,
        }
    )


def audit(lessons: list[dict], grammar_names: dict[str, str]) -> list[dict]:
    flags: list[dict] = []
    conversations: dict[tuple[str, str], list[str]] = defaultdict(list)

    for lesson in lessons:
        lid = lesson["id"]
        for ei, exercise in enumerate(lesson.get("exercises", [])):
            ex_type = exercise.get("type")
            items = exercise.get("items", [])
            if ex_type == "fill_blank":
                answers = [item.get("correct_answer", "") for item in items]
                unique = set(answers)
                if len(unique) == 1 and len(answers) >= 3:
                    flag(
                        flags,
                        "REPETITIVE",
                        lid,
                        f"All {len(answers)} items have same answer: '{answers[0]}'",
                        ei,
                    )
                elif answers and len(unique) / len(answers) < 0.5:
                    flag(
                        flags,
                        "LOW_VARIETY",
                        lid,
                        f"{len(answers)} items but only {len(unique)} unique answers",
                        ei,
                    )
            if ex_type in ("match", "multiple_choice"):
                for item in items:
                    answer = (item.get("correct_answer") or "").lower()
                    hint = item.get("image_hint") or ""
                    if answer in ABSTRACT_WORDS and hint.strip() and not item.get("prompt"):
                        flag(
                            flags,
                            "ABSTRACT_IMAGE",
                            lid,
                            f"Image hint for abstract word '{item.get('correct_answer')}': '{hint}'",
                            ei,
                        )
                    if re.search(r"\ba\s+[aeiou]", hint, re.I):
                        flag(flags, "HINT_GRAMMAR", lid, f"Grammar error in image_hint: '{hint}'", ei)
                    if re.search(r"showing a person to \w+", hint, re.I):
                        flag(flags, "HINT_NONSENSE", lid, f"Nonsensical image_hint: '{hint}'", ei)

        claimed = set()
        for gid in lesson.get("grammar_ids", []):
            name = grammar_names.get(gid)
            if name:
                claimed.add(name)
        practiced: set[str] = set()
        for exercise in lesson.get("exercises", []):
            for item in exercise.get("items", []):
                text = " ".join(
                    [
                        item.get("correct_answer", ""),
                        item.get("prompt", ""),
                        item.get("audio_text", ""),
                    ]
                )
                practiced |= detect_grammar_structures(text)
        detectable = set(GRAMMAR_DETECTORS) & claimed
        claimed_not_practiced = detectable - practiced
        if claimed_not_practiced:
            # Informational: claimed grammar IDs often sit in dialogue, not quiz items.
            flag(
                flags,
                "GRAMMAR_MISMATCH",
                lid,
                f"Grammar claimed but not practiced: {sorted(claimed_not_practiced)}",
            )

        ai = lesson.get("ai_conversation") or {}
        conversations[(ai.get("opening_line", ""), ai.get("scenario", ""))].append(lid)

    def get_level(lesson_id: str) -> str:
        return lesson_id.split("_")[0]

    for key, lesson_ids in conversations.items():
        if len(lesson_ids) <= 1:
            continue
        levels = {get_level(lid) for lid in lesson_ids}
        if len(levels) > 1:
            flag(
                flags,
                "AI_CONV_DUPLICATE",
                ",".join(lesson_ids),
                f"Same opening_line across levels: {sorted(levels)} — {key[0][:80]}",
            )
    return flags


def main() -> None:
    grammar_names = load_grammar_names()
    lessons = load_lessons()
    flags = audit(lessons, grammar_names)
    blocking = [f for f in flags if f["code"] != "GRAMMAR_MISMATCH"]
    warnings = [f for f in flags if f["code"] == "GRAMMAR_MISMATCH"]
    by_code: dict[str, int] = defaultdict(int)
    for f in blocking:
        by_code[f["code"]] += 1
    report = {
        "total_lessons": len(lessons),
        "flag_count": len(blocking),
        "warning_count": len(warnings),
        "by_code": dict(by_code),
        "flags": blocking,
        "warnings": warnings,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    print(f"Flags: {len(blocking)}  warnings: {len(warnings)}")
    for code, n in sorted(by_code.items()):
        print(f"  {code}: {n}")


if __name__ == "__main__":
    main()
