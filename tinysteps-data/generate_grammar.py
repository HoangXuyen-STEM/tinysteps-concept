#!/usr/bin/env python3
"""
TinySteps — Phase 1: Grammar Generator
Adds 25 new grammar points (5 per level) to existing grammar JSON files.
Run: python3 tinysteps-data/generate_grammar.py
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_DIR = os.path.join(SCRIPT_DIR, "grammar")

# ═══════════════════════════════════════════════════════════════════════
# NEW GRAMMAR DATA — 5 points per level (IDs 006-010)
# ═══════════════════════════════════════════════════════════════════════

NEW_GRAMMAR = {

# ── STARTERS ────────────────────────────────────────────────────────
"starters": [
    {
        "id": "starters_grammar_006",
        "name": "this_that_these_those",
        "pattern": "This/That + is + noun | These/Those + are + noun",
        "topic_ids": ["topic_in_class", "topic_checking_understanding", "topic_market"],
        "examples": [
            {"sentence": "This is a pen.", "context": "teacher showing a classroom item"},
            {"sentence": "That is a book.", "context": "pointing across the room"},
            {"sentence": "These are my students.", "context": "introducing the class"},
            {"sentence": "Those are your books.", "context": "checking student belongings"},
            {"sentence": "Is this your pen?", "context": "finding a lost item in class"}
        ],
        "common_mistakes": [
            {"wrong": "This are books.", "correct": "These are books."},
            {"wrong": "That are pens.", "correct": "Those are pens."}
        ]
    },
    {
        "id": "starters_grammar_007",
        "name": "singular_plural",
        "pattern": "one + noun | two/three/many + noun + -s/-es",
        "topic_ids": ["topic_in_class", "topic_market"],
        "examples": [
            {"sentence": "I have two books.", "context": "counting school supplies"},
            {"sentence": "There are three pens.", "context": "counting items on desk"},
            {"sentence": "I see many students.", "context": "looking at the classroom"},
            {"sentence": "I want two bags of rice.", "context": "buying at the market"},
            {"sentence": "The teachers are here.", "context": "morning greeting"}
        ],
        "common_mistakes": [
            {"wrong": "I have two book.", "correct": "I have two books."},
            {"wrong": "There are many student.", "correct": "There are many students."},
            {"wrong": "I see three teacher.", "correct": "I see three teachers."}
        ]
    },
    {
        "id": "starters_grammar_008",
        "name": "basic_prepositions",
        "pattern": "noun + is/are + in/on/under/next to + noun",
        "topic_ids": ["topic_in_class", "topic_giving_instructions"],
        "examples": [
            {"sentence": "The pen is on the desk.", "context": "describing classroom layout"},
            {"sentence": "The book is under the chair.", "context": "looking for a lost book"},
            {"sentence": "Sit next to your friend.", "context": "teacher giving seating instructions"},
            {"sentence": "The teacher is in the class.", "context": "describing who is where"},
            {"sentence": "The water is on the table.", "context": "pointing to a drink"}
        ],
        "common_mistakes": [
            {"wrong": "The pen is in the desk.", "correct": "The pen is on the desk."},
            {"wrong": "Sit to next your friend.", "correct": "Sit next to your friend."}
        ]
    },
    {
        "id": "starters_grammar_009",
        "name": "question_what",
        "pattern": "What + is/are + this/that? | What + do/does + subject + verb?",
        "topic_ids": ["topic_checking_understanding", "topic_in_class"],
        "examples": [
            {"sentence": "What is this?", "context": "teacher quizzing students"},
            {"sentence": "What is your name?", "context": "first day introduction"},
            {"sentence": "What is on the desk?", "context": "classroom activity"},
            {"sentence": "What do you want?", "context": "asking at the market"},
            {"sentence": "What is it?", "context": "teacher checking understanding"}
        ],
        "common_mistakes": [
            {"wrong": "What this is?", "correct": "What is this?"},
            {"wrong": "What you want?", "correct": "What do you want?"}
        ]
    },
    {
        "id": "starters_grammar_010",
        "name": "question_how_many",
        "pattern": "How many + plural noun + are there / do you have?",
        "topic_ids": ["topic_in_class", "topic_market"],
        "examples": [
            {"sentence": "How many books are there?", "context": "counting classroom items"},
            {"sentence": "How many students are here?", "context": "taking attendance"},
            {"sentence": "How many pens do you have?", "context": "checking supplies"},
            {"sentence": "How many teachers are in class?", "context": "morning meeting"},
            {"sentence": "How many do you want?", "context": "buying at the market"}
        ],
        "common_mistakes": [
            {"wrong": "How many book?", "correct": "How many books are there?"},
            {"wrong": "How much students?", "correct": "How many students?"}
        ]
    }
],

# ── MOVERS ──────────────────────────────────────────────────────────
"movers": [
    {
        "id": "movers_grammar_006",
        "name": "like_verb_ing",
        "pattern": "Subject + like/likes + Verb-ing",
        "topic_ids": ["topic_social", "topic_in_class", "topic_restaurant"],
        "examples": [
            {"sentence": "I like reading books.", "context": "talking about hobbies"},
            {"sentence": "She likes cooking chicken.", "context": "describing daily routine"},
            {"sentence": "Do you like learning English?", "context": "classroom chat"},
            {"sentence": "They like helping the teacher.", "context": "praising students"},
            {"sentence": "He likes buying fruit at the market.", "context": "weekend routine"}
        ],
        "common_mistakes": [
            {"wrong": "I like read books.", "correct": "I like reading books."},
            {"wrong": "She like cooking.", "correct": "She likes cooking."}
        ],
        "builds_on": ["starters_grammar_004"]
    },
    {
        "id": "movers_grammar_007",
        "name": "comparative_adjectives",
        "pattern": "noun + is + adjective-er + than + noun | more + adjective + than",
        "topic_ids": ["topic_in_class", "topic_market", "topic_social"],
        "examples": [
            {"sentence": "This book is bigger than that one.", "context": "comparing classroom items"},
            {"sentence": "Today is hotter than yesterday.", "context": "weather small talk"},
            {"sentence": "Chicken is cheaper than fruit.", "context": "comparing prices at market"},
            {"sentence": "She is taller than her friend.", "context": "describing classmates"},
            {"sentence": "My homework is better than before.", "context": "teacher giving feedback"}
        ],
        "common_mistakes": [
            {"wrong": "This is more bigger.", "correct": "This is bigger."},
            {"wrong": "She is more tall than me.", "correct": "She is taller than me."}
        ]
    },
    {
        "id": "movers_grammar_008",
        "name": "possessives",
        "pattern": "my/your/his/her/our/their + noun",
        "topic_ids": ["topic_in_class", "topic_social", "topic_school_communication"],
        "examples": [
            {"sentence": "This is my book.", "context": "claiming classroom item"},
            {"sentence": "Where is your homework?", "context": "teacher checking work"},
            {"sentence": "His pen is on the desk.", "context": "identifying belongings"},
            {"sentence": "Her name is Lan.", "context": "introducing a colleague"},
            {"sentence": "Our class is very good.", "context": "teacher praising the class"}
        ],
        "common_mistakes": [
            {"wrong": "I book is here.", "correct": "My book is here."},
            {"wrong": "She pen is blue.", "correct": "Her pen is blue."}
        ]
    },
    {
        "id": "movers_grammar_009",
        "name": "question_where_when_who",
        "pattern": "Where/When/Who + auxiliary + subject + verb?",
        "topic_ids": ["topic_travel", "topic_social", "topic_checking_understanding"],
        "examples": [
            {"sentence": "Where is the market?", "context": "asking for directions"},
            {"sentence": "When did you go to school?", "context": "social chat about routine"},
            {"sentence": "Who is your teacher?", "context": "getting to know someone"},
            {"sentence": "Where did you buy the fruit?", "context": "talking about shopping"},
            {"sentence": "When is the class?", "context": "checking schedule"}
        ],
        "common_mistakes": [
            {"wrong": "Where the market is?", "correct": "Where is the market?"},
            {"wrong": "When you go to school?", "correct": "When did you go to school?"}
        ],
        "builds_on": ["starters_grammar_009"]
    },
    {
        "id": "movers_grammar_010",
        "name": "conjunctions_and_but_because",
        "pattern": "clause + and/but/because + clause",
        "topic_ids": ["topic_social", "topic_praise_correction", "topic_restaurant"],
        "examples": [
            {"sentence": "I like chicken and rice.", "context": "ordering food"},
            {"sentence": "I am hungry but I have no food.", "context": "expressing need"},
            {"sentence": "He is sick because the weather is cold.", "context": "explaining absence"},
            {"sentence": "The answer is good but not great.", "context": "giving feedback"},
            {"sentence": "I called you because I need help.", "context": "explaining a phone call"}
        ],
        "common_mistakes": [
            {"wrong": "I like chicken, because I hungry.", "correct": "I like chicken because I am hungry."},
            {"wrong": "He sick but he come school.", "correct": "He is sick but he came to school."}
        ]
    }
],

# ── FLYERS ──────────────────────────────────────────────────────────
"flyers": [
    {
        "id": "flyers_grammar_006",
        "name": "superlative_adjectives",
        "pattern": "the + adjective-est + noun | the most + adjective + noun",
        "topic_ids": ["topic_in_class", "topic_market", "topic_social"],
        "examples": [
            {"sentence": "He is the best student in class.", "context": "praising a student"},
            {"sentence": "This is the cheapest fruit at the market.", "context": "shopping for value"},
            {"sentence": "That was the most interesting lesson.", "context": "end-of-day reflection"},
            {"sentence": "She is the tallest student in the school.", "context": "describing a classmate"},
            {"sentence": "It was the longest meeting this week.", "context": "colleague small talk"}
        ],
        "common_mistakes": [
            {"wrong": "He is the most best student.", "correct": "He is the best student."},
            {"wrong": "This is most cheap.", "correct": "This is the cheapest."}
        ],
        "builds_on": ["movers_grammar_007"]
    },
    {
        "id": "flyers_grammar_007",
        "name": "adverbs_of_frequency",
        "pattern": "Subject + always/usually/often/sometimes/never + verb",
        "topic_ids": ["topic_social", "topic_in_class", "topic_health"],
        "examples": [
            {"sentence": "I always do my homework.", "context": "describing a good habit"},
            {"sentence": "She sometimes helps the teacher.", "context": "classroom routine"},
            {"sentence": "We never go to school on Sunday.", "context": "talking about schedule"},
            {"sentence": "He usually takes the bus to school.", "context": "travel routine"},
            {"sentence": "They often meet at the market.", "context": "social habit"}
        ],
        "common_mistakes": [
            {"wrong": "I go always to school.", "correct": "I always go to school."},
            {"wrong": "He never is late.", "correct": "He is never late."}
        ],
        "builds_on": ["starters_grammar_004"]
    },
    {
        "id": "flyers_grammar_008",
        "name": "first_conditional",
        "pattern": "If + subject + present simple, subject + will + verb",
        "topic_ids": ["topic_giving_instructions", "topic_travel", "topic_social"],
        "examples": [
            {"sentence": "If it rains, we will stay inside.", "context": "planning outdoor activity"},
            {"sentence": "If you finish early, you can go home.", "context": "teacher instruction"},
            {"sentence": "If you study hard, you will do well.", "context": "encouraging a student"},
            {"sentence": "If I buy a ticket, I will travel to Hue.", "context": "planning a trip"},
            {"sentence": "If the meeting is late, I will call you.", "context": "colleague arrangement"}
        ],
        "common_mistakes": [
            {"wrong": "If it will rain, we stay inside.", "correct": "If it rains, we will stay inside."},
            {"wrong": "If you will study, you pass.", "correct": "If you study, you will pass."}
        ]
    },
    {
        "id": "flyers_grammar_009",
        "name": "question_how_long_often",
        "pattern": "How long/How often + auxiliary + subject + verb?",
        "topic_ids": ["topic_social", "topic_health", "topic_travel"],
        "examples": [
            {"sentence": "How long is the meeting?", "context": "checking schedule"},
            {"sentence": "How often do you go to the market?", "context": "social chat"},
            {"sentence": "How long have you been a teacher?", "context": "getting to know a colleague"},
            {"sentence": "How often does he take medicine?", "context": "health check"},
            {"sentence": "How long is the train journey?", "context": "planning travel"}
        ],
        "common_mistakes": [
            {"wrong": "How long you study English?", "correct": "How long have you studied English?"},
            {"wrong": "How often you go?", "correct": "How often do you go?"}
        ],
        "builds_on": ["movers_grammar_009"]
    },
    {
        "id": "flyers_grammar_010",
        "name": "too_adjective",
        "pattern": "too + adjective + (to + verb)",
        "topic_ids": ["topic_market", "topic_health", "topic_in_class"],
        "examples": [
            {"sentence": "The bill is too expensive.", "context": "complaining about a price"},
            {"sentence": "This exercise is too difficult for me.", "context": "student asking for help"},
            {"sentence": "It is too hot to go outside.", "context": "weather comment"},
            {"sentence": "The music is too loud.", "context": "asking to turn it down"},
            {"sentence": "The instructions are too long.", "context": "giving feedback on a task"}
        ],
        "common_mistakes": [
            {"wrong": "The bill is very too expensive.", "correct": "The bill is too expensive."},
            {"wrong": "It too hot.", "correct": "It is too hot."}
        ]
    }
],

# ── KET ─────────────────────────────────────────────────────────────
"ket": [
    {
        "id": "ket_grammar_006",
        "name": "past_continuous",
        "pattern": "Subject + was/were + Verb-ing + (when + past simple clause)",
        "topic_ids": ["topic_in_class", "topic_travel", "topic_phone"],
        "examples": [
            {"sentence": "I was working when the phone rang.", "context": "describing an interruption"},
            {"sentence": "She was reading when the meeting started.", "context": "explaining lateness"},
            {"sentence": "We were waiting at the airport.", "context": "travel situation"},
            {"sentence": "The students were writing when I arrived.", "context": "describing classroom scene"},
            {"sentence": "He was cooking when I called him.", "context": "phone call timing"}
        ],
        "common_mistakes": [
            {"wrong": "I was work when the phone rang.", "correct": "I was working when the phone rang."},
            {"wrong": "She was read when it started.", "correct": "She was reading when it started."}
        ],
        "builds_on": ["movers_grammar_001", "movers_grammar_002"]
    },
    {
        "id": "ket_grammar_007",
        "name": "passive_voice_simple",
        "pattern": "Subject + was/were + Verb-ed/3 + (by + agent)",
        "topic_ids": ["topic_school_communication", "topic_giving_instructions", "topic_restaurant"],
        "examples": [
            {"sentence": "The report was written by the teacher.", "context": "discussing school tasks"},
            {"sentence": "The homework was checked yesterday.", "context": "confirming progress"},
            {"sentence": "The email was sent this morning.", "context": "updating a colleague"},
            {"sentence": "The food was prepared by the chef.", "context": "complimenting a meal"},
            {"sentence": "The meeting was organised by the principal.", "context": "school event"}
        ],
        "common_mistakes": [
            {"wrong": "The report written by the teacher.", "correct": "The report was written by the teacher."},
            {"wrong": "The homework was check yesterday.", "correct": "The homework was checked yesterday."}
        ]
    },
    {
        "id": "ket_grammar_008",
        "name": "so_such",
        "pattern": "so + adjective | such + (a/an) + adjective + noun",
        "topic_ids": ["topic_social", "topic_praise_correction", "topic_restaurant"],
        "examples": [
            {"sentence": "The lesson was so interesting.", "context": "end-of-day feedback"},
            {"sentence": "He is such a good student.", "context": "praising a learner"},
            {"sentence": "It was so hot yesterday.", "context": "weather small talk"},
            {"sentence": "She is such a kind colleague.", "context": "complimenting a workmate"},
            {"sentence": "The food was so good that we ordered more.", "context": "dining out"}
        ],
        "common_mistakes": [
            {"wrong": "He is so good student.", "correct": "He is such a good student."},
            {"wrong": "It was such interesting.", "correct": "It was so interesting."}
        ]
    },
    {
        "id": "ket_grammar_009",
        "name": "enough",
        "pattern": "adjective + enough | enough + noun",
        "topic_ids": ["topic_in_class", "topic_market", "topic_health"],
        "examples": [
            {"sentence": "Do we have enough chairs for the class?", "context": "preparing the room"},
            {"sentence": "The room is big enough for the meeting.", "context": "checking venue"},
            {"sentence": "I don't have enough money to buy this.", "context": "shopping at market"},
            {"sentence": "Is the student old enough to take the test?", "context": "checking eligibility"},
            {"sentence": "We have enough time to finish the task.", "context": "managing class time"}
        ],
        "common_mistakes": [
            {"wrong": "The room is enough big.", "correct": "The room is big enough."},
            {"wrong": "I have enough not money.", "correct": "I don't have enough money."}
        ]
    },
    {
        "id": "ket_grammar_010",
        "name": "question_tags",
        "pattern": "statement + , + opposite auxiliary + pronoun + ?",
        "topic_ids": ["topic_checking_understanding", "topic_social", "topic_health"],
        "examples": [
            {"sentence": "It is hot today, isn't it?", "context": "small talk about weather"},
            {"sentence": "You understand the lesson, don't you?", "context": "checking comprehension"},
            {"sentence": "She is a good student, isn't she?", "context": "confirming with colleague"},
            {"sentence": "We should confirm the schedule, shouldn't we?", "context": "planning together"},
            {"sentence": "The student has a headache, doesn't he?", "context": "checking health concern"}
        ],
        "common_mistakes": [
            {"wrong": "It is hot today, is it?", "correct": "It is hot today, isn't it?"},
            {"wrong": "You like chicken, isn't it?", "correct": "You like chicken, don't you?"}
        ],
        "builds_on": ["starters_grammar_003"]
    }
],

# ── PET ─────────────────────────────────────────────────────────────
"pet": [
    {
        "id": "pet_grammar_006",
        "name": "although_however_despite",
        "pattern": "Although + clause, clause | However, clause | Despite + noun/-ing, clause",
        "topic_ids": ["topic_school_communication", "topic_social", "topic_restaurant"],
        "examples": [
            {"sentence": "Although the lesson was long, the students enjoyed it.", "context": "reflecting on a class"},
            {"sentence": "The food was expensive. However, the quality was excellent.", "context": "restaurant review"},
            {"sentence": "Despite the delay, we arrived on time.", "context": "travel update"},
            {"sentence": "Although I apologised, she was still upset.", "context": "resolving a misunderstanding"},
            {"sentence": "Despite the bad weather, we had a productive meeting.", "context": "school event review"}
        ],
        "common_mistakes": [
            {"wrong": "Although it was long but they enjoyed it.", "correct": "Although it was long, they enjoyed it."},
            {"wrong": "Despite of the delay, we arrived.", "correct": "Despite the delay, we arrived."}
        ]
    },
    {
        "id": "pet_grammar_007",
        "name": "purpose_so_that",
        "pattern": "clause + so that + clause | clause + in order to + verb",
        "topic_ids": ["topic_giving_instructions", "topic_school_communication", "topic_travel"],
        "examples": [
            {"sentence": "I studied hard so that I could pass the exam.", "context": "explaining motivation"},
            {"sentence": "We left early in order to arrive on time.", "context": "travel planning"},
            {"sentence": "I wrote a report so that the principal could review it.", "context": "school admin work"},
            {"sentence": "She took medicine in order to feel better.", "context": "health routine"},
            {"sentence": "I called the parent so that they would know.", "context": "school communication"}
        ],
        "common_mistakes": [
            {"wrong": "I studied hard for pass the exam.", "correct": "I studied hard in order to pass the exam."},
            {"wrong": "I left early so that arrive on time.", "correct": "I left early so that I could arrive on time."}
        ]
    },
    {
        "id": "pet_grammar_008",
        "name": "have_something_done",
        "pattern": "Subject + have/had + object + past participle",
        "topic_ids": ["topic_health", "topic_travel", "topic_school_communication"],
        "examples": [
            {"sentence": "I had my car fixed last week.", "context": "telling a colleague about weekend"},
            {"sentence": "She had her hair cut before the meeting.", "context": "social chat"},
            {"sentence": "We had the report printed by the office.", "context": "school admin"},
            {"sentence": "I need to have my eyes checked by the doctor.", "context": "health appointment"},
            {"sentence": "He had his phone repaired at the shop.", "context": "explaining absence of phone"}
        ],
        "common_mistakes": [
            {"wrong": "I had fixed my car. (meaning someone else did it)", "correct": "I had my car fixed."},
            {"wrong": "I have the report print.", "correct": "I had the report printed."}
        ]
    },
    {
        "id": "pet_grammar_009",
        "name": "complex_questions",
        "pattern": "Do you know / Could you tell me + wh-word + subject + verb?",
        "topic_ids": ["topic_checking_understanding", "topic_restaurant", "topic_social"],
        "examples": [
            {"sentence": "Do you know where the nearest hospital is?", "context": "asking for directions"},
            {"sentence": "Could you tell me what time the meeting starts?", "context": "checking schedule"},
            {"sentence": "I wonder if the reservation has been confirmed.", "context": "restaurant booking"},
            {"sentence": "Do you have any idea how long the delay will be?", "context": "travel disruption"},
            {"sentence": "Can you explain why the student was absent?", "context": "school communication"}
        ],
        "common_mistakes": [
            {"wrong": "Do you know where is the hospital?", "correct": "Do you know where the hospital is?"},
            {"wrong": "Can you tell me what time does it start?", "correct": "Can you tell me what time it starts?"}
        ],
        "builds_on": ["movers_grammar_009", "flyers_grammar_009"]
    },
    {
        "id": "pet_grammar_010",
        "name": "linking_words",
        "pattern": "Furthermore / Moreover / On the other hand / Nevertheless + , + clause",
        "topic_ids": ["topic_school_communication", "topic_social", "topic_giving_instructions"],
        "examples": [
            {"sentence": "Furthermore, we need to prepare the worksheets.", "context": "staff meeting discussion"},
            {"sentence": "On the other hand, the students might prefer a project.", "context": "debating lesson ideas"},
            {"sentence": "In addition, the principal has approved the new schedule.", "context": "sharing school updates"},
            {"sentence": "Nevertheless, we should continue with the original plan.", "context": "decision making"},
            {"sentence": "Moreover, the feedback from parents has been very positive.", "context": "reporting to colleagues"}
        ],
        "common_mistakes": [
            {"wrong": "Furthermore we need to prepare.", "correct": "Furthermore, we need to prepare."},
            {"wrong": "On other hand, they might prefer.", "correct": "On the other hand, they might prefer."}
        ]
    }
]
} # END NEW_GRAMMAR


# ═══════════════════════════════════════════════════════════════════════
# MAIN SCRIPT
# ═══════════════════════════════════════════════════════════════════════

def validate_point(point, level):
    """Basic validation for a grammar point."""
    errors = []
    # Check ID format
    expected_prefix = f"{level}_grammar_"
    if not point["id"].startswith(expected_prefix):
        errors.append(f"  ID '{point['id']}' doesn't match level '{level}'")
    # Check required fields
    for field in ["id", "name", "pattern", "topic_ids", "examples", "common_mistakes"]:
        if field not in point:
            errors.append(f"  Missing field: {field}")
    # Check examples count (5-10)
    n_ex = len(point.get("examples", []))
    if n_ex < 5 or n_ex > 10:
        errors.append(f"  {point['id']}: {n_ex} examples (need 5-10)")
    # Check common_mistakes count (2-3)
    n_cm = len(point.get("common_mistakes", []))
    if n_cm < 2 or n_cm > 3:
        errors.append(f"  {point['id']}: {n_cm} common_mistakes (need 2-3)")
    return errors


def main():
    print("=" * 60)
    print("TinySteps — Phase 1: Grammar Generator")
    print("=" * 60)

    all_errors = []
    summary = []

    for level in ["starters", "movers", "flyers", "ket", "pet"]:
        filepath = os.path.join(GRAMMAR_DIR, f"{level}.json")

        # Read existing file
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            sys.exit(1)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        existing_ids = {p["id"] for p in data["grammar_points"]}
        new_points = NEW_GRAMMAR[level]

        # Check for duplicate IDs
        for p in new_points:
            if p["id"] in existing_ids:
                print(f"⚠️  Skipping duplicate: {p['id']}")
                continue
            # Validate
            errs = validate_point(p, level)
            if errs:
                all_errors.extend(errs)
            data["grammar_points"].append(p)

        # Update total
        data["total_points"] = len(data["grammar_points"])

        # Write back
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        summary.append(f"  {level:10s}: {data['total_points']} grammar points")
        print(f"✅ {level}: {data['total_points']} grammar points → {filepath}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for line in summary:
        print(line)
    total = sum(len(NEW_GRAMMAR[l]) for l in NEW_GRAMMAR)
    print(f"\n  New points added: {total}")
    print(f"  Total grammar points: {sum(5 + len(NEW_GRAMMAR[l]) for l in NEW_GRAMMAR)}")

    if all_errors:
        print(f"\n⚠️  Validation warnings ({len(all_errors)}):")
        for e in all_errors:
            print(e)
    else:
        print("\n✅ All validation checks passed!")

    print("\n" + "=" * 60)
    print("Phase 1 complete! Next: run generate_vocabulary.py (Phase 2)")
    print("=" * 60)


if __name__ == "__main__":
    main()
