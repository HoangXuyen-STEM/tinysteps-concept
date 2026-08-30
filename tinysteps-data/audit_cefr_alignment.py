#!/usr/bin/env python3
"""Audit dialogue and exercise text for CEFR grammar overreach."""

from __future__ import annotations

import json
import os
from pathlib import Path

from cefr_grammar import allowed_grammar, detect_grammar_structures, severity_for

SCRIPT_DIR = Path(__file__).resolve().parent
LESSONS_DIR = SCRIPT_DIR / "lessons"
REPORT_PATH = SCRIPT_DIR / "reports" / "cefr_audit_report.json"
LEVELS = ["starters", "movers", "flyers", "ket", "pet"]


def load_lessons() -> list[tuple[Path, dict]]:
    out = []
    for level in LEVELS:
        folder = LESSONS_DIR / level
        for path in sorted(folder.glob("lesson-*.json")):
            with path.open(encoding="utf-8") as f:
                out.append((path, json.load(f)))
    return out


def flag_text(lesson: dict, location: str, text: str, violations_out: list) -> None:
    level = lesson["level"]
    allowed = allowed_grammar(level)
    detected = detect_grammar_structures(text)
    violations = detected - allowed
    if not violations:
        return
    violations_out.append(
        {
            "lesson_id": lesson["id"],
            "level": level,
            "location": location,
            "text": text,
            "violations": sorted(violations),
            "detected_all": sorted(detected),
            "severity": severity_for(violations, level),
        }
    )


def audit_lesson(lesson: dict) -> list[dict]:
    found: list[dict] = []
    for i, line in enumerate(lesson.get("dialogue", {}).get("lines", [])):
        flag_text(lesson, f"dialogue.lines[{i}]", line.get("text", ""), found)

    for ei, exercise in enumerate(lesson.get("exercises", [])):
        ex_type = exercise.get("type")
        for ii, item in enumerate(exercise.get("items", [])):
            loc = f"exercises[{ei}].items[{ii}]"
            if ex_type == "arrange":
                flag_text(lesson, f"{loc}.correct_answer", item.get("correct_answer", ""), found)
            elif ex_type in ("listen_choose", "fill_blank"):
                text = item.get("audio_text") or item.get("prompt", "")
                flag_text(lesson, loc, text, found)
    return found


def main() -> None:
    lessons = load_lessons()
    violations: list[dict] = []
    lesson_ids_with = set()
    summary = {level: {"total": 0, "violations": 0} for level in LEVELS}

    for _path, lesson in lessons:
        level = lesson["level"]
        summary[level]["total"] += 1
        found = audit_lesson(lesson)
        if found:
            lesson_ids_with.add(lesson["id"])
            summary[level]["violations"] += len(found)
            violations.extend(found)

    report = {
        "total_lessons": len(lessons),
        "lessons_with_violations": len(lesson_ids_with),
        "violation_count": len(violations),
        "violations": violations,
        "summary_by_level": summary,
    }
    os.makedirs(REPORT_PATH.parent, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    print(f"Lessons with violations: {report['lessons_with_violations']}")
    for level, info in summary.items():
        print(f"  {level}: {info['violations']} flags / {info['total']} lessons")


if __name__ == "__main__":
    main()
