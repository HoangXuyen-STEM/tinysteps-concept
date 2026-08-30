"""CEFR grammar maps and detectors shared by audit/fix scripts."""

from __future__ import annotations

import re

LEVEL_ORDER = ["starters", "movers", "flyers", "ket", "pet"]

GRAMMAR_BY_LEVEL = {
    "starters": {
        "imperative_positive",
        "imperative_negative",
        "present_simple_be",
        "present_simple_positive",
        "there_is_there_are",
        "this_that_these_those",
        "singular_plural",
        "basic_prepositions",
        "question_what",
        "question_how_many",
        "present_simple_negative",
        "present_simple_questions",
    },
    "movers": {
        "present_continuous",
        "past_simple_regular",
        "past_simple_irregular",
        "can_cant",
        "want_to_verb",
        "like_verb_ing",
        "comparative_adjectives",
        "possessives",
        "question_where_when_who",
        "conjunctions_and_but_because",
        "past_simple_be",
        "past_simple_negative",
        "past_simple_questions",
    },
    "flyers": {
        "present_perfect_simple",
        "going_to_verb",
        "must_mustnt",
        "should_shouldnt",
        "reported_commands",
        "superlative_adjectives",
        "adverbs_of_frequency",
        "first_conditional",
        "question_how_long_often",
        "too_adjective",
    },
    "ket": {
        "present_perfect_for_since",
        "could_requests",
        "would_like_to",
        "used_to",
        "relative_clauses_basic",
        "past_continuous",
        "passive_voice_simple",
        "so_such",
        "enough",
        "question_tags",
    },
    "pet": {
        "second_conditional",
        "present_perfect_continuous",
        "wish_past_simple",
        "reported_speech",
        "passive_with_modals",
        "although_however_despite",
        "purpose_so_that",
        "have_something_done",
        "complex_questions",
        "linking_words",
    },
}

# Words that match *ed but are not past-simple verbs in classroom English.
PAST_ED_FALSE_POSITIVES = {
    "needed", "used", "closed", "opened", "tired", "interested", "excited",
    "worried", "bored", "finished", "printed", "colored", "coloured",
    "limited", "related", "detailed", "advanced", "mixed", "shared",
    "based", "named", "called", "required", "expected", "listed",
    "crowded", "united", "pointed", "seated", "gifted", "noted",
}

IRREGULAR_AS_NOUN = {"read", "set", "put", "cut", "hit"}

