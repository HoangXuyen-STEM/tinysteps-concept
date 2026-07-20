#!/usr/bin/env python3
"""Replace the remaining obvious CEFR outliers missed by the earlier KET/PET pass.

The selected entries are either specialist academic terms (for example epidemiology and
intersectionality) or members of the PET 410-475 nominalisation run.  That run was generated
with the same empty "The X should be confirmed" template as the previously repaired jargon.

IDs and topic_ids stay unchanged.  Run without --apply for a dry run.
"""

import json
import os
import sys


DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def item(word, ipa, pos, sentence, hint=None):
    return {
        "word": word,
        "ipa": f"/{ipa}/",
        "pos": pos,
        "example_sentence": sentence,
        "image_hint": hint or f"a clear everyday illustration of {word}",
    }


FIXES = {
    # KET (A2): two abstract -ness nouns left beside the repaired jargon block.
    "ket_vocab_385": item("pencil case", "ˈpen.səl keɪs", "noun", "My pencil case is on the desk."),
    "ket_vocab_386": item("diagram", "ˈdaɪ.ə.ɡræm", "noun", "Draw a simple diagram in your notebook."),

    # PET (B1): specialist health/social-science terms left by the earlier pass.
    "pet_vocab_288": item("heartbeat", "ˈhɑːt.biːt", "noun", "The nurse listened to my heartbeat."),
    "pet_vocab_298": item("friendship", "ˈfrend.ʃɪp", "noun", "Their friendship began at school."),
    "pet_vocab_299": item("childhood", "ˈtʃaɪld.hʊd", "noun", "She told us a story from her childhood."),
    "pet_vocab_303": item("classmate", "ˈklɑːs.meɪt", "noun", "I invited a classmate to my birthday party."),
    "pet_vocab_305": item("roommate", "ˈruːm.meɪt", "noun", "My roommate is friendly and easygoing."),

    # PET 410-426: academic nominalisations in the in-class topic.
    "pet_vocab_410": item("title", "ˈtaɪ.təl", "noun", "Write a title at the top of the page."),
    "pet_vocab_411": item("heading", "ˈhed.ɪŋ", "noun", "Put each idea under the correct heading."),
    "pet_vocab_412": item("comma", "ˈkɒm.ə", "noun", "Put a comma after the first phrase."),
    "pet_vocab_413": item("alphabet", "ˈæl.fə.bet", "noun", "The English alphabet has twenty-six letters."),
    "pet_vocab_414": item("arithmetic", "əˈrɪθ.mə.tɪk", "noun", "We practise arithmetic in the morning."),
    "pet_vocab_415": item("biology", "baɪˈɒl.ə.dʒi", "noun", "We studied plants in biology today."),
    "pet_vocab_416": item("chemistry", "ˈkem.ɪ.stri", "noun", "Chemistry helps us understand different materials."),
    "pet_vocab_417": item("physics", "ˈfɪz.ɪks", "noun", "We learned about light in physics."),
    "pet_vocab_418": item("geography", "dʒiˈɒɡ.rə.fi", "noun", "Geography teaches us about countries and rivers."),
    "pet_vocab_419": item("history", "ˈhɪs.tər.i", "noun", "Our history lesson was about ancient Rome."),
    "pet_vocab_420": item("diploma", "dɪˈpləʊ.mə", "noun", "She received her diploma after the course."),
    "pet_vocab_421": item("degree", "dɪˈɡriː", "noun", "He hopes to study for a science degree."),
    "pet_vocab_422": item("research", "rɪˈsɜːtʃ", "noun", "I did some research for my school project."),
    "pet_vocab_423": item("laboratory", "ləˈbɒr.ə.tər.i", "noun", "Wear safety glasses in the laboratory."),
    "pet_vocab_425": item("library", "ˈlaɪ.brər.i", "noun", "I borrowed two books from the library."),
    "pet_vocab_426": item("composition", "ˌkɒm.pəˈzɪʃ.ən", "noun", "Write a short composition about your town."),

    # PET 427-438: concrete, everyday social and leisure vocabulary.
    "pet_vocab_427": item("guest", "ɡest", "noun", "We welcomed every guest at the door."),
    "pet_vocab_428": item("host", "həʊst", "noun", "Our host showed us around the house."),
    "pet_vocab_429": item("couple", "ˈkʌp.əl", "noun", "A young couple moved in next door."),
    "pet_vocab_430": item("course", "kɔːs", "noun", "I joined an evening English course."),
    "pet_vocab_431": item("teammate", "ˈtiːm.meɪt", "noun", "My teammate passed me the ball."),
    "pet_vocab_432": item("picnic", "ˈpɪk.nɪk", "noun", "We had a picnic beside the lake."),
    "pet_vocab_433": item("camping", "ˈkæm.pɪŋ", "noun", "We went camping in the mountains."),
    "pet_vocab_434": item("nightlife", "ˈnaɪt.laɪf", "noun", "The city is famous for its nightlife."),
    "pet_vocab_435": item("pottery", "ˈpɒt.ər.i", "noun", "She makes pottery in her free time."),
    "pet_vocab_436": item("sculpture", "ˈskʌlp.tʃər", "noun", "We saw a stone sculpture in the park."),
    "pet_vocab_437": item("drawing", "ˈdrɔː.ɪŋ", "noun", "He gave me a drawing of his dog."),
    "pet_vocab_438": item("painting", "ˈpeɪn.tɪŋ", "noun", "That painting shows a busy market."),

    # PET 439-475: replace the rest of the mass-produced nominalisation block.
    "pet_vocab_439": item("attach", "əˈtætʃ", "verb", "Attach the photo to your application."),
    "pet_vocab_440": item("guitar", "ɡɪˈtɑːr", "noun", "She plays the guitar in a band."),
    "pet_vocab_441": item("equipment", "ɪˈkwɪp.mənt", "noun", "The school bought new sports equipment."),
    "pet_vocab_442": item("keyboard", "ˈkiː.bɔːd", "noun", "This keyboard is easier to use."),
    "pet_vocab_443": item("printer", "ˈprɪn.tər", "noun", "The printer is in the staff room."),
    "pet_vocab_444": item("shopper", "ˈʃɒp.ər", "noun", "Each shopper received a free bag."),
    "pet_vocab_445": item("department", "dɪˈpɑːt.mənt", "noun", "Ask for help in the shoe department."),
    "pet_vocab_446": item("podcast", "ˈpɒd.kɑːst", "noun", "Our school publishes a weekly podcast."),
    "pet_vocab_447": item("fiction", "ˈfɪk.ʃən", "noun", "She prefers fiction to history books."),
    "pet_vocab_448": item("online", "ˈɒn.laɪn", "adverb", "You can complete the form online."),
    "pet_vocab_449": item("collection", "kəˈlek.ʃən", "noun", "He showed us his stamp collection."),
    "pet_vocab_450": item("facilities", "fəˈsɪl.ə.tiz", "noun", "The town has excellent sports facilities."),
    "pet_vocab_451": item("store", "stɔːr", "noun", "This store sells clothes at low prices."),
    "pet_vocab_452": item("trip", "trɪp", "noun", "We took a day trip to the coast."),
    "pet_vocab_453": item("sightseeing", "ˈsaɪtˌsiː.ɪŋ", "noun", "We went sightseeing after breakfast."),
    "pet_vocab_454": item("brochure", "ˈbrəʊ.ʃər", "noun", "The hotel brochure includes a map."),
    "pet_vocab_455": item("cabin", "ˈkæb.ɪn", "noun", "We stayed in a cabin by the lake."),
    "pet_vocab_456": item("comment", "ˈkɒm.ent", "noun", "The teacher posted a helpful comment."),
    "pet_vocab_457": item("elementary", "ˌel.ɪˈmen.tər.i", "adjective", "This book is for elementary learners."),
    "pet_vocab_458": item("pupil", "ˈpjuː.pəl", "noun", "Each pupil completed the activity."),
    "pet_vocab_459": item("classwork", "ˈklɑːs.wɜːk", "noun", "Please finish your classwork before lunch."),
    "pet_vocab_460": item("semester", "sɪˈmes.tər", "noun", "We have three exams this semester."),
    "pet_vocab_461": item("term", "tɜːm", "noun", "The new school term starts next week."),
    "pet_vocab_462": item("calculator", "ˈkæl.kjə.leɪ.tər", "noun", "Bring a calculator to the maths lesson."),
    "pet_vocab_463": item("robot", "ˈrəʊ.bɒt", "noun", "The students built a small robot."),
    "pet_vocab_464": item("fold", "fəʊld", "verb", "Fold the paper in half."),
    "pet_vocab_465": item("rubber", "ˈrʌb.ər", "noun", "Use a rubber to correct the mistake."),
    "pet_vocab_466": item("bookshelf", "ˈbʊk.ʃelf", "noun", "Put the dictionary on the bookshelf."),
    "pet_vocab_467": item("fasten", "ˈfɑː.sən", "verb", "Fasten the two sheets together."),
    "pet_vocab_468": item("experiment", "ɪkˈsper.ɪ.mənt", "noun", "We did a simple science experiment."),
    "pet_vocab_469": item("science", "ˈsaɪ.əns", "noun", "Science is my favourite school subject."),
    "pet_vocab_470": item("explanation", "ˌek.spləˈneɪ.ʃən", "noun", "Her explanation was clear and helpful."),
    "pet_vocab_471": item("speech", "spiːtʃ", "noun", "He gave a short speech to the class."),
    "pet_vocab_472": item("description", "dɪˈskrɪp.ʃən", "noun", "Write a description of the picture."),
    "pet_vocab_473": item("article", "ˈɑː.tɪ.kəl", "noun", "We read an article about space travel."),
    "pet_vocab_474": item("magazine", "ˌmæɡ.əˈziːn", "noun", "I found the photograph in a magazine."),
    "pet_vocab_475": item("wildlife", "ˈwaɪld.laɪf", "noun", "We should protect local wildlife."),

    # Three remaining theory terms near the end of PET.
    "pet_vocab_489": item("fact", "fækt", "noun", "Check every fact before you share the story."),
    "pet_vocab_493": item("teamwork", "ˈtiːm.wɜːk", "noun", "Good teamwork helped us finish early."),
    "pet_vocab_498": item("symbol", "ˈsɪm.bəl", "noun", "A red circle is a common warning symbol."),
}


def main():
    apply = "--apply" in sys.argv
    changed = []
    for level in ("ket", "pet"):
        path = os.path.join(DATA_DIR, "vocabulary", f"{level}.json")
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        touched = False
        for entry in data["words"]:
            replacement = FIXES.get(entry["id"])
            if replacement is None:
                continue
            print(f"{entry['id']}: {entry['word']} -> {replacement['word']}")
            entry.update(replacement)
            changed.append(entry["id"])
            touched = True
        if touched and apply:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
    expected = set(FIXES)
    if set(changed) != expected:
        missing = sorted(expected - set(changed))
        raise SystemExit(f"Missing vocabulary IDs: {missing}")
    print(f"{'Applied' if apply else 'Dry run'}: {len(changed)} entries")


if __name__ == "__main__":
    main()
