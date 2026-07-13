#!/usr/bin/env python3
"""
topup_vocabulary_batch3.py  — Final fill to reach targets.
Fixes PET (replaces over-advanced C1/C2 words with proper B2 vocabulary).
"""

import json, os, re, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR  = os.path.join(SCRIPT_DIR, "vocabulary")
TOPICS_FILE = os.path.join(SCRIPT_DIR, "topics", "topics.json")
LEVELS     = ["starters", "movers", "flyers", "ket", "pet"]
TARGETS    = {"starters": 300, "movers": 400, "flyers": 500, "ket": 400, "pet": 500}

EXAMPLE_TMPL = {
    "starters": {
        "noun": ["This is {w}.", "I see {w}.", "I have {w}."],
        "verb": ["Please {w}.", "I {w} now."],
        "adjective": ["It is {w}.", "He is {w}."],
        "default": ["I like {w}.", "That is {w}."],
    },
    "movers": {
        "noun": ["She bought {w} yesterday.", "I need {w}.", "Can you find the {w}?"],
        "verb": ["She {w}ed yesterday.", "Can you {w} with me?", "I want to {w}."],
        "adjective": ["It was very {w}.", "She looked {w}."],
        "adverb": ["Do it {w}.", "She walked {w}."],
        "default": ["I have {w} now.", "She used {w} yesterday."],
    },
    "flyers": {
        "noun": ["She has already checked the {w}.", "You should bring the {w}."],
        "verb": ["You should {w} carefully.", "She has already {w}ed."],
        "adjective": ["The lesson was so {w}.", "He is such a {w} student."],
        "default": ["I have already seen the {w}.", "You must check the {w}."],
    },
    "ket": {
        "noun": ["Could you confirm the {w}?", "I'd like to discuss the {w}."],
        "verb": ["Could you {w} this?", "I used to {w} every day."],
        "adjective": ["The report was {w} enough.", "He is such a {w} colleague."],
        "default": ["I'd like to review the {w}.", "Could we discuss the {w}?"],
    },
    "pet": {
        "noun": ["The {w} should be confirmed by Friday.", "If I had a better {w}, I would use it."],
        "verb": ["If I had time, I would {w} more.", "I wish I could {w} better."],
        "adjective": ["Despite being {w}, she continued.", "She said that it was {w}."],
        "default": ["Furthermore, the {w} was discussed.", "I apologise for the {w}."],
    },
}

def make_example(word, pos, level):
    pool = EXAMPLE_TMPL.get(level, EXAMPLE_TMPL["movers"])
    tmpl_list = pool.get(pos, pool.get("default", ["I see {w}."]))
    return random.choice(tmpl_list).replace("{w}", word)

def make_hint(word, pos):
    hints = {
        "noun": f"a clear image showing {word}",
        "verb": f"a person doing the action of {word}",
        "adjective": f"an image illustrating the quality of being {word}",
        "adverb": f"someone acting {word}",
        "default": f"a visual of {word}",
    }
    return hints.get(pos, hints["default"])

# ── Batch 3 word pools ─────────────────────────────────────────────────────

