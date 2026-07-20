#!/usr/bin/env python3
"""
Thay 72 mục từ vựng KET/PET vượt xa trình độ A2/B1: một cụm danh từ trừu tượng hiếm gặp
ở KET (multifacetedness, perspicuousness, sagaciousness...) và một cụm thuật ngữ triết
học/lý thuyết hàn lâm ở PET (hermeneutics, axiology, poststructuralism, deontology,
utilitarianism, teleology...) cộng một cụm chuyên khoa y tế (endocrinology, oncology,
psychiatry...) và kinh tế học hàn lâm (macroeconomics, oligopoly...).

Vì sao chắc đây là lỗi, không phải chủ ý: mọi mục trong hai cụm chính đều dùng chung
đúng ba khuôn câu template ("I'd like to discuss the X.", "The X should be confirmed.",
"If I had a better X, I would use it.") — dấu hiệu rõ của bộ sinh mất kiểm soát khi cố
tạo "từ vựng chuyên nghiệp nâng cao" và trôi sang thuật ngữ hàn lâm C2/sau đại học, hoàn
toàn lệch với KET (A2) và PET (B1) mà chúng được gắn nhãn.

Đã xác minh trước khi sửa: không mục nào trong 72 mục này được dùng làm đáp án hay lựa
chọn trong bất kỳ bài tập match/multiple_choice/listen_choose nào (0/875 bài tập) — chỉ
xuất hiện trong trường vocabulary_ids (siêu dữ liệu) của 22 bài học. Vì id giữ nguyên,
KHÔNG cần sửa file bài học nào trong đợt này.

Từ thay thế: chọn theo đúng topic_ids cũ (giữ nguyên phân bố chủ đề), là từ thật thông
dụng ở trình độ A2 (KET) / B1 (PET), và được kiểm tra không trùng với 2100 từ hiện có
trên toàn bộ 5 cấp độ (kể cả 72 từ bị thay — chọn hẳn từ mới, không tái dùng).

Chạy: python3 tinysteps-data/fix_ket_pet_academic_jargon.py [--apply]
"""

import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(DATA_DIR, "vocabulary")

# ═══════════════════════════════════════════════════════════════════════════
# KET (A2) — 25 mục, thay cụm danh từ/tính từ trừu tượng hiếm gặp
# ═══════════════════════════════════════════════════════════════════════════

