#!/usr/bin/env python3
"""Rewrite flagged CEFR violations in place. Requires audit report.

Does not call an AI API. Uses deterministic substitutions plus a small
rewrite table. Lines that cannot be rewritten safely are logged as
needs_manual_review.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from cefr_grammar import allowed_grammar, detect_grammar_structures

SCRIPT_DIR = Path(__file__).resolve().parent
LESSONS_DIR = SCRIPT_DIR / "lessons"
REPORT_PATH = SCRIPT_DIR / "reports" / "cefr_audit_report.json"
LOG_PATH = SCRIPT_DIR / "reports" / "cefr_fix_log.json"

WORD_LIMITS = {
    "starters": 6,
    "movers": 8,
    "flyers": 10,
    "ket": 14,
    "pet": 18,
}

# (pattern, replacement) applied in order. Keep meaning classroom-friendly.
SUBSTITUTIONS = [
    (re.compile(r"\bIf I were you, I would\b", re.I), "You can"),
    (re.compile(r"\bI would if I had\b", re.I), "I need"),
    (re.compile(r"\bif I had more free time\b", re.I), "when I have time"),
    (re.compile(r"\bI would\b", re.I), "I can"),
    (re.compile(r"\bwould\b", re.I), "will"),
    (re.compile(r"\bhave been (\w+)ing\b", re.I), r"\1 now"),
    (re.compile(r"\bhas been (\w+)ing\b", re.I), r"\1s now"),
    (re.compile(r"\bI wish I (was|were|had|could|knew)\b", re.I), "I want"),
    (re.compile(r"\bin order to\b", re.I), "to"),
    (re.compile(r"\bso that we can\b", re.I), "to"),
    (re.compile(r"\bso that you can\b", re.I), "to"),
    (re.compile(r"\bAlthough\b", re.I), "But"),
    (re.compile(r"\bHowever,\s*", re.I), ""),
    (re.compile(r"\bDespite\b", re.I), "With"),
    (re.compile(r"\bFurthermore,\s*", re.I), ""),
    (re.compile(r"\bMoreover,\s*", re.I), ""),
    (re.compile(r"\bNevertheless,\s*", re.I), "But "),
    (re.compile(r"\bCould you\b", re.I), "Please"),
    (re.compile(r"\bCould I\b", re.I), "May I"),
    (re.compile(r"\bCould we\b", re.I), "Can we"),
    (re.compile(r"\bWould you like to\b", re.I), "Do you want to"),
    (re.compile(r"\bI'd like to\b", re.I), "I want to"),
    (re.compile(r"\bI would like to\b", re.I), "I want to"),
    (re.compile(r"\bused to\b", re.I), "always"),
    (re.compile(r"\bmustn't\b", re.I), "don't"),
    (re.compile(r"\bmust not\b", re.I), "do not"),
    (re.compile(r"\bmust\b", re.I), "need to"),
    (re.compile(r"\bShould I\b", re.I), "Do I"),
    (re.compile(r"\bShould we\b", re.I), "Do we"),
    (re.compile(r"\bshouldn't\b", re.I), "don't"),
    (re.compile(r"\bshould not\b", re.I), "do not"),
    (re.compile(r"\bshould\b", re.I), "can"),
    (re.compile(r"\bare going to\b", re.I), "will"),
    (re.compile(r"\bis going to\b", re.I), "will"),
    (re.compile(r"\bam going to\b", re.I), "will"),
    (re.compile(r"\bWe are looking\b", re.I), "We look"),
    (re.compile(r"\bWe are listening\b", re.I), "We listen"),
    (re.compile(r"\bWho is calling\b", re.I), "Who calls"),
    (re.compile(r"\bhe was absent\b", re.I), "he is absent"),
    (re.compile(r"\bwas\b", re.I), "is"),
    (re.compile(r"\bwere\b", re.I), "are"),
    (re.compile(r"\bhave\s+(\w+ed)\b", re.I), r"\1"),
    (re.compile(r"\bhas\s+(\w+ed)\b", re.I), r"\1"),
    (re.compile(r"I am fine, thank you\. Who is calling\?", re.I), "I am fine. Who calls?"),
    (re.compile(r"He should stay at home and drink warm water\.", re.I), "He can stay home and drink water."),
    (re.compile(r"Good morning\. I'd like to check the school schedule before class\.", re.I),
     "Good morning. I want to check the schedule."),
    (re.compile(r"I'd like to discuss the feedback from last week's parent meeting\.", re.I),
     "I want to talk about parent feedback."),
    (re.compile(r"I would like to buy a train ticket to Hue, please\.", re.I),
     "I want a train ticket to Hue, please."),
    (re.compile(r"If I reviewed my work more carefully, I would make fewer errors\.", re.I),
     "If I check my work, I make fewer errors."),
    (re.compile(r"If I had known earlier, I would have planned something already\.", re.I),
     "If I know earlier, I will plan it."),
]


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def rewrite_text(text: str, level: str) -> str | None:
    allowed = allowed_grammar(level)
    new = text
    for pattern, repl in SUBSTITUTIONS:
        trial = pattern.sub(repl, new)
        if trial == new:
            continue
        # Keep a substitution only if it removes at least one disallowed structure.
        before = detect_grammar_structures(new) - allowed
        after = detect_grammar_structures(trial) - allowed
        if len(after) < len(before):
            new = trial
    new = re.sub(r"\s+", " ", new).strip()
    new = re.sub(r"\s+([.,!?])", r"\1", new)
    if new and new[0].islower():
        new = new[0].upper() + new[1:]
    leftover = detect_grammar_structures(new) - allowed
    if leftover:
        return None
    limit = WORD_LIMITS[level]
    if word_count(new) > limit and word_count(new) > word_count(text):
        return None
    return new


def set_nested(lesson: dict, location: str, value: str) -> None:
    # locations: dialogue.lines[i] | exercises[e].items[i] | exercises[e].items[i].correct_answer
    if location.startswith("dialogue.lines["):
        idx = int(location.split("[")[1].split("]")[0])
        lesson["dialogue"]["lines"][idx]["text"] = value
        return
    m = re.match(r"exercises\[(\d+)\]\.items\[(\d+)\](?:\.(.+))?", location)
    if not m:
        raise ValueError(location)
    ei, ii, field = int(m.group(1)), int(m.group(2)), m.group(3)
    item = lesson["exercises"][ei]["items"][ii]
    if field:
        item[field] = value
    elif "audio_text" in item:
        item["audio_text"] = value
        if item.get("correct_answer") and item["correct_answer"] != value:
            item["correct_answer"] = value
            opts = item.get("options") or []
            if opts and value not in opts:
                opts[0] = value
    elif "prompt" in item:
        item["prompt"] = value
    else:
        item["correct_answer"] = value


def lesson_path(lesson_id: str) -> Path:
    level, _, num = lesson_id.partition("_lesson_")
    return LESSONS_DIR / level / f"lesson-{num}.json"


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    by_lesson: dict[str, list] = defaultdict(list)
    for v in report.get("violations", []):
        by_lesson[v["lesson_id"]].append(v)

    log = {"fixed": [], "needs_manual_review": [], "unchanged": []}
    for lesson_id, flags in by_lesson.items():
        path = lesson_path(lesson_id)
        lesson = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for flag in flags:
            original = flag["text"]
            rewritten = rewrite_text(original, lesson["level"])
            entry = {
                "lesson_id": lesson_id,
                "location": flag["location"],
                "original": original,
                "rewritten": rewritten,
                "violations": flag["violations"],
            }
            if rewritten is None or rewritten == original:
                log["needs_manual_review"].append(entry)
                continue
            set_nested(lesson, flag["location"], rewritten)
            changed = True
            log["fixed"].append(entry)
        if changed:
            path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            log["unchanged"].append(lesson_id)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Fixed {len(log['fixed'])} items")
    print(f"Needs review: {len(log['needs_manual_review'])}")


if __name__ == "__main__":
    main()