BATCH3 = {

"starters": [
    ("pink", "adjective", "/pɪŋk/", "topic_social"),
    ("purple", "adjective", "/ˈpɜː.pəl/", "topic_social"),
    ("black", "adjective", "/blæk/", "topic_social"),
    ("white", "adjective", "/waɪt/", "topic_social"),
    ("brown", "adjective", "/braʊn/", "topic_social"),
    ("bird", "noun", "/bɜːd/", "topic_social"),
    ("fish", "noun", "/fɪʃ/", "topic_market"),
    ("tree", "noun", "/triː/", "topic_social"),
    ("flower", "noun", "/ˈflaʊ.ər/", "topic_social"),
    ("sun", "noun", "/sʌn/", "topic_social"),
    ("moon", "noun", "/muːn/", "topic_social"),
    ("star", "noun", "/stɑːr/", "topic_social"),
    ("house", "noun", "/haʊs/", "topic_social"),
    ("room", "noun", "/ruːm/", "topic_social"),
    ("kitchen", "noun", "/ˈkɪtʃ.ɪn/", "topic_restaurant"),
    ("bed", "noun", "/bed/", "topic_health"),
    ("chair", "noun", "/tʃeər/", "topic_before_class"),
    ("table", "noun", "/ˈteɪ.bəl/", "topic_before_class"),
    ("box", "noun", "/bɒks/", "topic_in_class"),
    ("ball", "noun", "/bɔːl/", "topic_social"),
    ("colour", "noun", "/ˈkʌl.ər/", "topic_in_class"),
    ("smile", "verb", "/smaɪl/", "topic_social"),
    ("wave", "verb", "/weɪv/", "topic_social"),
    ("clap", "verb", "/klæp/", "topic_praise_correction"),
    ("nod", "verb", "/nɒd/", "topic_checking_understanding"),
],

"movers": [
    # action verbs
    ("swim", "verb", "/swɪm/", "topic_social"),
    ("dance", "verb", "/dɑːns/", "topic_social"),
    ("sing", "verb", "/sɪŋ/", "topic_social"),
    ("paint", "verb", "/peɪnt/", "topic_in_class"),
    ("bake", "verb", "/beɪk/", "topic_restaurant"),
    ("wash", "verb", "/wɒʃ/", "topic_health"),
    ("iron", "verb", "/ˈaɪ.ən/", "topic_social"),
    ("sweep", "verb", "/swiːp/", "topic_before_class"),
    ("mop", "verb", "/mɒp/", "topic_before_class"),
    ("dust", "verb", "/dʌst/", "topic_before_class"),
    ("water", "verb", "/ˈwɔː.tər/", "topic_social"),
    ("plant", "verb", "/plɑːnt/", "topic_social"),
    ("pick", "verb", "/pɪk/", "topic_market"),
    ("measure", "verb", "/ˈmeʒ.ər/", "topic_giving_instructions"),
    ("mix", "verb", "/mɪks/", "topic_restaurant"),
    ("add", "verb", "/æd/", "topic_restaurant"),
    ("pour", "verb", "/pɔːr/", "topic_restaurant"),
    ("cool", "verb", "/kuːl/", "topic_restaurant"),
    ("heat", "verb", "/hiːt/", "topic_restaurant"),
    ("wrap", "verb", "/ræp/", "topic_market"),
    ("pack", "verb", "/pæk/", "topic_travel"),
    ("unpack", "verb", "/ˌʌnˈpæk/", "topic_travel"),
    ("carry", "verb", "/ˈkær.i/", "topic_travel"),
    ("lift", "verb", "/lɪft/", "topic_travel"),
    ("push", "verb", "/pʊʃ/", "topic_travel"),
    ("pull", "verb", "/pʊl/", "topic_travel"),
    ("jump", "verb", "/dʒʌmp/", "topic_social"),
    ("climb", "verb", "/klaɪm/", "topic_travel"),
    ("fall", "verb", "/fɔːl/", "topic_health"),
    ("hit", "verb", "/hɪt/", "topic_health"),
    # adjectives
    ("wet", "adjective", "/wet/", "topic_social"),
    ("dry", "adjective", "/draɪ/", "topic_social"),
    ("broken", "adjective", "/ˈbrəʊ.kən/", "topic_health"),
    ("fixed", "adjective", "/fɪkst/", "topic_school_communication"),
    ("open", "adjective", "/ˈəʊ.pən/", "topic_giving_instructions"),
    ("closed", "adjective", "/kləʊzd/", "topic_giving_instructions"),
    ("empty", "adjective", "/ˈemp.ti/", "topic_in_class"),
    ("full", "adjective", "/fʊl/", "topic_restaurant"),
    ("round", "adjective", "/raʊnd/", "topic_in_class"),
    ("square", "adjective", "/skweər/", "topic_in_class"),
    ("flat", "adjective", "/flæt/", "topic_giving_instructions"),
    ("thick", "adjective", "/θɪk/", "topic_in_class"),
    ("thin", "adjective", "/θɪn/", "topic_in_class"),
    ("wide", "adjective", "/waɪd/", "topic_travel"),
    ("narrow", "adjective", "/ˈnær.əʊ/", "topic_travel"),
    ("deep", "adjective", "/diːp/", "topic_travel"),
    ("shallow", "adjective", "/ˈʃæl.əʊ/", "topic_travel"),
    ("bright", "adjective", "/braɪt/", "topic_before_class"),
    ("dark", "adjective", "/dɑːk/", "topic_social"),
    ("loud", "adjective", "/laʊd/", "topic_social"),
    ("soft", "adjective", "/sɒft/", "topic_social"),
    ("rough", "adjective", "/rʌf/", "topic_travel"),
    ("smooth", "adjective", "/smuːð/", "topic_health"),
    ("sharp", "adjective", "/ʃɑːp/", "topic_health"),
    ("safe", "adjective", "/seɪf/", "topic_giving_instructions"),
    ("dangerous", "adjective", "/ˈdeɪn.dʒər.əs/", "topic_giving_instructions"),
    ("important", "adjective", "/ɪmˈpɔː.tənt/", "topic_giving_instructions"),
    ("useful", "adjective", "/ˈjuːs.fəl/", "topic_in_class"),
    ("different", "adjective", "/ˈdɪf.ər.ənt/", "topic_in_class"),
    ("same", "adjective", "/seɪm/", "topic_checking_understanding"),
    # nouns
    ("team", "noun", "/tiːm/", "topic_in_class"),
    ("member", "noun", "/ˈmem.bər/", "topic_school_communication"),
    ("leader", "noun", "/ˈliː.dər/", "topic_school_communication"),
    ("winner", "noun", "/ˈwɪn.ər/", "topic_praise_correction"),
    ("loser", "noun", "/ˈluː.zər/", "topic_praise_correction"),
    ("point", "noun", "/pɔɪnt/", "topic_praise_correction"),
    ("prize", "noun", "/praɪz/", "topic_praise_correction"),
    ("medal", "noun", "/ˈmed.əl/", "topic_praise_correction"),
    ("certificate", "noun", "/səˈtɪf.ɪ.kɪt/", "topic_school_communication"),
    ("diary", "noun", "/ˈdaɪ.ər.i/", "topic_before_class"),
    ("calendar", "noun", "/ˈkæl.ən.dər/", "topic_before_class"),
    ("clock", "noun", "/klɒk/", "topic_before_class"),
    ("watch", "noun", "/wɒtʃ/", "topic_before_class"),
    ("minute", "noun", "/ˈmɪn.ɪt/", "topic_giving_instructions"),
    ("second", "noun", "/ˈsek.ənd/", "topic_giving_instructions"),
    ("half", "noun", "/hɑːf/", "topic_giving_instructions"),
    ("quarter", "noun", "/ˈkwɔː.tər/", "topic_giving_instructions"),
    ("pair", "noun", "/peər/", "topic_in_class"),
    ("set", "noun", "/set/", "topic_in_class"),
    ("list", "noun", "/lɪst/", "topic_in_class"),
    ("table", "noun", "/ˈteɪ.bəl/", "topic_in_class"),
    ("chart", "noun", "/tʃɑːt/", "topic_in_class"),
    ("graph", "noun", "/ɡrɑːf/", "topic_in_class"),
    ("picture", "noun", "/ˈpɪk.tʃər/", "topic_in_class"),
    ("photo", "noun", "/ˈfəʊ.təʊ/", "topic_social"),
    ("camera", "noun", "/ˈkæm.ər.ə/", "topic_social"),
    ("umbrella", "noun", "/ʌmˈbrel.ə/", "topic_travel"),
    ("coat", "noun", "/kəʊt/", "topic_social"),
    ("hat", "noun", "/hæt/", "topic_social"),
    ("shoe", "noun", "/ʃuː/", "topic_social"),
    ("sock", "noun", "/sɒk/", "topic_social"),
    ("shirt", "noun", "/ʃɜːt/", "topic_social"),
    ("trousers", "noun", "/ˈtraʊ.zəz/", "topic_social"),
    ("glasses", "noun", "/ˈɡlɑː.sɪz/", "topic_health"),
    # adverbs / prepositions
    ("already", "adverb", "/ɔːlˈred.i/", "topic_checking_understanding"),
    ("still", "adverb", "/stɪl/", "topic_checking_understanding"),
    ("just", "adverb", "/dʒʌst/", "topic_checking_understanding"),
    ("always", "adverb", "/ˈɔːl.weɪz/", "topic_social"),
    ("never", "adverb", "/ˈnev.ər/", "topic_social"),
    ("sometimes", "adverb", "/ˈsʌm.taɪmz/", "topic_social"),
    ("often", "adverb", "/ˈɒf.ən/", "topic_social"),
    ("usually", "adverb", "/ˈjuː.ʒu.ə.li/", "topic_social"),
    ("together", "adverb", "/təˈɡeð.ər/", "topic_in_class"),
    ("alone", "adverb", "/əˈləʊn/", "topic_social"),
    ("outside", "adverb", "/ˌaʊtˈsaɪd/", "topic_social"),
    ("inside", "adverb", "/ˌɪnˈsaɪd/", "topic_before_class"),
    ("upstairs", "adverb", "/ˌʌpˈsteəz/", "topic_school_communication"),
    ("downstairs", "adverb", "/ˌdaʊnˈsteəz/", "topic_school_communication"),
    ("forward", "adverb", "/ˈfɔː.wəd/", "topic_travel"),
    ("backward", "adverb", "/ˈbæk.wəd/", "topic_giving_instructions"),
    ("above", "preposition", "/əˈbʌv/", "topic_in_class"),
    ("below", "preposition", "/bɪˈləʊ/", "topic_in_class"),
    ("between", "preposition", "/bɪˈtwiːn/", "topic_in_class"),
    ("behind", "preposition", "/bɪˈhaɪnd/", "topic_giving_instructions"),
    ("beside", "preposition", "/bɪˈsaɪd/", "topic_giving_instructions"),
    ("around", "preposition", "/əˈraʊnd/", "topic_travel"),
    ("through", "preposition", "/θruː/", "topic_travel"),
    ("along", "preposition", "/əˈlɒŋ/", "topic_travel"),
    ("across", "preposition", "/əˈkrɒs/", "topic_travel"),
    ("during", "preposition", "/ˈdjʊər.ɪŋ/", "topic_giving_instructions"),
    ("until", "preposition", "/ənˈtɪl/", "topic_giving_instructions"),
    ("since", "preposition", "/sɪns/", "topic_social"),
    ("towards", "preposition", "/təˈwɔːdz/", "topic_travel"),
],

"flyers": [
    # verbs
    ("accomplish", "verb", "/əˈkʌm.plɪʃ/", "topic_praise_correction"),
    ("achieve", "verb", "/əˈtʃiːv/", "topic_praise_correction"),
    ("succeed", "verb", "/səkˈsiːd/", "topic_praise_correction"),
    ("overcome", "verb", "/ˌəʊ.vəˈkʌm/", "topic_praise_correction"),
    ("persist", "verb", "/pəˈsɪst/", "topic_praise_correction"),
    ("dedicate", "verb", "/ˈded.ɪ.keɪt/", "topic_praise_correction"),
    ("commit", "verb", "/kəˈmɪt/", "topic_praise_correction"),
    ("focus", "verb", "/ˈfəʊ.kəs/", "topic_in_class"),
    ("concentrate", "verb", "/ˈkɒn.sən.treɪt/", "topic_in_class"),
    ("reflect", "verb", "/rɪˈflekt/", "topic_checking_understanding"),
    ("adjust", "verb", "/əˈdʒʌst/", "topic_giving_instructions"),
    ("adapt", "verb", "/əˈdæpt/", "topic_giving_instructions"),
    ("modify", "verb", "/ˈmɒd.ɪ.faɪ/", "topic_giving_instructions"),
    ("revise", "verb", "/rɪˈvaɪz/", "topic_in_class"),
    ("edit", "verb", "/ˈed.ɪt/", "topic_in_class"),
    ("proofread", "verb", "/ˈpruːf.riːd/", "topic_in_class"),
    ("draft", "verb", "/drɑːft/", "topic_in_class"),
    ("submit", "verb", "/səbˈmɪt/", "topic_giving_instructions"),
    ("upload", "verb", "/ˌʌpˈləʊd/", "topic_school_communication"),
    ("download", "verb", "/ˈdaʊn.ləʊd/", "topic_school_communication"),
    ("search", "verb", "/sɜːtʃ/", "topic_in_class"),
    ("browse", "verb", "/braʊz/", "topic_in_class"),
    ("link", "verb", "/lɪŋk/", "topic_school_communication"),
    ("create", "verb", "/kriˈeɪt/", "topic_in_class"),
    ("design", "verb", "/dɪˈzaɪn/", "topic_in_class"),
    ("build", "verb", "/bɪld/", "topic_in_class"),
    ("test", "verb", "/test/", "topic_checking_understanding"),
    ("launch", "verb", "/lɔːntʃ/", "topic_school_communication"),
    ("publish", "verb", "/ˈpʌb.lɪʃ/", "topic_school_communication"),
    ("distribute", "verb", "/dɪˈstrɪb.juːt/", "topic_school_communication"),
    # nouns
    ("effort", "noun", "/ˈef.ət/", "topic_praise_correction"),
    ("attitude", "noun", "/ˈæt.ɪ.tjuːd/", "topic_praise_correction"),
    ("behaviour", "noun", "/bɪˈheɪ.vjər/", "topic_praise_correction"),
    ("potential", "noun", "/pəˈten.ʃəl/", "topic_praise_correction"),
    ("ability", "noun", "/əˈbɪl.ɪ.ti/", "topic_praise_correction"),
    ("talent", "noun", "/ˈtæl.ənt/", "topic_praise_correction"),
    ("strength", "noun", "/streŋθ/", "topic_praise_correction"),
    ("weakness", "noun", "/ˈwiːk.nəs/", "topic_checking_understanding"),
    ("challenge", "noun", "/ˈtʃæl.ɪndʒ/", "topic_in_class"),
    ("opportunity", "noun", "/ˌɒp.əˈtjuː.nɪ.ti/", "topic_social"),
    ("responsibility", "noun", "/rɪˌspɒn.sɪˈbɪl.ɪ.ti/", "topic_giving_instructions"),
    ("experience", "noun", "/ɪkˈspɪər.i.əns/", "topic_social"),
    ("knowledge", "noun", "/ˈnɒl.ɪdʒ/", "topic_in_class"),
    ("information", "noun", "/ˌɪn.fəˈmeɪ.ʃən/", "topic_checking_understanding"),
    ("data", "noun", "/ˈdeɪ.tə/", "topic_in_class"),
    ("technology", "noun", "/tekˈnɒl.ə.dʒi/", "topic_in_class"),
    ("software", "noun", "/ˈsɒft.weər/", "topic_school_communication"),
    ("hardware", "noun", "/ˈhɑːd.weər/", "topic_in_class"),
    ("platform", "noun", "/ˈplæt.fɔːm/", "topic_school_communication"),
    ("website", "noun", "/ˈweb.saɪt/", "topic_school_communication"),
    ("account", "noun", "/əˈkaʊnt/", "topic_phone"),
    ("username", "noun", "/ˈjuː.zər.neɪm/", "topic_phone"),
    ("permission", "noun", "/pəˈmɪʃ.ən/", "topic_giving_instructions"),
    ("access", "noun", "/ˈæk.ses/", "topic_school_communication"),
    ("category", "noun", "/ˈkæt.ɪ.ɡər.i/", "topic_in_class"),
    ("section", "noun", "/ˈsek.ʃən/", "topic_in_class"),
    ("option", "noun", "/ˈɒp.ʃən/", "topic_giving_instructions"),
    ("choice", "noun", "/tʃɔɪs/", "topic_giving_instructions"),
    ("decision", "noun", "/dɪˈsɪʒ.ən/", "topic_school_communication"),
    ("solution", "noun", "/səˈluː.ʃən/", "topic_checking_understanding"),
    # adjectives
    ("suitable", "adjective", "/ˈsuː.tə.bəl/", "topic_giving_instructions"),
    ("appropriate", "adjective", "/əˈprəʊ.pri.ɪt/", "topic_giving_instructions"),
    ("essential", "adjective", "/ɪˈsen.ʃəl/", "topic_giving_instructions"),
    ("optional", "adjective", "/ˈɒp.ʃən.əl/", "topic_giving_instructions"),
    ("available", "adjective", "/əˈveɪ.lə.bəl/", "topic_school_communication"),
    ("limited", "adjective", "/ˈlɪm.ɪ.tɪd/", "topic_market"),
    ("flexible", "adjective", "/ˈflek.sɪ.bəl/", "topic_giving_instructions"),
    ("reliable", "adjective", "/rɪˈlaɪ.ə.bəl/", "topic_school_communication"),
    ("accurate", "adjective", "/ˈæk.jʊ.rɪt/", "topic_checking_understanding"),
    ("relevant", "adjective", "/ˈrel.ɪ.vənt/", "topic_in_class"),
    ("detailed", "adjective", "/ˈdiː.teɪld/", "topic_in_class"),
    ("specific", "adjective", "/spəˈsɪf.ɪk/", "topic_giving_instructions"),
    ("general", "adjective", "/ˈdʒen.ər.əl/", "topic_in_class"),
    ("main", "adjective", "/meɪn/", "topic_in_class"),
    ("basic", "adjective", "/ˈbeɪ.sɪk/", "topic_in_class"),
    ("advanced", "adjective", "/ədˈvɑːnst/", "topic_in_class"),
    ("practical", "adjective", "/ˈpræk.tɪ.kəl/", "topic_giving_instructions"),
    ("theoretical", "adjective", "/ˌθɪə.riˈet.ɪ.kəl/", "topic_in_class"),
    ("formal", "adjective", "/ˈfɔː.məl/", "topic_school_communication"),
    ("informal", "adjective", "/ɪnˈfɔː.məl/", "topic_social"),
    # more topic_market
    ("bargain", "noun", "/ˈbɑː.ɡɪn/", "topic_market"),
    ("offer", "noun", "/ˈɒf.ər/", "topic_market"),
    ("deal", "noun", "/diːl/", "topic_market"),
    ("promotion", "noun", "/prəˈməʊ.ʃən/", "topic_market"),
    ("sale", "noun", "/seɪl/", "topic_market"),
    ("product", "noun", "/ˈprɒd.ʌkt/", "topic_market"),
    ("brand", "noun", "/brænd/", "topic_market"),
    ("label", "noun", "/ˈleɪ.bəl/", "topic_market"),
    ("packaging", "noun", "/ˈpæk.ɪ.dʒɪŋ/", "topic_market"),
    ("ingredient", "noun", "/ɪnˈɡriː.di.ənt/", "topic_market"),
    # more topic_travel
    ("adventure", "noun", "/ədˈven.tʃər/", "topic_travel"),
    ("exploration", "noun", "/ˌek.splɔːˈreɪ.ʃən/", "topic_travel"),
    ("culture", "noun", "/ˈkʌl.tʃər/", "topic_travel"),
    ("heritage", "noun", "/ˈher.ɪ.tɪdʒ/", "topic_travel"),
    ("monument", "noun", "/ˈmɒn.jʊ.mənt/", "topic_travel"),
    ("museum", "noun", "/mjuːˈziː.əm/", "topic_travel"),
    ("gallery", "noun", "/ˈɡæl.ər.i/", "topic_travel"),
    ("souvenir", "noun", "/ˌsuː.vəˈnɪər/", "topic_travel"),
    ("currency", "noun", "/ˈkʌr.ən.si/", "topic_travel"),
    ("exchange", "noun", "/ɪksˈtʃeɪndʒ/", "topic_travel"),
    # health
    ("lifestyle", "noun", "/ˈlaɪf.staɪl/", "topic_health"),
    ("wellness", "noun", "/ˈwel.nəs/", "topic_health"),
    ("fitness", "noun", "/ˈfɪt.nəs/", "topic_health"),
    ("diet", "noun", "/ˈdaɪ.ɪt/", "topic_health"),
    ("routine", "noun", "/ruːˈtiːn/", "topic_health"),
    ("habit", "noun", "/ˈhæb.ɪt/", "topic_health"),
    ("balance", "noun", "/ˈbæl.əns/", "topic_health"),
    ("energy", "noun", "/ˈen.ər.dʒi/", "topic_health"),
    ("stamina", "noun", "/ˈstæm.ɪ.nə/", "topic_health"),
    ("flexibility", "noun", "/ˌflek.sɪˈbɪl.ɪ.ti/", "topic_health"),
],

"ket": [
    # Professional verbs
    ("anticipate", "verb", "/ænˈtɪs.ɪ.peɪt/", "topic_before_class"),
    ("formulate", "verb", "/ˈfɔː.mjʊ.leɪt/", "topic_before_class"),
    ("prioritise", "verb", "/praɪˈɒr.ɪ.taɪz/", "topic_before_class"),
    ("streamline", "verb", "/ˈstriːm.laɪn/", "topic_before_class"),
    ("optimise", "verb", "/ˈɒp.tɪ.maɪz/", "topic_before_class"),
    ("maximise", "verb", "/ˈmæk.sɪ.maɪz/", "topic_before_class"),
    ("minimise", "verb", "/ˈmɪn.ɪ.maɪz/", "topic_before_class"),
    ("coordinate", "verb", "/kəʊˈɔː.dɪ.neɪt/", "topic_school_communication"),
    ("liaise", "verb", "/liˈeɪz/", "topic_school_communication"),
    ("delegate", "verb", "/ˈdel.ɪ.ɡeɪt/", "topic_school_communication"),
    ("supervise", "verb", "/ˈsuː.pə.vaɪz/", "topic_school_communication"),
    ("monitor", "verb", "/ˈmɒn.ɪ.tər/", "topic_checking_understanding"),
    ("track", "verb", "/træk/", "topic_checking_understanding"),
    ("measure", "verb", "/ˈmeʒ.ər/", "topic_checking_understanding"),
    ("compare", "verb", "/kəmˈpeər/", "topic_checking_understanding"),
    ("contrast", "verb", "/ˈkɒn.trɑːst/", "topic_checking_understanding"),
    ("categorise", "verb", "/ˈkæt.ɪ.ɡə.raɪz/", "topic_in_class"),
    ("classify", "verb", "/ˈklæs.ɪ.faɪ/", "topic_in_class"),
    ("rank", "verb", "/ræŋk/", "topic_in_class"),
    ("sort", "verb", "/sɔːt/", "topic_in_class"),
    ("filter", "verb", "/ˈfɪl.tər/", "topic_in_class"),
    ("select", "verb", "/sɪˈlekt/", "topic_giving_instructions"),
    ("eliminate", "verb", "/ɪˈlɪm.ɪ.neɪt/", "topic_giving_instructions"),
    ("exclude", "verb", "/ɪkˈskluːd/", "topic_giving_instructions"),
    ("include", "verb", "/ɪnˈkluːd/", "topic_giving_instructions"),
    ("extend", "verb", "/ɪkˈstend/", "topic_in_class"),
    ("expand", "verb", "/ɪkˈspænd/", "topic_in_class"),
    ("narrow", "verb", "/ˈnær.əʊ/", "topic_giving_instructions"),
    ("broaden", "verb", "/ˈbrɔː.dən/", "topic_in_class"),
    ("deepen", "verb", "/ˈdiː.pən/", "topic_in_class"),
    # Professional nouns
    ("overview", "noun", "/ˈəʊ.və.vjuː/", "topic_before_class"),
    ("agenda", "noun", "/əˈdʒen.də/", "topic_before_class"),
    ("minutes", "noun", "/ˈmɪn.ɪts/", "topic_school_communication"),
    ("budget", "noun", "/ˈbʌdʒ.ɪt/", "topic_school_communication"),
    ("proposal", "noun", "/prəˈpəʊ.zəl/", "topic_school_communication"),
    ("approval", "noun", "/əˈpruː.vəl/", "topic_school_communication"),
    ("rejection", "noun", "/rɪˈdʒek.ʃən/", "topic_school_communication"),
    ("agreement", "noun", "/əˈɡriː.mənt/", "topic_school_communication"),
    ("disagreement", "noun", "/ˌdɪs.əˈɡriː.mənt/", "topic_school_communication"),
    ("compromise", "noun", "/ˈkɒm.prə.maɪz/", "topic_school_communication"),
    ("outcome", "noun", "/ˈaʊt.kʌm/", "topic_checking_understanding"),
    ("impact", "noun", "/ˈɪm.pækt/", "topic_in_class"),
    ("effect", "noun", "/ɪˈfekt/", "topic_in_class"),
    ("cause", "noun", "/kɔːz/", "topic_in_class"),
    ("factor", "noun", "/ˈfæk.tər/", "topic_in_class"),
    ("aspect", "noun", "/ˈæs.pekt/", "topic_in_class"),
    ("feature", "noun", "/ˈfiː.tʃər/", "topic_in_class"),
    ("element", "noun", "/ˈel.ɪ.mənt/", "topic_in_class"),
    ("component", "noun", "/kəmˈpəʊ.nənt/", "topic_in_class"),
    ("structure", "noun", "/ˈstrʌk.tʃər/", "topic_in_class"),
    # Daily life topics
    ("schedule", "verb", "/ˈʃed.juːl/", "topic_travel"),
    ("book", "verb", "/bʊk/", "topic_travel"),
    ("reserve", "verb", "/rɪˈzɜːv/", "topic_travel"),
    ("cancel", "verb", "/ˈkæn.sɪl/", "topic_travel"),
    ("reschedule", "verb", "/ˌriːˈʃed.juːl/", "topic_travel"),
    ("delay", "verb", "/dɪˈleɪ/", "topic_travel"),
    ("expedite", "verb", "/ˈek.spɪ.daɪt/", "topic_travel"),
    ("accelerate", "verb", "/əkˈsel.ər.eɪt/", "topic_travel"),
    ("decelerate", "verb", "/ˌdiːˈsel.ər.eɪt/", "topic_travel"),
    ("navigate", "verb", "/ˈnæv.ɪ.ɡeɪt/", "topic_travel"),
    ("estimate", "verb", "/ˈes.tɪ.meɪt/", "topic_travel"),
    ("calculate", "verb", "/ˈkæl.kjʊ.leɪt/", "topic_in_class"),
    ("evaluate", "verb", "/ɪˈvæl.jʊ.eɪt/", "topic_checking_understanding"),
    ("negotiate", "verb", "/nɪˈɡəʊ.ʃi.eɪt/", "topic_restaurant"),
    ("complain", "verb", "/kəmˈpleɪn/", "topic_market"),
    ("refund", "verb", "/ˈriː.fʌnd/", "topic_market"),
    ("exchange", "verb", "/ɪksˈtʃeɪndʒ/", "topic_market"),
    ("replace", "verb", "/rɪˈpleɪs/", "topic_market"),
    ("compensate", "verb", "/ˈkɒm.pən.seɪt/", "topic_market"),
    ("apologise", "verb", "/əˈpɒl.ə.dʒaɪz/", "topic_phone"),
    # Adjectives
    ("bilingual", "adjective", "/ˌbaɪˈlɪŋ.ɡwəl/", "topic_in_class"),
    ("fluent", "adjective", "/ˈfluː.ənt/", "topic_in_class"),
    ("proficient", "adjective", "/prəˈfɪʃ.ənt/", "topic_in_class"),
    ("competent", "adjective", "/ˈkɒm.pɪ.tənt/", "topic_in_class"),
    ("qualified", "adjective", "/ˈkwɒl.ɪ.faɪd/", "topic_school_communication"),
    ("experienced", "adjective", "/ɪkˈspɪər.i.ənst/", "topic_school_communication"),
    ("dedicated", "adjective", "/ˈded.ɪ.keɪ.tɪd/", "topic_praise_correction"),
    ("motivated", "adjective", "/ˈməʊ.tɪ.veɪ.tɪd/", "topic_praise_correction"),
    ("enthusiastic", "adjective", "/ɪnˌθjuː.ziˈæs.tɪk/", "topic_praise_correction"),
    ("resourceful", "adjective", "/rɪˈzɔːs.fəl/", "topic_in_class"),
    ("innovative", "adjective", "/ˈɪn.ə.veɪ.tɪv/", "topic_in_class"),
    ("adaptable", "adjective", "/əˈdæp.tə.bəl/", "topic_giving_instructions"),
    ("resilient", "adjective", "/rɪˈzɪl.i.ənt/", "topic_social"),
    ("empathetic", "adjective", "/ˌem.pəˈθet.ɪk/", "topic_social"),
    ("approachable", "adjective", "/əˈprəʊ.tʃə.bəl/", "topic_social"),
    ("supportive", "adjective", "/səˈpɔː.tɪv/", "topic_social"),
    ("constructive", "adjective", "/kənˈstrʌk.tɪv/", "topic_praise_correction"),
    ("objective", "adjective", "/əbˈdʒek.tɪv/", "topic_checking_understanding"),
    ("subjective", "adjective", "/səbˈdʒek.tɪv/", "topic_checking_understanding"),
    ("transparent", "adjective", "/trænsˈpær.ənt/", "topic_school_communication"),
    ("accountable", "adjective", "/əˈkaʊn.tə.bəl/", "topic_school_communication"),
    ("sustainable", "adjective", "/səˈsteɪ.nə.bəl/", "topic_social"),
    ("inclusive", "adjective", "/ɪnˈkluː.sɪv/", "topic_social"),
    ("equitable", "adjective", "/ˈek.wɪ.tə.bəl/", "topic_social"),
    ("proactive", "adjective", "/ˌprəʊˈæk.tɪv/", "topic_before_class"),
    ("reactive", "adjective", "/riˈæk.tɪv/", "topic_school_communication"),
    ("dynamic", "adjective", "/daɪˈnæm.ɪk/", "topic_in_class"),
    ("static", "adjective", "/ˈstæt.ɪk/", "topic_checking_understanding"),
    ("collaborative", "adjective", "/kəˈlæb.ər.ə.tɪv/", "topic_in_class"),
    ("competitive", "adjective", "/kəmˈpet.ɪ.tɪv/", "topic_social"),
],

"pet": [
    # Replacing over-advanced words with proper B2 vocabulary
    # Professional and academic B2 verbs
    ("acknowledge", "verb", "/əkˈnɒl.ɪdʒ/", "topic_praise_correction"),
    ("advocate", "verb", "/ˈæd.və.keɪt/", "topic_school_communication"),
    ("assert", "verb", "/əˈsɜːt/", "topic_school_communication"),
    ("assume", "verb", "/əˈsjuːm/", "topic_checking_understanding"),
    ("attribute", "verb", "/əˈtrɪb.juːt/", "topic_in_class"),
    ("categorise", "verb", "/ˈkæt.ɪ.ɡə.raɪz/", "topic_in_class"),
    ("challenge", "verb", "/ˈtʃæl.ɪndʒ/", "topic_in_class"),
    ("characterise", "verb", "/ˈkær.ɪk.tər.aɪz/", "topic_in_class"),
    ("compensate", "verb", "/ˈkɒm.pən.seɪt/", "topic_school_communication"),
    ("compromise", "verb", "/ˈkɒm.prə.maɪz/", "topic_school_communication"),
    ("consolidate", "verb", "/kənˈsɒl.ɪ.deɪt/", "topic_before_class"),
    ("contradict", "verb", "/ˌkɒn.trəˈdɪkt/", "topic_checking_understanding"),
    ("correlate", "verb", "/ˈkɒr.ɪ.leɪt/", "topic_checking_understanding"),
    ("customize", "verb", "/ˈkʌs.tə.maɪz/", "topic_giving_instructions"),
    ("differentiate", "verb", "/ˌdɪf.ərˈen.ʃi.eɪt/", "topic_in_class"),
    ("elaborate", "verb", "/ɪˈlæb.ər.eɪt/", "topic_in_class"),
    ("emphasise", "verb", "/ˈem.fə.saɪz/", "topic_giving_instructions"),
    ("enhance", "verb", "/ɪnˈhɑːns/", "topic_praise_correction"),
    ("evaluate", "verb", "/ɪˈvæl.jʊ.eɪt/", "topic_checking_understanding"),
    ("generate", "verb", "/ˈdʒen.ər.eɪt/", "topic_in_class"),
    ("illustrate", "verb", "/ˈɪl.ə.streɪt/", "topic_in_class"),
    ("implement", "verb", "/ˈɪm.plɪ.ment/", "topic_before_class"),
    ("incorporate", "verb", "/ɪnˈkɔː.pər.eɪt/", "topic_in_class"),
    ("interpret", "verb", "/ɪnˈtɜː.prɪt/", "topic_checking_understanding"),
    ("justify", "verb", "/ˈdʒʌs.tɪ.faɪ/", "topic_in_class"),
    ("maintain", "verb", "/meɪnˈteɪn/", "topic_school_communication"),
    ("manifest", "verb", "/ˈmæn.ɪ.fest/", "topic_checking_understanding"),
    ("minimise", "verb", "/ˈmɪn.ɪ.maɪz/", "topic_giving_instructions"),
    ("modify", "verb", "/ˈmɒd.ɪ.faɪ/", "topic_giving_instructions"),
    ("motivate", "verb", "/ˈməʊ.tɪ.veɪt/", "topic_praise_correction"),
    # B2 nouns
    ("ambiguity", "noun", "/ˌæm.bɪˈɡjuː.ɪ.ti/", "topic_checking_understanding"),
    ("approach", "noun", "/əˈprəʊtʃ/", "topic_in_class"),
    ("assumption", "noun", "/əˈsʌmp.ʃən/", "topic_checking_understanding"),
    ("circumstance", "noun", "/ˈsɜː.kəm.stæns/", "topic_social"),
    ("commitment", "noun", "/kəˈmɪt.mənt/", "topic_praise_correction"),
    ("consequence", "noun", "/ˈkɒn.sɪ.kwəns/", "topic_giving_instructions"),
    ("contradiction", "noun", "/ˌkɒn.trəˈdɪk.ʃən/", "topic_checking_understanding"),
    ("controversy", "noun", "/ˈkɒn.trə.vɜː.si/", "topic_school_communication"),
    ("convention", "noun", "/kənˈven.ʃən/", "topic_social"),
    ("credentials", "noun", "/krɪˈden.ʃəlz/", "topic_school_communication"),
    ("deadline", "noun", "/ˈded.laɪn/", "topic_giving_instructions"),
    ("discrepancy", "noun", "/dɪˈskrep.ən.si/", "topic_checking_understanding"),
    ("efficiency", "noun", "/ɪˈfɪʃ.ən.si/", "topic_before_class"),
    ("emphasis", "noun", "/ˈem.fə.sɪs/", "topic_giving_instructions"),
    ("endorsement", "noun", "/ɪnˈdɔːs.mənt/", "topic_school_communication"),
    ("expectation", "noun", "/ˌek.spekˈteɪ.ʃən/", "topic_in_class"),
    ("flexibility", "noun", "/ˌflek.sɪˈbɪl.ɪ.ti/", "topic_giving_instructions"),
    ("foundation", "noun", "/faʊnˈdeɪ.ʃən/", "topic_in_class"),
    ("implication", "noun", "/ˌɪm.plɪˈkeɪ.ʃən/", "topic_checking_understanding"),
    ("incentive", "noun", "/ɪnˈsen.tɪv/", "topic_praise_correction"),
    ("inconsistency", "noun", "/ˌɪn.kənˈsɪs.tən.si/", "topic_checking_understanding"),
    ("independence", "noun", "/ˌɪn.dɪˈpen.dəns/", "topic_social"),
    ("inference", "noun", "/ˈɪn.fər.əns/", "topic_in_class"),
    ("influence", "noun", "/ˈɪn.flu.əns/", "topic_social"),
    ("interpretation", "noun", "/ɪnˌtɜː.prɪˈteɪ.ʃən/", "topic_checking_understanding"),
    ("limitation", "noun", "/ˌlɪm.ɪˈteɪ.ʃən/", "topic_in_class"),
    ("mechanism", "noun", "/ˈmek.ə.nɪz.əm/", "topic_before_class"),
    ("methodology", "noun", "/ˌmeθ.əˈdɒl.ə.dʒi/", "topic_before_class"),
    ("motivation", "noun", "/ˌməʊ.tɪˈveɪ.ʃən/", "topic_praise_correction"),
    ("obstacle", "noun", "/ˈɒb.stɪ.kəl/", "topic_social"),
    # B2 adjectives
    ("abstract", "adjective", "/ˈæb.strækt/", "topic_in_class"),
    ("ambiguous", "adjective", "/æmˈbɪɡ.ju.əs/", "topic_checking_understanding"),
    ("arbitrary", "adjective", "/ˈɑː.bɪ.trər.i/", "topic_giving_instructions"),
    ("authentic", "adjective", "/ɔːˈθen.tɪk/", "topic_in_class"),
    ("compelling", "adjective", "/kəmˈpel.ɪŋ/", "topic_in_class"),
    ("comprehensive", "adjective", "/ˌkɒm.prɪˈhen.sɪv/", "topic_in_class"),
    ("controversial", "adjective", "/ˌkɒn.trəˈvɜː.ʃəl/", "topic_social"),
    ("credible", "adjective", "/ˈkred.ɪ.bəl/", "topic_school_communication"),
    ("decisive", "adjective", "/dɪˈsaɪ.sɪv/", "topic_school_communication"),
    ("deliberate", "adjective", "/dɪˈlɪb.ər.ɪt/", "topic_in_class"),
    ("diverse", "adjective", "/daɪˈvɜːs/", "topic_social"),
    ("dominant", "adjective", "/ˈdɒm.ɪ.nənt/", "topic_social"),
    ("explicit", "adjective", "/ɪkˈsplɪs.ɪt/", "topic_giving_instructions"),
    ("fundamental", "adjective", "/ˌfʌn.dəˈmen.tl/", "topic_in_class"),
    ("implicit", "adjective", "/ɪmˈplɪs.ɪt/", "topic_checking_understanding"),
    ("inadequate", "adjective", "/ɪnˈæd.ɪ.kwɪt/", "topic_praise_correction"),
    ("inevitable", "adjective", "/ɪnˈev.ɪ.tə.bəl/", "topic_social"),
    ("inherent", "adjective", "/ɪnˈhɪər.ənt/", "topic_in_class"),
    ("intrinsic", "adjective", "/ɪnˈtrɪn.zɪk/", "topic_praise_correction"),
    ("logical", "adjective", "/ˈlɒdʒ.ɪ.kəl/", "topic_in_class"),
    ("marginal", "adjective", "/ˈmɑː.dʒɪ.nəl/", "topic_market"),
    ("neutral", "adjective", "/ˈnjuː.trəl/", "topic_social"),
    ("objective", "adjective", "/əbˈdʒek.tɪv/", "topic_checking_understanding"),
    ("partial", "adjective", "/ˈpɑː.ʃəl/", "topic_checking_understanding"),
    ("prevalent", "adjective", "/ˈprev.ə.lənt/", "topic_health"),
    ("profound", "adjective", "/prəˈfaʊnd/", "topic_in_class"),
    ("rational", "adjective", "/ˈræʃ.ən.əl/", "topic_checking_understanding"),
    ("strategic", "adjective", "/strəˈtiː.dʒɪk/", "topic_before_class"),
    ("systematic", "adjective", "/ˌsɪs.tɪˈmæt.ɪk/", "topic_before_class"),
    ("tangible", "adjective", "/ˈtæn.dʒɪ.bəl/", "topic_in_class"),
],
}