KET_FIXES = {
    # topic_in_class
    "ket_vocab_396": {  # acumen
        "word": "register", "ipa": "/ˈredʒ.ɪ.stər/", "pos": "noun",
        "example_sentence": "The teacher checks the register.",
        "image_hint": "a teacher marking names on a class list",
    },
    "ket_vocab_097": {  # constructivist
        "word": "blackboard", "ipa": "/ˈblæk.bɔːd/", "pos": "noun",
        "example_sentence": "Write the date on the blackboard.",
        "image_hint": "a blackboard with a piece of chalk beside it",
    },
    "ket_vocab_394": {  # incisiveness
        "word": "punishment", "ipa": "/ˈpʌn.ɪʃ.mənt/", "pos": "noun",
        "example_sentence": "The punishment should be fair.",
        "image_hint": "a child sitting alone at a separate desk",
    },
    "ket_vocab_382": {  # multidimensionality
        "word": "memorize", "ipa": "/ˈmem.ər.aɪz/", "pos": "verb",
        "example_sentence": "Please memorize this poem.",
        "image_hint": "a pupil with eyes closed reciting from memory",
    },
    "ket_vocab_383": {  # multifacetedness
        "word": "recite", "ipa": "/rɪˈsaɪt/", "pos": "verb",
        "example_sentence": "Can you recite the poem?",
        "image_hint": "a pupil standing and speaking in front of the class",
    },
    "ket_vocab_384": {  # multilayeredness
        "word": "playground", "ipa": "/ˈpleɪ.ɡraʊnd/", "pos": "noun",
        "example_sentence": "The children play in the playground.",
        "image_hint": "a school playground with a slide and swings",
    },
    "ket_vocab_398": {  # perspicuousness
        "word": "locker", "ipa": "/ˈlɒk.ər/", "pos": "noun",
        "example_sentence": "Put your bag in the locker.",
        "image_hint": "a row of small school lockers",
    },

    # topic_checking_understanding
    "ket_vocab_391": {  # acuteness
        "word": "recap", "ipa": "/ˈriː.kæp/", "pos": "verb",
        "example_sentence": "Let's recap what we learned.",
        "image_hint": "a teacher pointing back at earlier notes on the board",
    },
    "ket_vocab_389": {  # exactitude
        "word": "unclear", "ipa": "/ʌnˈklɪər/", "pos": "adjective",
        "example_sentence": "This instruction is unclear.",
        "image_hint": "a pupil scratching their head at a confusing worksheet",
    },
    "ket_vocab_390": {  # preciseness
        "word": "misunderstand", "ipa": "/ˌmɪs.ʌn.dəˈstænd/", "pos": "verb",
        "example_sentence": "Please don't misunderstand me.",
        "image_hint": "two people with confused expressions facing each other",
    },
    "ket_vocab_124": {  # triangulation
        "word": "clarity", "ipa": "/ˈklær.ə.ti/", "pos": "noun",
        "example_sentence": "I'd like more clarity, please.",
        "image_hint": "a clear glass of water beside a cloudy one",
    },

    # topic_social
    "ket_vocab_397": {  # astuteness
        "word": "stranger", "ipa": "/ˈstreɪn.dʒər/", "pos": "noun",
        "example_sentence": "Don't talk to a stranger.",
        "image_hint": "an unfamiliar person standing at a distance",
    },
    "ket_vocab_381": {  # interrelatedness
        "word": "apology", "ipa": "/əˈpɒl.ə.dʒi/", "pos": "noun",
        "example_sentence": "She gave a sincere apology.",
        "image_hint": "one person offering a hand to another with a sorry expression",
    },
    "ket_vocab_399": {  # judiciousness
        "word": "compliment", "ipa": "/ˈkɒm.plɪ.mənt/", "pos": "noun",
        "example_sentence": "Thank you for the compliment.",
        "image_hint": "a person smiling after hearing kind words",
    },
    "ket_vocab_379": {  # interconnectedness
        "word": "gratitude", "ipa": "/ˈɡræt.ɪ.tʃuːd/", "pos": "noun",
        "example_sentence": "I want to show my gratitude.",
        "image_hint": "a hand offering a small thank-you card",
    },
    "ket_vocab_395": {  # perspicacity
        "word": "kindness", "ipa": "/ˈkaɪnd.nəs/", "pos": "noun",
        "example_sentence": "Thank you for your kindness.",
        "image_hint": "one person helping another carry a heavy bag",
    },
    "ket_vocab_400": {  # sagaciousness
        "word": "manners", "ipa": "/ˈmæn.əz/", "pos": "noun",
        "example_sentence": "Please remember your manners.",
        "image_hint": "a child politely waiting in a queue",
    },

    # topic_praise_correction
    "ket_vocab_336": {  # conscientiousness
        "word": "hardworking", "ipa": "/ˌhɑːdˈwɜː.kɪŋ/", "pos": "adjective",
        "example_sentence": "You are a hardworking student.",
        "image_hint": "a pupil focused and writing steadily at a desk",
    },
    "ket_vocab_392": {  # keenness
        "word": "messy", "ipa": "/ˈmes.i/", "pos": "adjective",
        "example_sentence": "Your desk looks messy today.",
        "image_hint": "a desk cluttered with scattered papers and pens",
    },
    "ket_vocab_388": {  # punctiliousness
        "word": "attentive", "ipa": "/əˈten.tɪv/", "pos": "adjective",
        "example_sentence": "Please be attentive in class.",
        "image_hint": "a pupil sitting upright and looking closely at the teacher",
    },
    "ket_vocab_387": {  # scrupulousness
        "word": "distracted", "ipa": "/dɪˈstræk.tɪd/", "pos": "adjective",
        "example_sentence": "He looks distracted today.",
        "image_hint": "a pupil staring out of the window instead of the board",
    },

    # topic_health
    "ket_vocab_173": {  # cardiovascular
        "word": "checkup", "ipa": "/ˈtʃek.ʌp/", "pos": "noun",
        "example_sentence": "I have a checkup tomorrow.",
        "image_hint": "a doctor listening to a patient's chest with a stethoscope",
    },
    "ket_vocab_175": {  # neurological
        "word": "bruise", "ipa": "/bruːz/", "pos": "noun",
        "example_sentence": "I have a bruise on my arm.",
        "image_hint": "a small dark bruise mark on a forearm",
    },
    "ket_vocab_174": {  # respiratory
        "word": "sore throat", "ipa": "/sɔːr θrəʊt/", "pos": "noun",
        "example_sentence": "I have a sore throat today.",
        "image_hint": "a person holding their throat with a pained expression",
    },

    # topic_before_class
    "ket_vocab_085": {  # pedagogical
        "word": "punctual", "ipa": "/ˈpʌŋk.tʃu.əl/", "pos": "adjective",
        "example_sentence": "Please be punctual for class.",
        "image_hint": "a clock showing the exact start time beside an open door",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# PET (B1) — 47 mục, thay cụm thuật ngữ triết học / chuyên khoa y tế / kinh tế
# ═══════════════════════════════════════════════════════════════════════════

PET_FIXES = {
    # topic_health
    "pet_vocab_287": {  # aetiology
        "word": "receptionist", "ipa": "/rɪˈsep.ʃən.ɪst/", "pos": "noun",
        "example_sentence": "The receptionist booked my appointment.",
        "image_hint": "a person behind a clinic front desk answering the phone",
    },
    "pet_vocab_295": {  # dermatology
        "word": "infection", "ipa": "/ɪnˈfek.ʃən/", "pos": "noun",
        "example_sentence": "The wound has a mild infection.",
        "image_hint": "a bandaged finger with a small red mark",
    },
    "pet_vocab_293": {  # endocrinology
        "word": "ambulance", "ipa": "/ˈæm.bjə.ləns/", "pos": "noun",
        "example_sentence": "The ambulance arrived very quickly.",
        "image_hint": "an ambulance van with its lights on",
    },
    "pet_vocab_294": {  # gastroenterology
        "word": "insurance", "ipa": "/ɪnˈʃɔː.rəns/", "pos": "noun",
        "example_sentence": "Does your insurance cover this visit?",
        "image_hint": "a hand holding an insurance card at a clinic desk",
    },
    "pet_vocab_291": {  # haematology
        "word": "appetite", "ipa": "/ˈæp.ɪ.taɪt/", "pos": "noun",
        "example_sentence": "I have lost my appetite today.",
        "image_hint": "a full plate of food left untouched",
    },
    "pet_vocab_292": {  # immunology
        "word": "fatigue", "ipa": "/fəˈtiːɡ/", "pos": "noun",
        "example_sentence": "I feel a lot of fatigue lately.",
        "image_hint": "a tired person resting their head on a desk",
    },
    "pet_vocab_290": {  # oncology
        "word": "recovery", "ipa": "/rɪˈkʌv.ər.i/", "pos": "noun",
        "example_sentence": "Her recovery is going well.",
        "image_hint": "a patient smiling while resting in a hospital bed",
    },
    "pet_vocab_289": {  # pharmacology
        "word": "therapy", "ipa": "/ˈθer.ə.pi/", "pos": "noun",
        "example_sentence": "He goes to therapy every week.",
        "image_hint": "a therapist and patient talking in a calm room",
    },
    "pet_vocab_296": {  # psychiatry
        "word": "diagnose", "ipa": "/ˈdaɪ.əɡ.nəʊz/", "pos": "verb",
        "example_sentence": "The doctor could not diagnose the problem yet.",
        "image_hint": "a doctor examining an x-ray on a lightboard",
    },

    # topic_social
    "pet_vocab_481": {  # axiology
        "word": "acquaintance", "ipa": "/əˈkweɪn.təns/", "pos": "noun",
        "example_sentence": "He is a colleague, not a close acquaintance.",
        "image_hint": "two people shaking hands at a first meeting",
    },
    "pet_vocab_483": {  # consequentialism
        "word": "generosity", "ipa": "/ˌdʒen.əˈrɒs.ə.ti/", "pos": "noun",
        "example_sentence": "Thank you for your generosity.",
        "image_hint": "a hand giving a wrapped gift to another person",
    },
    "pet_vocab_302": {  # deconstructionist
        "word": "hospitable", "ipa": "/hɒˈspɪt.ə.bəl/", "pos": "adjective",
        "example_sentence": "Our host family was very hospitable.",
        "image_hint": "a host welcoming a guest with open arms at a doorway",
    },
    "pet_vocab_482": {  # deontology
        "word": "sympathy", "ipa": "/ˈsɪm.pə.θi/", "pos": "noun",
        "example_sentence": "She showed real sympathy for him.",
        "image_hint": "a hand resting gently on a friend's shoulder",
    },
    "pet_vocab_499": {  # essentialism
        "word": "rumour", "ipa": "/ˈruː.mər/", "pos": "noun",
        "example_sentence": "Don't believe every rumour you hear.",
        "image_hint": "two people whispering behind cupped hands",
    },
    "pet_vocab_304": {  # hegemony
        "word": "farewell", "ipa": "/feəˈwel/", "pos": "noun",
        "example_sentence": "We said our farewell at the station.",
        "image_hint": "friends waving goodbye at a train platform",
    },
    "pet_vocab_492": {  # humanism
        "word": "companionship", "ipa": "/kəmˈpæn.jən.ʃɪp/", "pos": "noun",
        "example_sentence": "I value our long companionship.",
        "image_hint": "two elderly friends walking together and talking",
    },
    "pet_vocab_496": {  # idealism
        "word": "loyalty", "ipa": "/ˈlɔɪ.əl.ti/", "pos": "noun",
        "example_sentence": "She has shown great loyalty to us.",
        "image_hint": "a dog sitting faithfully beside its owner",
    },
    "pet_vocab_497": {  # materialism
        "word": "honesty", "ipa": "/ˈɒn.ɪ.sti/", "pos": "noun",
        "example_sentence": "I always appreciate your honesty.",
        "image_hint": "two people looking each other in the eye while talking",
    },
    "pet_vocab_297": {  # phenomenological
        "word": "cordial", "ipa": "/ˈkɔː.di.əl/", "pos": "adjective",
        "example_sentence": "The meeting had a cordial atmosphere.",
        "image_hint": "two colleagues smiling and shaking hands warmly",
    },
    "pet_vocab_300": {  # philosophical
        "word": "easygoing", "ipa": "/ˌiː.ziˈɡəʊ.ɪŋ/", "pos": "adjective",
        "example_sentence": "Our new colleague is very easygoing.",
        "image_hint": "a relaxed person leaning back with a calm smile",
    },
    "pet_vocab_488": {  # postmodernism
        "word": "modesty", "ipa": "/ˈmɒd.ə.sti/", "pos": "noun",
        "example_sentence": "He accepted the prize with modesty.",
        "image_hint": "a person quietly declining extra applause with a smile",
    },
    "pet_vocab_301": {  # postmodernist
        "word": "trustworthy", "ipa": "/ˈtrʌst.wɜː.ði/", "pos": "adjective",
        "example_sentence": "He is a trustworthy colleague.",
        "image_hint": "a person confidently handing keys to a trusted friend",
    },
    "pet_vocab_484": {  # utilitarianism
        "word": "forgiving", "ipa": "/fəˈɡɪv.ɪŋ/", "pos": "adjective",
        "example_sentence": "She was forgiving about the mistake.",
        "image_hint": "two people smiling and shaking hands after a small argument",
    },

    # topic_in_class
    "pet_vocab_491": {  # behaviourism
        "word": "projector", "ipa": "/prəˈdʒek.tər/", "pos": "noun",
        "example_sentence": "The projector shows the slides clearly.",
        "image_hint": "a classroom projector displaying a bright screen",
    },
    "pet_vocab_490": {  # cognitivism
        "word": "workbook", "ipa": "/ˈwɜːk.bʊk/", "pos": "noun",
        "example_sentence": "Open your workbook to page five.",
        "image_hint": "an open exercise workbook with pencil marks",
    },
    "pet_vocab_424": {  # deconstruction
        "word": "brainstorm", "ipa": "/ˈbreɪn.stɔːm/", "pos": "verb",
        "example_sentence": "Let's brainstorm some ideas together.",
        "image_hint": "a group of pupils around a table with sticky notes",
    },
    "pet_vocab_204": {  # dialectic
        "word": "roleplay", "ipa": "/ˈrəʊl.pleɪ/", "pos": "noun",
        "example_sentence": "We did a roleplay in pairs.",
        "image_hint": "two pupils acting out a short scene together",
    },
    "pet_vocab_494": {  # empiricism
        "word": "pairwork", "ipa": "/ˈpeə.wɜːk/", "pos": "noun",
        "example_sentence": "Let's do some pairwork now.",
        "image_hint": "two pupils sitting together sharing one worksheet",
    },
    "pet_vocab_485": {  # functionalism
        "word": "groupwork", "ipa": "/ˈɡruːp.wɜːk/", "pos": "noun",
        "example_sentence": "This task needs some groupwork.",
        "image_hint": "four pupils sitting together around one table",
    },
    "pet_vocab_500": {  # nominalism
        "word": "handwriting", "ipa": "/ˈhænd.raɪ.tɪŋ/", "pos": "noun",
        "example_sentence": "Your handwriting is very neat.",
        "image_hint": "a notebook page with neat handwritten lines",
    },
    "pet_vocab_487": {  # poststructuralism
        "word": "seating", "ipa": "/ˈsiː.tɪŋ/", "pos": "noun",
        "example_sentence": "We changed the seating this week.",
        "image_hint": "rows of classroom desks arranged neatly",
    },
    "pet_vocab_495": {  # rationalism
        "word": "flashcard", "ipa": "/ˈflæʃ.kɑːd/", "pos": "noun",
        "example_sentence": "The teacher held up a flashcard.",
        "image_hint": "a hand holding up a picture flashcard",
    },
    "pet_vocab_486": {  # structuralism
        "word": "noticeboard", "ipa": "/ˈnəʊ.tɪs.bɔːd/", "pos": "noun",
        "example_sentence": "Check the noticeboard for updates.",
        "image_hint": "a cork noticeboard with several pinned notes",
    },
    "pet_vocab_480": {  # teleology
        "word": "stationery", "ipa": "/ˈsteɪ.ʃən.ər.i/", "pos": "noun",
        "example_sentence": "We need more stationery for class.",
        "image_hint": "a pot of pens, pencils, and a ruler on a desk",
    },

    # topic_checking_understanding
    "pet_vocab_226": {  # deconstruct
        "word": "restate", "ipa": "/ˌriːˈsteɪt/", "pos": "verb",
        "example_sentence": "Could you restate that more simply?",
        "image_hint": "a teacher rephrasing a point with open hands",
    },
    "pet_vocab_222": {  # epistemology
        "word": "confusion", "ipa": "/kənˈfjuː.ʒən/", "pos": "noun",
        "example_sentence": "There was some confusion about the task.",
        "image_hint": "a pupil looking puzzled at a worksheet",
    },
    "pet_vocab_225": {  # hermeneutics
        "word": "misinterpretation", "ipa": "/ˌmɪs.ɪnˌtɜː.prəˈteɪ.ʃən/", "pos": "noun",
        "example_sentence": "That was a simple misinterpretation.",
        "image_hint": "two speech bubbles with mismatched meanings",
    },
    "pet_vocab_223": {  # ontology
        "word": "reassurance", "ipa": "/ˌriː.əˈʃɔː.rəns/", "pos": "noun",
        "example_sentence": "She just needed a little reassurance.",
        "image_hint": "a teacher giving a pupil an encouraging nod",
    },
    "pet_vocab_224": {  # phenomenology
        "word": "query", "ipa": "/ˈkwɪə.ri/", "pos": "noun",
        "example_sentence": "I have a quick query about the homework.",
        "image_hint": "a raised hand with a question mark above it",
    },

    # topic_restaurant
    "pet_vocab_261": {  # epicurean
        "word": "appetizer", "ipa": "/ˈæp.ɪ.taɪ.zər/", "pos": "noun",
        "example_sentence": "We ordered an appetizer to share.",
        "image_hint": "a small shared plate of appetizers on a table",
    },

    # topic_before_class
    "pet_vocab_194": {  # epistemological
        "word": "alarm", "ipa": "/əˈlɑːm/", "pos": "noun",
        "example_sentence": "My alarm went off very early.",
        "image_hint": "an alarm clock on a bedside table",
    },
    "pet_vocab_197": {  # praxis
        "word": "rehearse", "ipa": "/rɪˈhɜːs/", "pos": "verb",
        "example_sentence": "I like to rehearse my lesson plan.",
        "image_hint": "a teacher practising alone in an empty classroom",
    },

    # topic_travel
    "pet_vocab_269": {  # geopolitical
        "word": "layover", "ipa": "/ˈleɪ.əʊ.vər/", "pos": "noun",
        "example_sentence": "We had a short layover in Bangkok.",
        "image_hint": "travellers waiting at an airport departure gate",
    },

    # topic_market
    "pet_vocab_249": {  # macroeconomics
        "word": "retail", "ipa": "/ˈriː.teɪl/", "pos": "noun",
        "example_sentence": "She works in retail management.",
        "image_hint": "a bright clothing shop with racks and shelves",
    },
    "pet_vocab_250": {  # microeconomics
        "word": "voucher", "ipa": "/ˈvaʊ.tʃər/", "pos": "noun",
        "example_sentence": "I used a voucher at the till.",
        "image_hint": "a hand handing over a printed discount voucher",
    },
    "pet_vocab_253": {  # monopoly
        "word": "installment", "ipa": "/ɪnˈstɔːl.mənt/", "pos": "noun",
        "example_sentence": "I paid the first installment today.",
        "image_hint": "a hand placing coins into a small savings jar",
    },
    "pet_vocab_252": {  # oligopoly
        "word": "warranty", "ipa": "/ˈwɒr.ən.ti/", "pos": "noun",
        "example_sentence": "This laptop has a two-year warranty.",
        "image_hint": "a hand holding a printed warranty card beside a box",
    },
}


def apply_fixes(level: str, fixes: dict, apply: bool) -> list[str]:
    path = os.path.join(VOCAB_DIR, f"{level}.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    index = {w["id"]: w for w in data["words"]}
    changed_ids = []
    for vocab_id, new_fields in fixes.items():
        entry = index.get(vocab_id)
        if entry is None:
            print(f"  ! {vocab_id} không tồn tại — bỏ qua")
            continue
        for field in ("word", "ipa", "pos", "example_sentence", "image_hint"):
            new_value = new_fields[field]
            if entry.get(field) != new_value:
                print(f"  {vocab_id}.{field}: {entry.get(field)!r} → {new_value!r}")
                entry[field] = new_value
        changed_ids.append(vocab_id)

    if apply and changed_ids:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"  → đã ghi {path}")

    return changed_ids


def main() -> int:
    apply = "--apply" in sys.argv

    print("--- KET ---")
    ket_changed = apply_fixes("ket", KET_FIXES, apply)
    print("--- PET ---")
    pet_changed = apply_fixes("pet", PET_FIXES, apply)

    total = len(ket_changed) + len(pet_changed)
    print()
    print(f"{'ĐÃ SỬA' if apply else 'DRY RUN'}: {total} mục ({len(ket_changed)} KET, {len(pet_changed)} PET).")
    if apply:
        print("Audio cần xoá rồi sinh lại (word + sentence cho mỗi id):")
        for vocab_id in ket_changed:
            print(f"  audio/vocabulary/ket/{vocab_id}_word.mp3 audio/vocabulary/ket/{vocab_id}_sentence.mp3")
        for vocab_id in pet_changed:
            print(f"  audio/vocabulary/pet/{vocab_id}_word.mp3 audio/vocabulary/pet/{vocab_id}_sentence.mp3")
    else:
        print("Chạy lại với --apply để ghi thay đổi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