GRAMMAR_DETECTORS = {
    "second_conditional": re.compile(
        r"\bif\b.*\b(would|wouldn't)\b|\bwould\b.*\bif\b", re.I
    ),
    "present_perfect_continuous": re.compile(r"\b(have|has)\s+been\s+\w+ing\b", re.I),
    "wish_past_simple": re.compile(
        r"\bwish(es|ed)?\b.*\b(was|were|had|could|knew)\b", re.I
    ),
    "reported_speech": re.compile(
        r"\bsaid\s+(that\s+)?\w+\s+(was|were|had|would|could)\b", re.I
    ),
    "passive_with_modals": re.compile(
        r"\b(must|should|can|could|may|might|will|would)\s+be\s+\w+(ed|en|t)\b", re.I
    ),
    "although_however_despite": re.compile(
        r"\b(although|however|despite|nevertheless|moreover|furthermore)\b", re.I
    ),
    "purpose_so_that": re.compile(r"\bso\s+that\b|\bin\s+order\s+to\b", re.I),
    "have_something_done": re.compile(
        r"\b(have|has|had)\s+\w+\s+(repaired|fixed|done|made|built|cleaned|checked|delivered)\b",
        re.I,
    ),
    "present_perfect_for_since": re.compile(
        r"\b(have|has)\s+\w+(ed|en|t)\b.*\b(for|since)\b", re.I
    ),
    "could_requests": re.compile(r"\bcould\s+(you|i|we)\b", re.I),
    "would_like_to": re.compile(r"\b(would\s+like|'d\s+like)\s+to\b", re.I),
    "used_to": re.compile(r"\bused\s+to\s+\w+", re.I),
    "past_continuous": re.compile(r"\b(was|were)\s+\w+ing\b", re.I),
    "passive_voice_simple": re.compile(
        r"\b(was|were)\s+(made|given|told|taken|written|done|seen|found|put|"
        r"sent|called|asked|taught|checked|cleaned|opened|closed|finished|"
        r"started|used|needed|required|expected|allowed|invited|chosen|"
        r"broken|built|kept|left|held|shown|paid)\b",
        re.I,
    ),
    "question_tags": re.compile(
        r",\s*(isn't|aren't|wasn't|weren't|don't|doesn't|didn't|won't|can't|hasn't|haven't)\s+(it|he|she|they|we|you)\s*\?",
        re.I,
    ),
    "present_perfect_simple": re.compile(r"\b(have|has)\s+\w+(ed|en|t)\b", re.I),
    "going_to_verb": re.compile(r"\b(going\s+to|gonna)\s+\w+", re.I),
    "must_mustnt": re.compile(r"\b(must|mustn't)\b", re.I),
    "should_shouldnt": re.compile(r"\b(should|shouldn't)\b", re.I),
    "first_conditional": re.compile(r"\bif\b.*\bwill\b|\bwill\b.*\bif\b", re.I),
    "present_continuous": re.compile(r"\b(am|is|are)\s+\w+ing\b", re.I),
    "past_simple_regular": re.compile(r"\b[a-z]+ed\b", re.I),
    "past_simple_irregular": re.compile(
        r"\b(went|saw|came|took|gave|made|got|said|told|thought|knew|found|left|"
        r"felt|became|brought|kept|began|ran|wrote|sat|stood|lost|paid|met|set|"
        r"put|grew|drew|spoke|broke|chose|fell|held|built|sent|spent|bought|"
        r"caught|taught|fought|heard|hung|led|meant|shot|showed|shut|woke|wore|"
        r"won|drove|ate|drank|sang|swam|threw|blew|flew|forgot|hid|rode|shook|"
        r"stole|woke)\b",
        re.I,
    ),
    "can_cant": re.compile(r"\b(can|can't|cannot)\b", re.I),
    "comparative_adjectives": re.compile(
        r"\b\w+(er|ier)\s+than\b|\bmore\s+\w+\s+than\b", re.I
    ),
    "past_simple_be": re.compile(r"\b(was|were)\b", re.I),
    "linking_words": re.compile(
        r"\b(furthermore|moreover|nevertheless|therefore|meanwhile)\b", re.I
    ),
    "complex_questions": re.compile(
        r"\b(do you know|could you tell me|would you mind)\b", re.I
    ),
}


def allowed_grammar(level: str) -> set[str]:
    idx = LEVEL_ORDER.index(level)
    result: set[str] = set()
    for i in range(idx + 1):
        result |= GRAMMAR_BY_LEVEL[LEVEL_ORDER[i]]
    return result


def detect_grammar_structures(text: str) -> set[str]:
    if not text:
        return set()
    found: set[str] = set()
    for name, pattern in GRAMMAR_DETECTORS.items():
        if not pattern.search(text):
            continue
        if name == "past_simple_regular":
            tokens = re.findall(r"\b[a-z]+ed\b", text.lower())
            tokens = [t for t in tokens if t not in PAST_ED_FALSE_POSITIVES]
            if not tokens:
                continue
        if name == "past_simple_irregular":
            tokens = GRAMMAR_DETECTORS["past_simple_irregular"].findall(text)
            tokens = [t.lower() for t in tokens]
            if all(t in IRREGULAR_AS_NOUN for t in tokens) and re.search(
                r"\b(a|the|your|my|his|her)\s+(set|put|read)\b", text, re.I
            ):
                continue
        if name == "present_perfect_simple" and GRAMMAR_DETECTORS[
            "present_perfect_for_since"
        ].search(text):
            found.add("present_perfect_for_since")
            continue
        if name == "past_simple_be" and (
            GRAMMAR_DETECTORS["past_continuous"].search(text)
            or GRAMMAR_DETECTORS["passive_voice_simple"].search(text)
        ):
            continue
        if name == "although_however_despite" and GRAMMAR_DETECTORS[
            "linking_words"
        ].search(text):
            found.add("although_however_despite")
            found.add("linking_words")
            continue
        found.add(name)
    return found


def severity_for(violations: set[str], level: str) -> str:
    high = {
        "second_conditional",
        "present_perfect_continuous",
        "wish_past_simple",
        "passive_with_modals",
        "reported_speech",
        "first_conditional",
        "present_perfect_simple",
        "past_continuous",
    }
    if violations & high:
        return "high"
    idx = LEVEL_ORDER.index(level)
    for v in violations:
        for i, lv in enumerate(LEVEL_ORDER):
            if v in GRAMMAR_BY_LEVEL[lv] and i > idx + 1:
                return "high"
    return "medium"