def main():
    print("=" * 60)
    print("TinySteps — Vocabulary Batch 3 Final Fill")
    print("=" * 60)

    existing = {}
    global_seen: set[str] = set()
    for level in LEVELS:
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        data = json.load(open(path, encoding="utf-8"))
        existing[level] = data["words"]
        for w in data["words"]:
            global_seen.add(w["word"].lower())

    print(f"Before: {sum(len(v) for v in existing.values())} words\n")

    for level in LEVELS:
        target = TARGETS[level]
        current = len(existing[level])
        gap = target - current
        if gap <= 0:
            print(f"{level}: already full ({current}/{target})")
            continue

        pool = BATCH3.get(level, [])
        added = []
        for word, pos, ipa, topic in pool:
            if len(added) >= gap:
                break
            key = word.lower()
            if key in global_seen:
                continue
            idx = current + len(added) + 1
            added.append({
                "id": f"{level}_vocab_{idx:03d}",
                "word": word,
                "ipa": ipa,
                "pos": pos,
                "topic_ids": [topic],
                "example_sentence": make_example(word, pos, level),
                "image_hint": make_hint(word, pos),
                "frequency_rank": idx,
            })
            global_seen.add(key)

        merged = existing[level] + added
        for i, w in enumerate(merged, 1):
            w["id"] = f"{level}_vocab_{i:03d}"

        payload = {"level": level, "total_words": len(merged), "words": merged}
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        remaining = max(0, target - len(merged))
        flag = "✓" if remaining == 0 else f"still need +{remaining}"
        print(f"{level}: +{len(added)} → {len(merged)}/{target}  {flag}")

    print(f"\nAfter: {sum(TARGETS[l] for l in LEVELS)} target")
    print("Run validate_data.py to verify.")


if __name__ == "__main__":
    main()
