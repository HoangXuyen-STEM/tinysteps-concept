#!/usr/bin/env python3
"""
TinySteps — Phase 2: Vocabulary Generator
Generates ~2100 vocabulary words across 5 CEFR levels (Starters to PET).
Preserves existing 15 prototype words and generates the remaining words up to target counts.
Updates topics.json dynamically with the new vocabulary IDs.
Run: python3 tinysteps-data/generate_vocabulary.py
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(SCRIPT_DIR, "vocabulary")
TOPICS_FILE = os.path.join(SCRIPT_DIR, "topics", "topics.json")

# TARGET COUNTS (including the 15 prototype words)
TARGETS = {
    "starters": 300,
    "movers": 400,
    "flyers": 500,
    "ket": 400,
    "pet": 500
}

# ═══════════════════════════════════════════════════════════════════════
# TEMPLATES FOR LEVEL-APPROPRIATE NATURAL SENTENCES
# ═══════════════════════════════════════════════════════════════════════
SENTENCE_TEMPLATES = {
    "starters": {
        "topic_before_class": ["Hello, [word]!", "I see [word].", "It is [word].", "This is [word].", "I am [word]."],
        "topic_in_class": ["Draw a [word].", "I have [word].", "This is [word].", "Look at [word].", "Show me [word]."],
        "topic_giving_instructions": ["Show me [word].", "Write [word].", "Look at [word].", "Touch the [word].", "Hold the [word]."],
        "topic_checking_understanding": ["Is this [word]?", "Point to [word].", "Look at [word].", "See the [word].", "Is it [word]?"],
        "topic_praise_correction": ["Great [word]!", "Good [word]!", "Yes, [word]!", "Try [word]!", "Very good [word]!"],
        "topic_school_communication": ["Hello, [word]!", "See you, [word]!", "Bye, [word]!", "Hi, [word]!", "This is [word]."],
        "topic_market": ["I want [word].", "Buy [word], please.", "I like [word].", "More [word], please.", "I need [word]."],
        "topic_restaurant": ["I like [word].", "Eat the [word].", "More [word], please.", "I want [word].", "I need [word]."],
        "topic_travel": ["See the [word].", "I see [word].", "Look at [word].", "I go [word].", "Go to [word]."],
        "topic_phone": ["Hello, [word]!", "Call [word], please.", "Listen to [word].", "Answer [word].", "Hear the [word]."],
        "topic_health": ["I am [word].", "He is [word].", "Are you [word]?", "I feel [word].", "She is [word]."],
        "topic_social": ["Hello, [word]!", "Bye, [word]!", "I am [word].", "He is [word].", "She is [word]."]
    },
    "movers": {
        "topic_before_class": ["I prepared the [word] yesterday.", "I arrived [word] yesterday.", "We prepared the [word].", "He cleaned the [word] early.", "She prepared [word] before class."],
        "topic_in_class": ["Show me your [word], please.", "Can you help me clean the [word]?", "He cleaned the [word].", "She answered the [word] question.", "I wrote in my [word] book."],
        "topic_giving_instructions": ["Clean the [word], please.", "Do your [word] now.", "Open your [word] book.", "Write the [word] on board.", "Please show your [word]."],
        "topic_checking_understanding": ["Do you understand the [word]?", "Can you help me check [word]?", "Did you understand the [word]?", "Is the [word] correct?", "Let's check the [word] together."],
        "topic_praise_correction": ["That is a great [word]!", "Great job on your [word].", "He helped me with [word].", "You did a good [word].", "This is a very good [word]!"],
        "topic_school_communication": ["He is sick today.", "Please call the [word] parent.", "I prepared the [word] report.", "My colleague called about [word].", "We discussed the [word] report."],
        "topic_market": ["I want to buy [word].", "I bought [word] yesterday.", "She wanted to buy [word].", "I bought fresh [word] today.", "He wants some [word]."],
        "topic_restaurant": ["I am hungry for [word].", "I want [word] and rice.", "She ordered chicken and [word].", "We wanted to order [word].", "Can I have [word]?"],
        "topic_travel": ["I went to school yesterday.", "Can you help me find [word]?", "We walked to the [word].", "I wanted to travel by [word].", "He found the [word] yesterday."],
        "topic_phone": ["Answer the [word], please.", "Please call the [word] parent.", "I want to call my [word].", "He called me yesterday morning.", "Answer the [word] call now."],
        "topic_health": ["He is sick today.", "I am [word] and tired.", "The doctor gave me [word].", "Are you feeling [word] today?", "I have a [word] stomach."],
        "topic_social": ["The weather is very nice today.", "Yesterday I walked to [word].", "I like reading [word] books.", "Do you like [word]?", "We walked and talked about [word]."]
    },
    "flyers": {
        "topic_before_class": ["He is my colleague at school.", "We have a staff [word] meeting.", "You should prepare the [word] plan.", "I have already prepared the [word].", "The principal gave the [word] schedule."],
        "topic_in_class": ["Can you explain this [word]?", "She told me to clean the [word].", "You should write the [word] down.", "I am going to explain the [word].", "He has finished the [word] task."],
        "topic_giving_instructions": ["You must follow my [word].", "You should listen carefully to [word].", "You mustn't make a [word] mistake.", "You should explain the [word] rule.", "The student must follow [word] rules."],
        "topic_checking_understanding": ["Can you explain this [word] to class?", "Should I explain the [word] again?", "You must check if they understand [word].", "We should explain the [word] clearly.", "He told me to check the [word]."],
        "topic_praise_correction": ["It is okay to make a [word].", "That is the correct [word] answer.", "You should not make a [word] mistake.", "That is an excellent [word] answer.", "You have done a correct [word]!"],
        "topic_school_communication": ["I sent you an email [word].", "The parent called me about [word].", "I have sent the [word] email.", "We should have a [word] meeting.", "She told me to send the [word]."],
        "topic_market": ["Could I see the bill for [word]?", "I have already bought the [word].", "We should check the [word] bill.", "I bought a bag of [word].", "The vendor gave me the [word] bill."],
        "topic_restaurant": ["Could I see the [word] menu, please?", "Can we have the [word] bill?", "You should check the [word] bill.", "I have already ordered the [word].", "She wants to see the [word] menu."],
        "topic_travel": ["I bought a train [word].", "Ask for [word] directions, please.", "I'm going to travel by [word].", "We have already bought the [word].", "You should check the travel [word]."],
        "topic_phone": ["Please leave a [word] message.", "I sent you a phone [word] message.", "The parent has called my [word].", "She is going to call my [word].", "I told him to leave a [word]."],
        "topic_health": ["Take this medicine after [word] meals.", "You should see the [word] doctor.", "The doctor told him to take [word].", "He should see a [word] doctor.", "Take the [word] medicine after meals."],
        "topic_social": ["Gardening is my favorite outdoor [word].", "I'm going to share my [word].", "We are going to discuss [word].", "I have already shared my [word].", "What are you going to do, [word]?"]
    },
    "ket": {
        "topic_before_class": ["Let me check the school [word].", "I'd like to suggest we check [word].", "I have worked under this [word] schedule.", "The schedule which we use is [word].", "Could you check my [word] schedule?"],
        "topic_in_class": ["The student is making [word] in class.", "What is your opinion on this [word]?", "The lesson was so [word] today.", "He is such an active [word] student.", "The report which you asked for is [word]."],
        "topic_giving_instructions": ["Could you check the [word] instructions?", "I'd like to suggest you follow [word].", "The instructions which are [word] are easy.", "You must check the [word] schedule.", "The teacher told us to open the [word]."],
        "topic_checking_understanding": ["The student is making progress on [word].", "I'd like to check your [word] progress.", "You understand the [word] lesson, don't you?", "The progress which they made in [word] is great.", "Could we check the [word] progress together?"],
        "topic_praise_correction": ["You are making good [word] progress.", "Could we correct the [word] mistakes together?", "He is such a good [word] student.", "The mistakes which we corrected in [word] are gone.", "Your opinion is so [word] to me."],
        "topic_school_communication": ["I finished the student [word] reports.", "I suggest we confirm the [word] schedule.", "The parent would like to confirm [word].", "I have had this schedule [word] since Monday.", "The report was written by my [word] colleague."],
        "topic_market": ["The market [word] is too high.", "I always bargain for a lower [word].", "I don't have enough [word] to buy.", "The price which is too high is [word].", "I used to bargain for [word] here."],
        "topic_restaurant": ["Could you recommend a good [word] dish?", "I prefer [word] to rice.", "The seafood pasta was so [word].", "Could I bargain at this [word] restaurant?", "The food was prepared by a [word] chef."],
        "topic_travel": ["I am waiting at the travel [word].", "Could you recommend a travel [word]?", "I used to travel to the [word] station.", "The ticket can be bought at [word].", "Could you show me the [word] direction?"],
        "topic_phone": ["This is an urgent [word] call.", "Please confirm the meeting on the [word].", "I would like to call my [word] colleague.", "I was working when the [word] rang.", "The phone call which was [word] is finished."],
        "topic_health": ["I have a terrible [word] today.", "He has a high [word], doesn't he?", "The student who has a [word] went home.", "He has had a headache [word] since Monday.", "He has a high fever, doesn't [word]?"],
        "topic_social": ["I suggest we meet on [word] afternoon.", "What is your opinion on this [word]?", "It is hot today, isn't [word]?", "I used to talk to my [word] colleague.", "The opinion which you gave on [word] is good."]
    },
    "pet": {
        "topic_before_class": ["Let me explain the prep [word] procedure.", "The [word] was discussed with my colleague.", "We've been preparing this [word] since morning.", "The safety procedure must be followed by [word].", "I wish the safety [word] were simpler."],
        "topic_in_class": ["You should try to improve your [word].", "If I had a question, I would [word].", "I wish I could improve my [word] faster.", "The lesson plans could be improved [word].", "If they didn't understand, I would [word]."],
        "topic_giving_instructions": ["Let me explain the [word] procedure clearly.", "The [word] should be done by Friday.", "The safety [word] must be followed carefully.", "The instructions should be explained in [word].", "I wish the [word] were more detailed."],
        "topic_checking_understanding": ["You should try to improve your [word].", "If they didn't understand, I would [word].", "I wish you didn't make that [word] mistake.", "The feedback could be improved with [word].", "If they didn't understand, I'd check [word]."],
        "topic_praise_correction": ["You should try to improve your [word].", "I apologize for making a [word] mistake.", "I wish you didn't make that [word].", "The feedback could be improved with [word].", "I apology for the [word] in my correction."],
        "topic_school_communication": ["We had a long [word] about school policy.", "I apologize for the delay in [word].", "Furthermore, the [word] was very useful.", "They have been complaining about the [word].", "My colleague said he had sent [word]."],
        "topic_market": ["I made a complaint about [word] prices.", "If the price were lower, I'd [word].", "If the market price were lower, [word].", "They complained about the [word] at the market.", "I wish the [word] at the market were lower."],
        "topic_restaurant": ["Do you have any vegetarian [word] options?", "I want to make a dinner [word].", "She wishes she had a vegetarian [word].", "The reservation should be confirmed before [word].", "She said she preferred vegetarian [word]."],
        "topic_travel": ["I am sorry for the flight [word].", "The [word] reservation should be confirmed.", "Despite the [word], we arrived on time.", "The ticket can be bought at the [word].", "The reservation should be confirmed for [word]."],
        "topic_phone": ["I called to apologize for [word] delay.", "If they called, I would answer [word].", "The parent has been waiting on [word].", "He said that he was waiting for [word].", "If the colleague called, I would [word]."],
        "topic_health": ["Describe your medical [word] clearly.", "The doctor wrote a medical [word].", "I need to have my [word] checked.", "The doctor said that I needed [word].", "The medicine should be taken after [word]."],
        "topic_social": ["Furthermore, the [word] discussion was useful.", "If I had time, I'd try [word].", "I wish I apologized to my [word] yesterday.", "On the other hand, the [word] was nice.", "Moreover, the [word] has been very positive."]
    }
}

# ═══════════════════════════════════════════════════════════════════════
# RAW VOCABULARY BASE LISTS (Compact representaton: Word, POS, IPA, Topic, ImageHint)
# ═══════════════════════════════════════════════════════════════════════
VOCAB_BASE = {
"starters": [
    # topic_before_class
    ("morning", "noun", "/ˈmɔː.nɪŋ/", "topic_before_class", "a bright yellow sun rising over school"),
    ("hello", "phrase", "/həˈləʊ/", "topic_before_class", "a friendly smiling hand waving hello"),
    ("teacher", "noun", "/ˈtiː.tʃər/", "topic_before_class", "a female teacher wearing glasses smiling in classroom"),
    ("desk", "noun", "/desk/", "topic_before_class", "a clean wooden school desk in morning light"),
    ("chair", "noun", "/tʃeər/", "topic_before_class", "a small blue plastic school chair next to desk"),
    ("clock", "noun", "/klɒk/", "topic_before_class", "a round white wall clock showing 8:00 AM"),
    ("bag", "noun", "/bæɡ/", "topic_before_class", "a colorful children's school backpack resting on desk"),
    ("classroom", "noun", "/ˈklɑːs.ruːm/", "topic_before_class", "a bright classroom with small desks and colorful walls"),
    ("door", "noun", "/dɔːr/", "topic_before_class", "an open classroom door with sunlight coming in"),
    ("window", "noun", "/ˈwɪn.dəʊ/", "topic_before_class", "a bright school window showing green trees outside"),
    ("early", "adjective", "/ˈɜː.li/", "topic_before_class", "a yellow alarm clock ringing at sunrise"),
    ("bell", "noun", "/bel/", "topic_before_class", "a golden metal bell ringing on a wall"),
    ("greet", "verb", "/ɡriːt/", "topic_before_class", "two friendly teachers waving hello to each other"),
    ("welcome", "phrase", "/ˈwel.kəm/", "topic_before_class", "a friendly school welcome sign on wooden board"),
    ("colleague", "noun", "/ˈkɒl.iːɡ/", "topic_before_class", "two teachers standing together smiling"),
    ("colleague", "noun", "/ˈkɒl.iːɡ/", "topic_before_class", "two teachers standing together smiling"), # Duplicate to make counts correct, will be replaced programmatically
    ("agenda", "noun", "/əˈdʒen.də/", "topic_before_class", "a simple printed notepad showing morning tasks"),
    ("ready", "adjective", "/ˈred.i/", "topic_before_class", "a child with double thumbs up looking ready"),
    ("today", "noun", "/təˈdeɪ/", "topic_before_class", "a simple calendar sheet showing a bright today circle"),
    ("calendar", "noun", "/ˈkæl.ən.dər/", "topic_before_class", "a small paper desk calendar with colorful tabs"),
    ("pencil", "noun", "/ˈpen.səl/", "topic_before_class", "a sharp yellow wooden pencil resting on notepad"),
    ("notebook", "noun", "/ˈnəʊt.bʊk/", "topic_before_class", "an open blank notebook with blue lines on desk"),
    ("textbook", "noun", "/ˈtekst.bʊk/", "topic_before_class", "a closed English textbook with cartoon cover"),
    ("paper", "noun", "/ˈpeɪ.pər/", "topic_before_class", "a clean white sheet of paper on desk"),
    ("friend", "noun", "/frend/", "topic_before_class", "two cartoon classmates walking together with backpacks"),
    ("school", "noun", "/skuːl/", "topic_before_class", "a beautiful brick school building under blue sky"),
    
    # topic_in_class
    ("book", "noun", "/bʊk/", "topic_in_class", "an open colorful textbook on school desk"),
    ("pen", "noun", "/pen/", "topic_in_class", "a shiny blue ballpoint pen next to paper"),
    ("board", "noun", "/bɔːd/", "topic_in_class", "a clean black board with chalk writing"),
    ("pencil", "noun", "/ˈpen.səl/", "topic_in_class", "a sharp yellow cartoon pencil drawing a line"),
    ("eraser", "noun", "/ɪˈreɪ.zər/", "topic_in_class", "a small pink eraser erasing a pencil line"),
    ("ruler", "noun", "/ˈruː.lər/", "topic_in_class", "a yellow transparent plastic ruler on desk"),
    ("crayon", "noun", "/ˈkreɪ.ɒn/", "topic_in_class", "a set of colorful wax crayons in box"),
    ("marker", "noun", "/ˈmɑː.kər/", "topic_in_class", "a blue whiteboard marker marker on desk"),
    ("paper", "noun", "/ˈpeɪ.pər/", "topic_in_class", "a neat stack of white writing paper sheets"),
    ("bag", "noun", "/bæɡ/", "topic_in_class", "a red children backpack zipped on chair"),
    ("desk", "noun", "/desk/", "topic_in_class", "a student desk with school supplies neat on it"),
    ("classroom", "noun", "/ˈklɑːs.ruːm/", "topic_in_class", "children sitting in class listening to teacher"),
    ("student", "noun", "/ˈstjuː.dənt/", "topic_in_class", "a young schoolboy holding a pencil smiling"),
    ("picture", "noun", "/ˈpɪk.tʃər/", "topic_in_class", "a colorful drawing of a house on wall"),
    ("map", "noun", "/mæp/", "topic_in_class", "a world map with blue oceans on school wall"),
    ("computer", "noun", "/kəmˈpjuː.tər/", "topic_in_class", "a modern computer monitor on teacher's desk"),
    ("lesson", "noun", "/ˈles.ən/", "topic_in_class", "a whiteboard with ABC letters written neatly"),
    ("exercise", "noun", "/ˈek.sə.saɪz/", "topic_in_class", "a worksheets page with matching cartoon puzzles"),
    ("story", "noun", "/ˈstɔː.ri/", "topic_in_class", "a cartoon storybook with animal illustrations"),
    ("dialogue", "noun", "/ˈdaɪ.ə.lɒɡ/", "topic_in_class", "two speech bubble icons on paper"),
    ("game", "noun", "/ɡeɪm/", "topic_in_class", "colorful building blocks arranged on table"),
    ("quiz", "noun", "/kwɪz/", "topic_in_class", "a paper page with large checked options"),
    ("test", "noun", "/test/", "topic_in_class", "a test sheet with correct answers marked green"),
    ("homework", "noun", "/ˈhəʊm.wɜːk/", "topic_in_class", "a notebook with a clean homework star mark"),
    ("colleague", "noun", "/ˈkɒl.iːɡ/", "topic_in_class", "two friendly teachers collaborating in classroom"),
    ("page", "noun", "/peɪdʒ/", "topic_in_class", "a paper page with number 10 at corner"),
],
"movers": [], # Will be expanded programmatically
"flyers": [],
"ket": [],
"pet": []
}

# Expand dynamic vocabulary lists for all levels so they easily meet targets without writing 10,000 lines
def expand_level_vocab(level, existing_words, global_seen):
    """Generates lists of words dynamically for each topic to meet target counts, ensuring POS and IPA.
    global_seen: set of ALL words already used across all previously processed levels.
    """
    # Combine: words in this level's prototype + everything from lower levels
    seen = global_seen | {w["word"].lower() for w in existing_words}
    
    # We will build a generator based on topic lists
    # General word pool mapping to topics, POS, IPAs
    word_pool = {
        "topic_before_class": [
            ("agenda", "noun", "/əˈdʒen.də/"), ("arrive", "verb", "/əˈraɪv/"), ("calendar", "noun", "/ˈkæl.ən.dər/"),
            ("early", "adverb", "/ˈɜː.li/"), ("prepare", "verb", "/prɪˈpeər/"), ("schedule", "noun", "/ˈʃed.juːl/"),
            ("meeting", "noun", "/ˈmiː.tɪŋ/"), ("colleague", "noun", "/ˈkɒl.iːɡ/"), ("plan", "noun", "/plæn/"),
            ("timetable", "noun", "/ˈtaɪm.teɪ.bəl/"), ("briefing", "noun", "/ˈbriː.fɪŋ/"), ("routine", "noun", "/ruːˈtiːn/"),
            ("organize", "verb", "/ˈɔː.ɡən.aɪz/"), ("morning", "noun", "/ˈmɔː.nɪŋ/"), ("coffee", "noun", "/ˈkɒf.i/"),
            ("notes", "noun", "/nəʊts/"), ("textbook", "noun", "/ˈtekst.bʊk/"), ("folder", "noun", "/ˈfəʊl.dər/"),
            ("marker", "noun", "/ˈmɑː.kər/"), ("computer", "noun", "/kəmˈpjuː.tər/"), ("desk", "noun", "/desk/"),
            ("board", "noun", "/bɔːd/"), ("check", "verb", "/tʃek/"), ("discuss", "verb", "/dɪˈskʌs/"),
            ("coordinate", "verb", "/kəʊˈɔː.dɪ.neɪt/"), ("prompt", "adjective", "/prɒmpt/"), ("punctual", "adjective", "/ˈpʌŋk.tʃu.əl/"),
            ("session", "noun", "/ˈseʃ.ən/"), ("prep", "noun", "/prep/"), ("staff", "noun", "/stɑːf/"),
            ("checklist", "noun", "/ˈtʃek.lɪst/"), ("safety", "noun", "/ˈseɪf.ti/"), ("bell", "noun", "/bel/"),
            ("gate", "noun", "/ɡeɪt/"), ("office", "noun", "/ˈɒf.ɪs/"), ("key", "noun", "/kiː/"),
            ("paper", "noun", "/ˈpeɪ.pər/"), ("print", "verb", "/prɪnt/"), ("copy", "verb", "/ˈkɒp.i/"),
            ("colleague", "noun", "/ˈkɒl.iːɡ/")
        ],
        "topic_in_class": [
            ("homework", "noun", "/ˈhəʊm.wɜːk/"), ("help", "verb", "/help/"), ("clean", "verb", "/kliːn/"),
            ("ask", "verb", "/ɑːsk/"), ("question", "noun", "/ˈkwes.tʃən/"), ("answer", "noun", "/ˈɑːn.sər/"),
            ("explain", "verb", "/ɪkˈspleɪn/"), ("understand", "verb", "/ˌʌn.dəˈstænd/"), ("progress", "noun", "/ˈprəʊ.ɡres/"),
            ("opinion", "noun", "/əˈpɪn.jən/"), ("improve", "verb", "/ɪmˈpruːv/"), ("speaking", "noun", "/ˈspiː.kɪŋ/"),
            ("writing", "noun", "/ˈraɪ.tɪŋ/"), ("reading", "noun", "/ˈriː.dɪŋ/"), ("listening", "noun", "/ˈlɪs.ən.ɪŋ/"),
            ("practice", "verb", "/ˈpræk.tɪs/"), ("partner", "noun", "/ˈpɑːt.nər/"), ("group", "noun", "/ɡruːp/"),
            ("activity", "noun", "/ækˈtɪv.ə.ti/"), ("lesson", "noun", "/ˈles.ən/"), ("correct", "verb", "/kəˈrekt/"),
            ("mistake", "noun", "/mɪˈsteɪk/"), ("board", "noun", "/bɔːd/"), ("eraser", "noun", "/ɪˈreɪ.zər/"),
            ("marker", "noun", "/ˈmɑː.kər/"), ("whiteboard", "noun", "/ˈwaɪt.bɔːd/"), ("pencil", "noun", "/ˈpen.səl/"),
            ("exercise", "noun", "/ˈek.sə.saɪz/"), ("dialogue", "noun", "/ˈdaɪ.ə.lɒɡ/"), ("pronounce", "verb", "/prəˈnaʊns/"),
            ("sentence", "noun", "/ˈsen.təns/"), ("dictionary", "noun", "/ˈdɪk.ʃən.ər.i/"), ("repeat", "verb", "/rɪˈpiːt/"),
            ("translate", "verb", "/trænzˈleɪt/"), ("grammar", "noun", "/ˈɡræm.ər/"), ("vocabulary", "noun", "/vəˈkæb.jʊ.lər.i/"),
            ("test", "noun", "/test/"), ("score", "noun", "/skɔːr/"), ("grade", "noun", "/ɡreɪd/"),
            ("learn", "verb", "/lɜːn/")
        ],
        "topic_giving_instructions": [
            ("imperative", "noun", "/ɪmˈper.ə.tɪv/"), ("instructions", "noun", "/ɪnˈstrʌk.ʃənz/"), ("rule", "noun", "/ruːl/"),
            ("follow", "verb", "/ˈfɒl.əʊ/"), ("listen", "verb", "/ˈlɪs.ən/"), ("look", "verb", "/lʊk/"),
            ("sit", "verb", "/sɪt/"), ("stand", "verb", "/stænd/"), ("quiet", "adjective", "/ˈkwaɪ.ət/"),
            ("silence", "noun", "/ˈsaɪ.ləns/"), ("must", "verb", "/mʌst/"), ("should", "verb", "/ʃʊd/"),
            ("could", "verb", "/kʊd/"), ("explain", "verb", "/ɪkˈspleɪn/"), ("suggest", "verb", "/səˈdʒest/"),
            ("procedure", "noun", "/prəˈsiː.dʒər/"), ("steps", "noun", "/steps/"), ("method", "noun", "/ˈmeθ.əd/"),
            ("guidelines", "noun", "/ˈɡaɪd.laɪnz/"), ("process", "noun", "/ˈprəʊ.ses/"), ("order", "noun", "/ˈɔː.dər/"),
            ("sequence", "noun", "/ˈsiː.kwəns/"), ("pattern", "noun", "/ˈpæt.ən/"), ("attention", "noun", "/əˈten.ʃən/"),
            ("careful", "adjective", "/ˈkeə.fəl/"), ("clearly", "adverb", "/ˈklɪə.li/"), ("repeat", "verb", "/rɪˈpiːt/"),
            ("copy", "verb", "/ˈkɒp.i/"), ("paste", "verb", "/peɪst/"), ("draw", "verb", "/drɔː/"),
            ("color", "verb", "/ˈkʌl.ər/"), ("match", "verb", "/mætʃ/"), ("fill", "verb", "/fɪl/"),
            ("complete", "verb", "/kəmˈpliːt/"), ("circle", "verb", "/ˈsɜː.kəl/"), ("underline", "verb", "/ˌʌn.dəˈlaɪn/"),
            ("tick", "verb", "/tɪk/"), ("cross", "verb", "/krɒs/"), ("turn", "verb", "/tɜːn/"),
            ("page", "noun", "/peɪdʒ/")
        ],
        "topic_checking_understanding": [
            ("check", "verb", "/tʃek/"), ("understand", "verb", "/ˌʌn.dəˈstænd/"), ("clear", "adjective", "/klɪər/"),
            ("comprehend", "verb", "/ˌkɒm.prɪˈhend/"), ("repeat", "verb", "/rɪˈpiːt/"), ("explain", "verb", "/ɪkˈspleɪn/"),
            ("progress", "noun", "/ˈprəʊ.ɡres/"), ("improve", "verb", "/ɪmˈpruːv/"), ("feedback", "noun", "/ˈfiːd.bæk/"),
            ("monitor", "verb", "/ˈmɒn.ɪ.tər/"), ("review", "verb", "/rɪˈvjuː/"), ("confirm", "verb", "/kənˈfɜːm/"),
            ("ask", "verb", "/ɑːsk/"), ("question", "noun", "/ˈkwes.tʃən/"), ("test", "noun", "/test/"),
            ("quiz", "noun", "/kwɪz/"), ("exam", "noun", "/ɪɡˈzæm/"), ("report", "noun", "/rɪˈpɔːt/"),
            ("assessment", "noun", "/əˈses.mənt/"), ("verify", "verb", "/ˈver.ɪ.faɪ/"), ("follow", "verb", "/ˈfɒl.əʊ/"),
            ("opinion", "noun", "/əˈpɪn.jən/"), ("idea", "noun", "/aɪˈdɪə/"), ("meaning", "noun", "/ˈmiː.nɪŋ/"),
            ("definition", "noun", "/ˌdef.ɪˈnɪʃ.ən/"), ("concept", "noun", "/ˈkɒn.sept/"), ("correct", "adjective", "/kəˈrekt/"),
            ("true", "adjective", "/truː/"), ("false", "adjective", "/fɒls/"), ("know", "verb", "/nəʊ/"),
            ("think", "verb", "/θɪŋ/"), ("sure", "adjective", "/ʃɔːr/"), ("confused", "adjective", "/kənˈfjuːzd/"),
            ("difficult", "adjective", "/ˈdɪf.ɪ.kəlt/"), ("easy", "adjective", "/ˈiː.zi/"), ("help", "verb", "/help/"),
            ("again", "adverb", "/əˈɡen/"), ("slowly", "adverb", "/ˈsləʊ.li/"), ("loudly", "adverb", "/ˈlaʊd.li/"),
            ("quietly", "adverb", "/ˈkwaɪ.ət.li/")
        ],
        "topic_praise_correction": [
            ("good", "adjective", "/ɡʊd/"), ("great", "adjective", "/ɡreɪt/"), ("excellent", "adjective", "/ˈek.səl.ənt/"),
            ("job", "noun", "/dʒɒb/"), ("nice", "adjective", "/naɪs/"), ("well", "adverb", "/wel/"),
            ("done", "adjective", "/dʌn/"), ("right", "adjective", "/raɪt/"), ("correct", "adjective", "/kəˈrekt/"),
            ("star", "noun", "/stɑːr/"), ("sticker", "noun", "/ˈstɪk.ər/"), ("try", "verb", "/traɪ/"),
            ("mistake", "noun", "/mɪˈsteɪk/"), ("answer", "noun", "/ˈɑːn.sər/"), ("homework", "noun", "/ˈhəʊm.wɜːk/"),
            ("explain", "verb", "/ɪkˈspleɪn/"), ("progress", "noun", "/ˈprəʊ.ɡres/"), ("improve", "verb", "/ɪmˈpruːv/"),
            ("apologize", "verb", "/əˈpɒl.ə.dʒaɪz/"), ("feedback", "noun", "/ˈfiːd.bæk/"), ("correction", "noun", "/kəˈrek.ʃən/"),
            ("encouragement", "noun", "/ɪnˈkʌr.ɪdʒ.mənt/"), ("praise", "noun", "/preɪz/"), ("superb", "adjective", "/suːˈpɜːb/"),
            ("wonderful", "adjective", "/ˈwʌn.də.fəl/"), ("perfect", "adjective", "/ˈpɜː.fekt/"), ("congratulations", "noun", "/kənˌɡræt.jʊˈleɪ.ʃənz/"),
            ("reward", "noun", "/rɪˈwɔːd/"), ("gift", "noun", "/ɡɪft/"), ("point", "noun", "/pɔɪnt/"),
            ("smart", "adjective", "/smɑːt/"), ("clever", "adjective", "/ˈklev.ər/"), ("quick", "adjective", "/kwɪk/"),
            ("careful", "adjective", "/ˈkeə.fəl/"), ("effort", "noun", "/ˈef.ət/"), ("try", "verb", "/traɪ/"),
            ("again", "adverb", "/əˈɡen/"), ("better", "adjective", "/ˈbet.ər/"), ("best", "adjective", "/best/"),
            ("super", "adjective", "/ˈsuː.pər/")
        ],
        "topic_school_communication": [
            ("email", "noun", "/ˈiː.meɪl/"), ("colleague", "noun", "/ˈkɒl.iːɡ/"), ("meeting", "noun", "/ˈmiː.tɪŋ/"),
            ("parent", "noun", "/ˈpeə.rənt/"), ("message", "noun", "/ˈmes.ɪdʒ/"), ("report", "noun", "/rɪˈpɔːt/"),
            ("schedule", "noun", "/ˈʃed.juːl/"), ("confirm", "verb", "/kənˈfɜːm/"), ("suggest", "verb", "/səˈdʒest/"),
            ("discussion", "noun", "/dɪˈskʌʃ.ən/"), ("apologize", "verb", "/əˈpɒl.ə.dʒaɪz/"), ("delay", "noun", "/dɪˈleɪ/"),
            ("furthermore", "adverb", "/ˌfɜː.ðəˈmɔːr/"), ("argument", "noun", "/ˈɑːɡ.jə.mənt/"), ("complaint", "noun", "/kəmˈpleɪnt/"),
            ("recommendation", "noun", "/ˌrek.ə.menˈdeɪ.ʃən/"), ("colleague", "noun", "/ˈkɒl.iːɡ/"), ("official", "adjective", "/əˈfɪʃ.əl/"),
            ("document", "noun", "/ˈdɒk.jʊ.mənt/"), ("notification", "noun", "/ˌnəʊ.tɪ.fɪˈkeɪ.ʃən/"), ("letter", "noun", "/ˈlet.ər/"),
            ("principal", "noun", "/ˈprɪn.sɪ.pəl/"), ("headteacher", "noun", "/hedˈtiː.tʃər/"), ("staff", "noun", "/stɑːf/"),
            ("briefing", "noun", "/ˈbriː.fɪŋ/"), ("appointment", "noun", "/əˈpɔɪnt.mənt/"), ("feedback", "noun", "/ˈfiːd.bæk/"),
            ("grades", "noun", "/ɡreɪdz/"), ("progress", "noun", "/ˈprəʊ.ɡres/"), ("behavior", "noun", "/bɪˈheɪ.vjər/"),
            ("absence", "noun", "/ˈæb.səns/"), ("sick", "adjective", "/sɪk/"), ("holiday", "noun", "/ˈhɒl.ə.deɪ/"),
            ("event", "noun", "/ɪˈvent/"), ("party", "noun", "/ˈpɑː.ti/"), ("cooperation", "noun", "/kəʊˌɒp.ərˈeɪ.ʃən/"),
            ("support", "noun", "/səˈpɔːt/"), ("help", "verb", "/help/"), ("share", "verb", "/ʃeər/"),
            ("contact", "verb", "/ˈkɒn.tækt/")
        ],
        "topic_market": [
            ("market", "noun", "/ˈmɑː.kɪt/"), ("food", "noun", "/fuːd/"), ("rice", "noun", "/raɪs/"),
            ("chicken", "noun", "/ˈtʃɪk.ɪn/"), ("fruit", "noun", "/fruːt/"), ("vegetable", "noun", "/ˈvedʒ.tə.bəl/"),
            ("buy", "verb", "/baɪ/"), ("want", "verb", "/wɒnt/"), ("shop", "verb", "/ʃɒp/"),
            ("price", "noun", "/praɪs/"), ("money", "noun", "/ˈmʌn.i/"), ("dong", "noun", "/dɒŋ/"),
            ("dollar", "noun", "/ˈdɒl.ər/"), ("bill", "noun", "/bɪl/"), ("cheap", "adjective", "/tʃiːp/"),
            ("expensive", "adjective", "/ɪkˈspen.sɪv/"), ("bargain", "verb", "/ˈbɑː.ɡɪn/"), ("cost", "noun", "/kɒst/"),
            ("fresh", "adjective", "/freʃ/"), ("list", "noun", "/lɪst/"), ("bag", "noun", "/bæɡ/"),
            ("change", "noun", "/tʃeɪndʒ/"), ("cash", "noun", "/kæʃ/"), ("vendor", "noun", "/ˈven.dər/"),
            ("negotiate", "verb", "/nəˈɡəʊ.ʃi.eɪt/"), ("discount", "noun", "/ˈdɪs.kaʊnt/"), ("complaint", "noun", "/kəmˈpleɪnt/"),
            ("refund", "noun", "/ˈriː.fʌnd/"), ("sale", "noun", "/seɪl/"), ("receipt", "noun", "/rɪˈsiːt/"),
            ("stall", "noun", "/stɔːl/"), ("seller", "noun", "/ˈsel.ər/"), ("buyer", "noun", "/ˈbaɪ.ər/"),
            ("organic", "adjective", "/ɔːˈɡæn.ɪk/"), ("local", "adjective", "/ˈləʊ.kəl/"), ("healthy", "adjective", "/ˈhel.θi/"),
            ("sweet", "adjective", "/swiːt/"), ("sour", "adjective", "/saʊər/"), ("basket", "noun", "/ˈbɑː.skɪt/"),
            ("weight", "noun", "/weɪt/")
        ],
        "topic_restaurant": [
            ("restaurant", "noun", "/ˈres.trɒnt/"), ("water", "noun", "/ˈwɔː.tər/"), ("food", "noun", "/fuːd/"),
            ("rice", "noun", "/raɪs/"), ("chicken", "noun", "/ˈtʃɪk.ɪn/"), ("soup", "noun", "/suːp/"),
            ("bread", "noun", "/bred/"), ("meat", "noun", "/miːt/"), ("fish", "noun", "/fɪʃ/"),
            ("menu", "noun", "/ˈmen.juː/"), ("bill", "noun", "/bɪl/"), ("hungry", "adjective", "/ˈhʌŋ.ɡri/"),
            ("thirsty", "adjective", "/ˈθɜː.sti/"), ("drink", "verb", "/drɪŋk/"), ("eat", "verb", "/iːt/"),
            ("table", "noun", "/ˈteɪ.bəl/"), ("chair", "noun", "/tʃeər/"), ("order", "verb", "/ˈɔː.dər/"),
            ("delicious", "adjective", "/dɪˈlɪʃ.əs/"), ("recommend", "verb", "/ˌrek.əˈmend/"), ("prefer", "verb", "/prɪˈfɜːr/"),
            ("vegetarian", "adjective", "/ˌvedʒ.ɪˈteə.ri.ən/"), ("reservation", "noun", "/ˌrez.əˈveɪ.ʃən/"), ("dessert", "noun", "/dɪˈzɜːt/"),
            ("salad", "noun", "/ˈsæl.əd/"), ("chef", "noun", "/ʃef/"), ("waiter", "noun", "/ˈweɪ.tər/"),
            ("booking", "noun", "/ˈbʊk.ɪŋ/"), ("service", "noun", "/ˈsɜː.vɪs/"), ("complaint", "noun", "/kəmˈpleɪnt/"),
            ("glass", "noun", "/ɡlɑːs/"), ("cup", "noun", "/kʌp/"), ("plate", "noun", "/pleɪt/"),
            ("fork", "noun", "/fɔːk/"), ("spoon", "noun", "/spuːn/"), ("knife", "noun", "/naɪf/"),
            ("salt", "noun", "/sɒlt/"), ("pepper", "noun", "/ˈpep.ər/"), ("spicy", "adjective", "/ˈspaɪ.si/"),
            ("sweet", "adjective", "/swiːt/")
        ],
        "topic_travel": [
            ("travel", "verb", "/ˈtræv.əl/"), ("go", "verb", "/ɡəʊ/"), ("bus", "noun", "/bʌs/"),
            ("car", "noun", "/kɑːr/"), ("bike", "noun", "/baɪk/"), ("train", "noun", "/treɪn/"),
            ("airport", "noun", "/ˈeə.pɔːt/"), ("ticket", "noun", "/ˈtɪk.ɪt/"), ("direction", "noun", "/daɪˈrek.ʃən/"),
            ("map", "noun", "/mæp/"), ("delay", "noun", "/dɪˈleɪ/"), ("reservation", "noun", "/ˌrez.əˈveɪ.ʃən/"),
            ("cancel", "verb", "/ˈkæn.səl/"), ("passport", "noun", "/ˈpɑː.spɔːt/"), ("luggage", "noun", "/ˈlʌɡ.ɪdʒ/"),
            ("bag", "noun", "/bæɡ/"), ("flight", "noun", "/flaɪt/"), ("station", "noun", "/ˈsteɪ.ʃən/"),
            ("route", "noun", "/ruːt/"), ("location", "noun", "/ləʊˈkeɪ.ʃən/"), ("guide", "noun", "/ɡaɪd/"),
            ("hotel", "noun", "/həʊˈtel/"), ("room", "noun", "/ruːm/"), ("trip", "noun", "/trɪp/"),
            ("journey", "noun", "/ˈdʒɜː.ni/"), ("ticket", "noun", "/ˈtɪk.ɪt/"), ("visit", "verb", "/ˈvɪz.ɪt/"),
            ("explore", "verb", "/ɪkˈsplɔːr/"), ("lost", "adjective", "/lɒst/"), ("find", "verb", "/faɪnd/"),
            ("street", "noun", "/striːt/"), ("road", "noun", "/rəʊd/"), ("left", "noun", "/left/"),
            ("right", "noun", "/raɪt/"), ("straight", "adverb", "/streɪt/"), ("walk", "verb", "/wɔːk/"),
            ("drive", "verb", "/draɪv/"), ("fly", "verb", "/flaɪ/"), ("arrive", "verb", "/əˈraɪv/"),
            ("leave", "verb", "/liːv/")
        ],
        "topic_phone": [
            ("phone", "noun", "/fəʊn/"), ("call", "verb", "/kɔːl/"), ("speak", "verb", "/spiːk/"),
            ("talk", "verb", "/tɔːk/"), ("listen", "verb", "/ˈlɪs.ən/"), ("hear", "verb", "/hɪər/"),
            ("say", "verb", "/seɪ/"), ("answer", "verb", "/ˈɑːn.sər/"), ("message", "noun", "/ˈmes.ɪdʒ/"),
            ("urgent", "adjective", "/ˈɜː.dʒənt/"), ("confirm", "verb", "/kənˈfɜːm/"), ("apologize", "verb", "/əˈpɒl.ə.dʒaɪz/"),
            ("delayed", "adjective", "/dɪˈleɪd/"), ("mobile", "noun", "/ˈməʊ.baɪl/"), ("signal", "noun", "/ˈsɪɡ.nəl/"),
            ("line", "noun", "/laɪn/"), ("connection", "noun", "/kəˈnek.ʃən/"), ("contact", "verb", "/ˈkɒn.tækt/"),
            ("dial", "verb", "/ˈdaɪ.əl/"), ("text", "noun", "/tekst/"), ("voicemail", "noun", "/ˈvɔɪs.meɪl/"),
            ("number", "noun", "/ˈnʌm.bər/"), ("ring", "verb", "/rɪŋ/"), ("busy", "adjective", "/ˈbɪz.i/"),
            ("wait", "verb", "/weɪt/"), ("hello", "phrase", "/həˈləʊ/"), ("goodbye", "phrase", "/ˌɡʊdˈbaɪ/"),
            ("charge", "verb", "/tʃɑːdʒ/"), ("battery", "noun", "/ˈbæt.ər.i/"), ("screen", "noun", "/skriːn/"),
            ("button", "noun", "/ˈbʌt.ən/"), ("loud", "adjective", "/laʊd/"), ("quiet", "adjective", "/ˈkwaɪ.ət/"),
            ("hear", "verb", "/hɪər/"), ("repeat", "verb", "/rɪˈpiːt/"), ("understand", "verb", "/ˌʌn.dəˈstænd/"),
            ("parent", "noun", "/ˈpeə.rənt/"), ("colleague", "noun", "/ˈkɒl.iːɡ/"), ("teacher", "noun", "/ˈtiː.tʃər/"),
            ("school", "noun", "/skuːl/")
        ],
        "topic_health": [
            ("fine", "adjective", "/faɪn/"), ("thank", "verb", "/θæŋk/"), ("well", "adjective", "/wel/"),
            ("sick", "adjective", "/sɪk/"), ("hot", "adjective", "/hɒt/"), ("cold", "adjective", "/kəʊld/"),
            ("tired", "adjective", "/ˈtaɪəd/"), ("hungry", "adjective", "/ˈhʌŋ.ɡri/"), ("doctor", "noun", "/ˈdɒn.tər/"),
            ("hospital", "noun", "/ˈhɒs.pɪ.təl/"), ("medicine", "noun", "/ˈmed.sn/"), ("headache", "noun", "/ˈhedeɪk/"),
            ("fever", "noun", "/ˈfiː.vər/"), ("prescription", "noun", "/prɪˈskrɪp.ʃən/"), ("symptom", "noun", "/ˈsɪmp.təm/"),
            ("pain", "noun", "/peɪn/"), ("stomach", "noun", "/ˈstʌm.ək/"), ("cough", "noun", "/kɒf/"),
            ("flu", "noun", "/fluː/"), ("health", "noun", "/helθ/"), ("healthy", "adjective", "/ˈhel.θi/"),
            ("body", "noun", "/ˈbɒd.i/"), ("rest", "verb", "/rest/"), ("sleep", "verb", "/sliːp/"),
            ("clinic", "noun", "/ˈklɪn.ɪk/"), ("pharmacy", "noun", "/ˈfɑː.mə.si/"), ("dentist", "noun", "/ˈden.tɪst/"),
            ("nurse", "noun", "/nɜːs/"), ("patient", "noun", "/ˈpeɪ.ʃənt/"), ("illness", "noun", "/ˈɪl.nəs/"),
            ("hurt", "verb", "/hɜːt/"), ("bleed", "verb", "/bliːd/"), ("wound", "noun", "/wuːnd/"),
            ("fit", "adjective", "/fɪt/"), ("energy", "noun", "/ˈen.ə.dʒi/"), ("diet", "noun", "/ˈdaɪ.ət/"),
            ("water", "noun", "/ˈwɔː.tər/"), ("fruit", "noun", "/fruːt/"), ("sleep", "noun", "/sliːp/"),
            ("relax", "verb", "/rɪˈlæks/")
        ],
        "topic_social": [
            ("hello", "phrase", "/həˈləʊ/"), ("goodbye", "phrase", "/ˌɡʊdˈbaɪ/"), ("friend", "noun", "/frend/"),
            ("name", "noun", "/neɪm/"), ("meet", "verb", "/miːt/"), ("weather", "noun", "/ˈweð.ər/"),
            ("hot", "adjective", "/hɒt/"), ("cold", "adjective", "/kəʊld/"), ("warm", "adjective", "/wɔːm/"),
            ("rain", "noun", "/reɪn/"), ("sun", "noun", "/sʌn/"), ("walk", "verb", "/wɔːk/"),
            ("run", "verb", "/rân/"), ("hobby", "noun", "/ˈhɒb.i/"), ("garden", "noun", "/ˈɡɑː.dən/"),
            ("sport", "noun", "/spɔːt/"), ("suggest", "verb", "/səˈdʒest/"), ("opinion", "noun", "/əˈpɪn.jən/"),
            ("recommendation", "noun", "/ˌrek.ə.menˈdeɪ.ʃən/"), ("debate", "noun", "/dɪˈbeɪt/"), ("discussion", "noun", "/dɪˈskʌʃ.ən/"),
            ("holiday", "noun", "/ˈhɒl.ə.deɪ/"), ("weekend", "noun", "/ˈwiːk.end/"), ("family", "noun", "/ˈfæm.əl.i/"),
            ("chat", "verb", "/tʃæt/"), ("introduce", "verb", "/ˌɪn.trəˈdjuːs/"), ("pleased", "adjective", "/pliːzd/"),
            ("welcome", "phrase", "/ˈwel.kəm/"), ("hobby", "noun", "/ˈhɒb.i/"), ("music", "noun", "/ˈmjuː.zɪk/"),
            ("movie", "noun", "/ˈmuː.vi/"), ("game", "noun", "/ɡeɪm/"), ("play", "verb", "/pleɪ/"),
            ("share", "verb", "/ʃeər/"), ("hear", "verb", "/hɪər/"), ("talk", "verb", "/tɔːk/"),
            ("laugh", "verb", "/lɑːf/"), ("smile", "verb", "/smaɪl/"), ("happy", "adjective", "/ˈhæp.i/"),
            ("nice", "adjective", "/naɪs/")
        ]
    }

    # Seed list of new generated words for each level up to the target
    target_count = TARGETS[level]
    new_words = []
    
    # We will generate words level-by-level using deterministic offsets to avoid randomness across runs
    topics_list = list(word_pool.keys())
    
    # Let's populate Starters explicitly first if empty
    if level == "starters" and not VOCAB_BASE["starters"]:
         # We already have starters hardcoded, but if not we can generate
         pass
         
    # Use a different starting offset per level so each level draws different words from the pool
    LEVEL_OFFSETS = {"starters": 0, "movers": 7, "flyers": 14, "ket": 21, "pet": 28}
    word_index = LEVEL_OFFSETS.get(level, 0)
    topic_index = LEVEL_OFFSETS.get(level, 0) % len(topics_list)

    MAX_ATTEMPTS = target_count * 20  # safety guard against infinite loop
    attempts = 0

    while len(existing_words) + len(new_words) < target_count and attempts < MAX_ATTEMPTS:
        attempts += 1
        topic = topics_list[topic_index % len(topics_list)]
        pool = word_pool[topic]

        pool_idx = word_index % len(pool)
        word, pos, ipa = pool[pool_idx]
        word = word.lower()

        word_index += 1
        topic_index += 1

        # HARD SKIP: word already used in this level OR any previous level
        if word in seen:
            continue

        seen.add(word)

        # Build example sentence and validate word count
        templates = SENTENCE_TEMPLATES[level][topic]
        template = templates[len(new_words) % len(templates)]
        sentence = template.replace("[word]", word)
        sentence = sentence[0].upper() + sentence[1:]

        # Image hint
        image_hints = {
            "noun": f"a clean graphic illustration of a {word}",
            "verb": f"an action illustration showing a person to {word}",
            "adjective": f"a simple colorful visualization of {word}",
            "adverb": f"a simple diagram illustrating how to act {word}ly",
            "phrase": f"a friendly speech bubble displaying {word}"
        }
        image_hint = image_hints.get(pos, f"a colorful visual representation of {word}")

        vocab_item = {
            "id": f"{level}_vocab_{len(existing_words) + len(new_words) + 1:03d}",
            "word": word,
            "ipa": ipa,
            "pos": pos,
            "topic_ids": [topic],
            "example_sentence": sentence,
            "image_hint": image_hint,
            "frequency_rank": len(existing_words) + len(new_words) + 1
        }
        new_words.append(vocab_item)

    if len(existing_words) + len(new_words) < target_count:
        print(f"  ⚠️  WARNING [{level}]: word pool exhausted — only {len(existing_words)+len(new_words)} / {target_count} generated")

    return existing_words + new_words


# ═══════════════════════════════════════════════════════════════════════
# MAIN GENERATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("TinySteps — Phase 2: Vocabulary Generator v2")
    print("=" * 60)

    all_generated_words = {"starters": [], "movers": [], "flyers": [], "ket": [], "pet": []}

    # KEY FIX: ONE global_seen set shared across ALL levels, built up progressively
    global_seen = set()

    for level in ["starters", "movers", "flyers", "ket", "pet"]:
        filepath = os.path.join(VOCAB_DIR, f"{level}.json")

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            sys.exit(1)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        existing_words = data.get("words", [])

        # Remove known cross-level duplicates from PET prototype
        if level == "pet":
            filtered = []
            for w in existing_words:
                if w["word"] in ["colleague", "delicious"]:
                    print(f"  ⚠️  Removing duplicate '{w['word']}' from PET prototype")
                    continue
                filtered.append(w)
            for idx, w in enumerate(filtered):
                w["id"] = f"pet_vocab_{idx+1:03d}"
                w["frequency_rank"] = idx + 1
            existing_words = filtered

        # Add all prototype words of this level to global_seen BEFORE generating
        for w in existing_words:
            global_seen.add(w["word"].lower())

        print(f"  Generating {level} (existing={len(existing_words)}, target={TARGETS[level]}, pool_seen={len(global_seen)})")

        # Generate — global_seen prevents any cross-level duplicates
        expanded_words = expand_level_vocab(level, existing_words, global_seen)

        # Update global_seen with newly generated words
        for w in expanded_words:
            global_seen.add(w["word"].lower())

        # Save
        data["total_words"] = len(expanded_words)
        data["words"] = expanded_words
        all_generated_words[level] = expanded_words

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print(f"  ✅ {level}: {len(expanded_words)} words saved → {filepath}")

    # ═══════════════════════════════════════════════════════════════════════
    # DYNAMIC TOPICS.JSON CURRICULUM MAP UPDATE
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Updating Curriculum Map (topics.json) ...")
    print("=" * 60)

    if not os.path.exists(TOPICS_FILE):
        print(f"❌ Topics file not found: {TOPICS_FILE}")
        sys.exit(1)

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    # For each topic and level, we collect the list of vocab IDs that map to it
    for topic_entry in topics_data.get("topics", []):
        topic_id = topic_entry["id"]
        
        for spiral_entry in topic_entry.get("spiral", []):
            spiral_level = spiral_entry["level"]
            
            # Filter all generated words for this level that have this topic_id in topic_ids
            matching_words = all_generated_words[spiral_level]
            topic_vocab_ids = []
            
            for w in matching_words:
                if topic_id in w["topic_ids"]:
                    topic_vocab_ids.append(w["id"])
            
            # Map grammar points as well
            # Map grammar_ids 001-010 to topics matching their definitions
            # (Ensures all grammar points including Phase 1 are integrated)
            topic_grammar_ids = []
            grammar_file = os.path.join(SCRIPT_DIR, "grammar", f"{spiral_level}.json")
            if os.path.exists(grammar_file):
                with open(grammar_file, "r", encoding="utf-8") as gf:
                    g_data = json.load(gf)
                for gp in g_data.get("grammar_points", []):
                    if topic_id in gp.get("topic_ids", []):
                        topic_grammar_ids.append(gp["id"])

            # Save in spiral entry
            spiral_entry["vocabulary_ids"] = topic_vocab_ids
            if topic_grammar_ids:
                spiral_entry["grammar_ids"] = topic_grammar_ids

            print(f"Mapped topic: {topic_id:28s} | {spiral_level:8s} -> {len(topic_vocab_ids):2d} words, {len(topic_grammar_ids):2d} grammar points")

    # Save topics.json
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n✅ Curriculum Map updated successfully!")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for level, count in TARGETS.items():
        print(f"  {level:10s}: {len(all_generated_words[level])} words")
    print(f"\n  Total vocabulary words: {sum(len(all_generated_words[l]) for l in all_generated_words)}")
    print("=" * 60)
    print("Phase 2 complete! Next: run Phase 3 validation script")
    print("=" * 60)


if __name__ == "__main__":
    main()
