#!/usr/bin/env python3
"""
TinySteps — fix_vocabulary.py
Fixes corrupted vocabulary files. Issues addressed:
  1. Dash artifacts: "good-40" -> "good"
  2. -eing misspellings: "organizeing" -> "organizing"
  3. Invalid words: digits, special chars, length < 2
  4. Plural/form errors: "rices", "energys", "meats" (uncountable nouns wrongly pluralised)
  5. Intra-level duplicates (after stripping artifacts)
  6. Cross-level duplicates (keep word in lowest level)
  7. Example sentences that don't contain the word -> regenerate
  8. Renumber IDs sequentially
"""

import json, os, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR  = os.path.join(SCRIPT_DIR, "vocabulary")
LEVELS     = ["starters", "movers", "flyers", "ket", "pet"]

MAX_SENTENCE = {"starters": 5, "movers": 7, "flyers": 10, "ket": 12, "pet": 15}

# Words that should not appear in Starters (clearly B1+ or abstract/non-concrete)
STARTERS_BLACKLIST = {
    "opinion", "confirm", "argument", "comprehending", "comprehension",
    "agendas", "agenda", "colleagues", "hearing", "must", "achievement",
    "improvement", "understanding", "preparation", "announcement",
    "presentation", "recommendation", "demonstration", "communication",
    "administrator", "management", "development", "progress", "official",
    "guidelines", "corrections", "discussions", "appointments", "appointment",
    "coordinateing", "recommending", "translateing", "pronounceing",
    "organizeing", "urgent", "although", "despite", "furthermore",
    "passive", "conditional", "procedure", "negotiate", "reservation",
    "prescription", "vegetarian", "diagnosis", "symptom", "complaint",
}

# Uncountable nouns that should never be plural
UNCOUNTABLE = {
    "rice", "water", "milk", "coffee", "tea", "sugar", "salt", "bread",
    "butter", "cheese", "meat", "fish", "homework", "information", "advice",
    "equipment", "furniture", "music", "news", "energy", "money",
}

# POS-based example sentence templates (level -> pos -> list of templates)
# [word] placeholder is replaced with the actual word
TEMPLATES = {
    "starters": {
        "noun":        ["I see a [word].", "This is a [word].", "Look at the [word]."],
        "verb":        ["Please [word].", "I [word] now.", "We [word] here."],
        "adjective":   ["It is [word].", "He is [word].", "That is [word]."],
        "adverb":      ["Walk [word].", "Speak [word], please."],
        "interjection":["[word]!", "Say [word].", "I say [word]."],
        "phrase":      ["I say [word].", "We say [word]."],
        "default":     ["This is [word].", "I like [word]."],
    },
    "movers": {
        "noun":        ["I bought [word] yesterday.", "Can you find the [word]?", "She has a [word]."],
        "verb":        ["I want to [word] today.", "Can you [word] with me?", "He [word]ed yesterday."],
        "adjective":   ["It was very [word].", "The day was [word].", "He looked so [word]."],
        "adverb":      ["She walked [word] to school.", "He answered [word]."],
        "interjection":["[word]!", "She said [word].", "He shouted [word]."],
        "phrase":      ["I always say [word].", "He uses [word] a lot."],
        "default":     ["She saw the [word] yesterday.", "I have [word] now."],
    },
    "flyers": {
        "noun":        ["I have already prepared the [word].", "You should bring the [word].", "She told me to check the [word]."],
        "verb":        ["You should [word] carefully.", "I'm going to [word] tomorrow.", "She has already [word]ed."],
        "adjective":   ["The lesson was so [word].", "He is such a [word] student.", "It is too [word] to finish."],
        "adverb":      ["She finished the task [word].", "He answered [word]."],
        "interjection":["[word]! That is great.", "She said [word] to me."],
        "phrase":      ["We often say [word] here.", "I'm going to use [word]."],
        "default":     ["I have already seen the [word].", "You must check the [word]."],
    },
    "ket": {
        "noun":        ["I'd like to confirm the [word].", "Could you check the [word]?", "The [word] has been updated."],
        "verb":        ["Could you [word] this for me?", "I used to [word] every day.", "I have been [word]ing since Monday."],
        "adjective":   ["The report is so [word].", "He is such a [word] colleague.", "It was [word] enough for everyone."],
        "adverb":      ["She completed the task [word].", "He handled it [word] enough."],
        "interjection":["[word]! That is great news.", "She replied [word] to the question."],
        "phrase":      ["We often use [word] in class.", "I'd like to suggest [word]."],
        "default":     ["I'd like to confirm the [word].", "Could we discuss the [word]?"],
    },
    "pet": {
        "noun":        ["If I had a better [word], I would use it.", "The [word] should be confirmed by Friday.", "I apologise for the [word] issue."],
        "verb":        ["If I had time, I would [word] more.", "I wish I could [word] better.", "The work should be [word]ed by noon."],
        "adjective":   ["If it were [word], I would agree.", "She said that it was [word].", "Despite being [word], he continued."],
        "adverb":      ["She handled it [word] despite the difficulty.", "He completed the task [word]."],
        "interjection":["[word]! That was unexpected.", "She responded [word] to the question."],
        "phrase":      ["Furthermore, we use [word] often.", "I apologise for the [word]."],
        "default":     ["Furthermore, the [word] was discussed.", "If I had more [word], I would succeed."],
    },
}


