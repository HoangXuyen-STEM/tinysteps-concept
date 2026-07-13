#!/usr/bin/env python3
"""
TinySteps — Phase 3: Comprehensive Integrity and Schema Validator
Checks vocabulary, grammar, and topics.json files for absolute correctness,
verifies CEFR word-length limits, checks for duplicates, and confirms all ID references are valid.
Run: python3 tinysteps-data/validate_data.py
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(SCRIPT_DIR, "vocabulary")
GRAMMAR_DIR = os.path.join(SCRIPT_DIR, "grammar")
TOPICS_FILE = os.path.join(SCRIPT_DIR, "topics", "topics.json")

LEVELS = ["starters", "movers", "flyers", "ket", "pet"]

# CEFR Sentence Word-count Constraints (Strict Limits)
SENTENCE_LENGTH_LIMITS = {
    "starters": 5,
    "movers": 7,
    "flyers": 10,
    "ket": 12,
    "pet": 15
}

# Vocabulary Target Counts
VOCAB_TARGETS = {
    "starters": 300,
    "movers": 400,
    "flyers": 500,
    "ket": 400,
    "pet": 500
}

# Grammar Target Counts (minimum)
GRAMMAR_MIN_TARGETS = {
    "starters": 10,
    "movers": 10,
    "flyers": 10,
    "ket": 10,
    "pet": 10
}


def clean_words_count(sentence):
    """Counts words in a sentence, ignoring punctuation."""
    words = re.findall(r"\b\w+(?:'\w+)?\b", sentence)
    return len(words)


def main():
    print("=" * 60)
    print("TinySteps — Comprehensive Pipeline Validator")
    print("=" * 60)

    errors = []
    warnings = []

    # Store loaded data for cross-reference validation
    loaded_vocab = {}
    loaded_grammar = {}

    # ═══════════════════════════════════════════════════════════════════════
    # 1. VALIDATE VOCABULARY FILES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n[1/3] Validating Vocabulary JSON files...")
    
    global_words = {}  # word -> level

    for level in LEVELS:
        vocab_path = os.path.join(VOCAB_DIR, f"{level}.json")
        if not os.path.exists(vocab_path):
            errors.append(f"Missing vocabulary file: {vocab_path}")
            continue

        try:
            with open(vocab_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse {level}.json: {str(e)}")
            continue

        words = data.get("words", [])
        loaded_vocab[level] = {w["id"]: w for w in words}

        # Check total count matches header
        declared_total = data.get("total_words", 0)
        actual_total = len(words)
        if declared_total != actual_total:
            errors.append(f"[{level.upper()} VOCAB] total_words ({declared_total}) does not match actual length ({actual_total})")

        # Check target count
        target = VOCAB_TARGETS[level]
        if actual_total != target:
            errors.append(f"[{level.upper()} VOCAB] Word count is {actual_total}, expected exactly {target}")

        # Individual word validations
        for idx, item in enumerate(words):
            word_id = item.get("id")
            word = item.get("word")
            pos = item.get("pos")
            ipa = item.get("ipa")
            topic_ids = item.get("topic_ids", [])
            example = item.get("example_sentence", "")
            image_hint = item.get("image_hint")
            freq = item.get("frequency_rank")

            # ID format
            expected_id = f"{level}_vocab_{idx+1:03d}"
            if word_id != expected_id:
                errors.append(f"[{level.upper()} VOCAB] Invalid ID at index {idx}: got '{word_id}', expected '{expected_id}'")

            # Word case & validity
            if not word or not isinstance(word, str):
                errors.append(f"[{level.upper()} VOCAB] Missing or invalid word string at ID {word_id}")
            elif word != word.lower():
                errors.append(f"[{level.upper()} VOCAB] Word '{word}' at ID {word_id} is not lowercase")

            # Duplicate checking (strictly no duplicates across levels)
            if word:
                if word in global_words:
                    errors.append(f"❌ [DUPLICATE] Word '{word}' is present in both '{global_words[word]}' and '{level}'")
                else:
                    global_words[word] = level

            # IPA and POS
            if not ipa or "/" not in ipa:
                errors.append(f"[{level.upper()} VOCAB] ID {word_id}: Missing or invalid IPA notation: '{ipa}'")
            if pos not in ["noun", "verb", "adjective", "adverb", "pronoun", "preposition", "conjunction", "determiner", "interjection", "phrase"]:
                errors.append(f"[{level.upper()} VOCAB] ID {word_id}: Invalid POS: '{pos}'")

            # Sentence Word-count Constraint Check
            word_count = clean_words_count(example)
            limit = SENTENCE_LENGTH_LIMITS[level]
            if word_count > limit:
                errors.append(f"[{level.upper()} VOCAB] ID {word_id} example exceeds length limit: '{example}' ({word_count} words, max {limit})")

            # Topic ID existence
            if not topic_ids:
                errors.append(f"[{level.upper()} VOCAB] ID {word_id}: topic_ids list is empty")

            # Image Hint check
            if not image_hint or len(image_hint.strip()) < 5:
                errors.append(f"[{level.upper()} VOCAB] ID {word_id}: Missing or too short image hint")

        print(f"  ✓ {level:8s}: Loaded and checked {actual_total} words.")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. VALIDATE GRAMMAR FILES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n[2/3] Validating Grammar JSON files...")

    for level in LEVELS:
        grammar_path = os.path.join(GRAMMAR_DIR, f"{level}.json")
        if not os.path.exists(grammar_path):
            errors.append(f"Missing grammar file: {grammar_path}")
            continue

        try:
            with open(grammar_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse {level}.json: {str(e)}")
            continue

        g_points = data.get("grammar_points", [])
        loaded_grammar[level] = {gp["id"]: gp for gp in g_points}

        # Check total count matches header
        declared_total = data.get("total_points", 0)
        actual_total = len(g_points)
        if declared_total != actual_total:
            errors.append(f"[{level.upper()} GRAMMAR] total_points ({declared_total}) does not match actual length ({actual_total})")

        # Check target count
        min_target = GRAMMAR_MIN_TARGETS[level]
        if actual_total < min_target:
            errors.append(f"[{level.upper()} GRAMMAR] Found {actual_total} grammar points, expected at least {min_target}")

        for idx, item in enumerate(g_points):
            gp_id = item.get("id")
            name = item.get("name")
            # Grammar JSONs may use "structure" or "pattern" — accept either
            structure = item.get("structure") or item.get("pattern") or ""
            topic_ids = item.get("topic_ids", [])
            examples = item.get("examples", [])
            mistakes = item.get("common_mistakes", [])

            # ID format
            expected_id = f"{level}_grammar_{idx+1:03d}"
            if gp_id != expected_id:
                errors.append(f"[{level.upper()} GRAMMAR] Invalid ID at index {idx}: got '{gp_id}', expected '{expected_id}'")

            # Structure field missing entirely?
            if not structure:
                errors.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: missing 'structure' (or 'pattern') field")
            else:
                # Warn if it looks like an explanation rather than a concise pattern
                if len(structure) > 100 or (
                    "verb" not in structure.lower()
                    and "noun" not in structure.lower()
                    and "+" not in structure
                    and "subject" not in structure.lower()
                ):
                    warnings.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: structure '{structure}' looks like explanation rather than pattern")

            # Topic ID existence
            if not topic_ids:
                errors.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: topic_ids list is empty")

            # Check Examples count (5 to 10)
            if not (5 <= len(examples) <= 10):
                errors.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: examples count is {len(examples)} (must be between 5 and 10)")

            # Check Mistakes count (2 to 3)
            if not (2 <= len(mistakes) <= 3):
                errors.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: common mistake pairs count is {len(mistakes)} (must be 2 or 3)")

            # Validate each mistake pair structure
            # Schema uses "wrong"/"correct" (grammar.schema.json)
            for m_idx, pair in enumerate(mistakes):
                wrong = pair.get("wrong") or pair.get("incorrect")
                correct = pair.get("correct")

                if not wrong or not correct:
                    errors.append(f"[{level.upper()} GRAMMAR] ID {gp_id}: Mistake pair at index {m_idx} has missing fields")

        print(f"  ✓ {level:8s}: Loaded and checked {actual_total} grammar points.")

    # ═══════════════════════════════════════════════════════════════════════
    # 3. VALIDATE TOPICS.JSON AND MASTER REFERENCES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n[3/3] Validating Curriculum Map (topics.json) reference integrity...")

    if not os.path.exists(TOPICS_FILE):
        errors.append(f"Missing master topics file: {TOPICS_FILE}")
    else:
        try:
            with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                topics_data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse topics.json: {str(e)}")
            topics_data = {}

        topics = topics_data.get("topics", [])
        if len(topics) != 12:
            errors.append(f"[CURRICULUM] topics.json has {len(topics)} topics, expected exactly 12")

        for topic in topics:
            topic_id = topic.get("id")
            spiral = topic.get("spiral", [])

            for spiral_entry in spiral:
                lvl = spiral_entry.get("level")
                vocab_ids = spiral_entry.get("vocabulary_ids", [])
                grammar_ids = spiral_entry.get("grammar_ids", [])

                # Cross-reference vocab IDs
                for vid in vocab_ids:
                    if lvl not in loaded_vocab or vid not in loaded_vocab[lvl]:
                        errors.append(f"[REF ERROR] topics.json reference '{vid}' at level '{lvl}' does not exist in vocabulary/{lvl}.json")

                # Cross-reference grammar IDs
                for gid in grammar_ids:
                    if lvl not in loaded_grammar or gid not in loaded_grammar[lvl]:
                        errors.append(f"[REF ERROR] topics.json reference '{gid}' at level '{lvl}' does not exist in grammar/{lvl}.json")

        print("  ✓ topics.json reference mapping completed.")

    # ═══════════════════════════════════════════════════════════════════════
    # REPORTING RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  - {w}")
        if len(warnings) > 10:
            print(f"  - ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"❌ Errors Found ({len(errors)}):")
        for e in errors[:20]:
            print(f"  - {e}")
        if len(errors) > 20:
            print(f"  - ... and {len(errors) - 20} more errors.")
        print("\n❌ Pipeline verification FAILED. Please resolve the errors above.")
        sys.exit(1)
    else:
        print("🎉 EXCELLENT! All checks passed successfully with 0 errors!")
        print("The data pipeline is perfectly compliant, robust, and ready for lesson synthesis!")
        sys.exit(0)


if __name__ == "__main__":
    main()