def strip_dash(word: str) -> str:
    """'good-40' -> 'good', 'cheap-new' -> 'cheap', 'word-123' -> 'word'"""
    return re.sub(r'-\w+$', '', word)


def fix_eing(word: str) -> str:
    """'organizeing' -> 'organizing', 'coordinateing' -> 'coordinating'"""
    if word.endswith('eing') and len(word) > 5:
        base = word[:-4]
        if base and base[-1] not in 'aeiou':
            return base + 'ing'
    return word


def fix_bad_plural(word: str) -> str:
    """'rices' -> 'rice', 'energys' -> 'energy'"""
    # Uncountable nouns pluralised
    for unc in UNCOUNTABLE:
        if word.lower() == unc + 's' or word.lower() == unc + 'es':
            return unc
    # Handle irregular: 'energys'
    if word.endswith('ys') and word[:-2] in UNCOUNTABLE:
        return word[:-2]
    return word


# Common verb bases whose gerund form should not be a standalone vocab entry
_GERUND_BASES = {
    "ask", "call", "book", "buy", "cancel", "hear", "arrive", "apologize",
    "bleed", "attend", "button", "board", "act", "answer", "behave",
    "absence", "activity", "attention", "correct", "discuss", "guide",
    "comprehend", "coordinate", "recommend", "translate", "pronounce",
    "organize", "schedule", "confirm", "argue", "complain",
}

def is_valid(word: str) -> bool:
    """Must be alphabetic only, length 2-20. Rejects standalone gerunds of common verbs."""
    if not (bool(re.match(r'^[a-zA-Z\'-]+$', word)) and 2 <= len(word) <= 20):
        return False
    # Reject standalone gerunds: word ends in 'ing' and base (strip 'ing' or 'eing') is known
    if word.endswith('ing') and len(word) > 5:
        base_no_ing = word[:-3]          # "asking" -> "ask"
        base_no_eing = word[:-4] + 'e'  # "arriving" -> would need different approach
        if base_no_ing in _GERUND_BASES:
            return False
    return True


def is_wrong_plural(word: str, seen_in_level: set) -> bool:
    """Returns True if word is a spurious plural of a base already in the level."""
    if word.endswith('s') and len(word) > 3:
        base = word[:-1]                 # "baskets" -> "basket"
        base2 = word[:-2]               # "activitys" -> "activity"
        if base.lower() in seen_in_level or base2.lower() in seen_in_level:
            return True
    if word.endswith('ings') and len(word) > 5:  # "bookings", "callings"
        return True
    return False


def make_example(word: str, pos: str, level: str) -> str:
    """Build a level-appropriate example sentence containing the word."""
    level_tmpl = TEMPLATES.get(level, TEMPLATES["starters"])
    pos_key = pos if pos in level_tmpl else "default"
    limit = MAX_SENTENCE[level]

    for tmpl in level_tmpl[pos_key]:
        sentence = tmpl.replace("[word]", word)
        if len(sentence.split()) <= limit:
            return sentence

    # Fallback: ultra-short
    return f"I see {word}." if pos == "noun" else f"It is {word}."


def example_needs_fix(word: str, example: str) -> bool:
    """True if example doesn't contain the word or contains a dash artifact."""
    if '-' in example and re.search(r'\w+-\d+', example):
        return True
    return word.lower() not in example.lower()


def main():
    print("=" * 60)
    print("TinySteps — Vocabulary Fix Script")
    print("=" * 60)

    # --- Pass 1: clean each level independently ---
    cleaned: dict[str, list] = {}
    for level in LEVELS:
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        raw = json.load(open(path, encoding="utf-8"))["words"]

        seen_in_level: set[str] = set()
        out = []
        stats = dict(dash=0, eing=0, plural=0, invalid=0, blacklist=0,
                     dupe=0, ex_fixed=0)

        for entry in raw:
            w = entry["word"]

            # Fix 1 — dash artifact
            w2 = strip_dash(w)
            if w2 != w:
                stats["dash"] += 1

            # Fix 2 — -eing misspelling
            w3 = fix_eing(w2)
            if w3 != w2:
                stats["eing"] += 1

            # Fix 3 — wrong plural of uncountable noun
            w4 = fix_bad_plural(w3)
            if w4 != w3:
                stats["plural"] += 1

            clean = w4

            # Fix 4 — validity check
            if not is_valid(clean):
                stats["invalid"] += 1
                continue

            # Fix 5 — Starters blacklist
            if level == "starters" and clean.lower() in STARTERS_BLACKLIST:
                stats["blacklist"] += 1
                continue

            # Fix 6a — reject wrong plurals (before adding to seen set)
            if is_wrong_plural(clean.lower(), seen_in_level):
                stats["dupe"] += 1
                continue

            # Fix 6b — intra-level dedup
            key = clean.lower()
            if key in seen_in_level:
                stats["dupe"] += 1
                continue
            seen_in_level.add(key)

            # Fix 7 — example sentence
            ex = entry.get("example_sentence", "")
            if example_needs_fix(clean, ex):
                ex = make_example(clean, entry.get("pos", "noun"), level)
                stats["ex_fixed"] += 1

            out.append({**entry, "word": clean, "example_sentence": ex})

        cleaned[level] = out
        print(f"\n{level}: {len(raw)} raw → {len(out)} after intra-level clean")
        print(f"  dash={stats['dash']} eing={stats['eing']} "
              f"plural={stats['plural']} invalid={stats['invalid']} "
              f"blacklist={stats['blacklist']} dupe={stats['dupe']} "
              f"ex_fixed={stats['ex_fixed']}")

    # --- Pass 2: cross-level dedup (keep word in LOWEST level) ---
    print("\n--- Cross-level dedup ---")
    global_seen: set[str] = set()
    for level in LEVELS:
        before = len(cleaned[level])
        deduped = []
        for entry in cleaned[level]:
            key = entry["word"].lower()
            if key not in global_seen:
                global_seen.add(key)
                deduped.append(entry)
        removed = before - len(deduped)
        cleaned[level] = deduped
        if removed:
            print(f"  {level}: removed {removed} cross-level dupes")

    # --- Pass 3: renumber IDs + save ---
    print("\n--- Saving ---")
    total = 0
    for level in LEVELS:
        words = cleaned[level]
        for i, entry in enumerate(words, 1):
            entry["id"] = f"{level}_vocab_{i:03d}"

        payload = {"level": level, "total_words": len(words), "words": words}
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        total += len(words)
        target = {"starters": 300, "movers": 400, "flyers": 500,
                  "ket": 400, "pet": 500}[level]
        gap = target - len(words)
        flag = "✓" if gap <= 0 else f"⚠ need +{gap}"
        print(f"  {level}.json: {len(words)}/{target} words  {flag}")

    print(f"\nTotal saved: {total} | Target: 2100 | Gap: {max(0, 2100-total)}")
    print("Run validate_data.py to verify.")


if __name__ == "__main__":
    main()
