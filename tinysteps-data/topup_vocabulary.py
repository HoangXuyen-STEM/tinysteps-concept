#!/usr/bin/env python3
"""
TinySteps — topup_vocabulary.py
Fills vocabulary gap with curated, CEFR-level-appropriate words.
Each entry: (word, pos, ipa, topic_id, image_hint, example_sentence)
Reads existing words first → only adds what is missing.
"""

import json, os, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR  = os.path.join(SCRIPT_DIR, "vocabulary")
TOPICS_FILE = os.path.join(SCRIPT_DIR, "topics", "topics.json")
LEVELS     = ["starters", "movers", "flyers", "ket", "pet"]

TARGETS = {"starters": 300, "movers": 400, "flyers": 500, "ket": 400, "pet": 500}

# ─────────────────────────────────────────────────────────────────────────────
# WORD BANKS — (word, pos, ipa, topic_id, image_hint, example_sentence)
# Starters = A1 | Movers = A1+ | Flyers = A2 | KET = B1 | PET = B2
# ─────────────────────────────────────────────────────────────────────────────

WORD_BANK = {

# ═══════════════════════════════════════════════════════════════════════════
# STARTERS — A1 concrete vocabulary
# ═══════════════════════════════════════════════════════════════════════════
"starters": [
    # topic_before_class
    ("hall", "noun", "/hɔːl/", "topic_before_class", "a school entrance hall with doors and chairs", "I see the hall."),
    ("office", "noun", "/ˈɒf.ɪs/", "topic_before_class", "a small school office with a desk", "She is in the office."),
    ("gate", "noun", "/ɡeɪt/", "topic_before_class", "a metal school gate with students walking through", "Open the gate, please."),
    ("key", "noun", "/kiː/", "topic_before_class", "a small silver key on a desk", "I have a key."),
    ("note", "noun", "/nəʊt/", "topic_before_class", "a small white paper note on a board", "Read the note."),
    ("uniform", "noun", "/ˈjuː.nɪ.fɔːm/", "topic_before_class", "a neat school uniform hanging on a hook", "This is my uniform."),
    ("late", "adjective", "/leɪt/", "topic_before_class", "a clock showing 8:15 with a worried face", "I am late."),
    ("arrive", "verb", "/əˈraɪv/", "topic_before_class", "a student walking through a school door", "I arrive early."),
    ("sit", "verb", "/sɪt/", "topic_before_class", "a student sitting at a school desk", "Please sit down."),
    ("stand", "verb", "/stænd/", "topic_before_class", "students standing up next to their chairs", "Stand up, please."),
    ("flag", "noun", "/flæɡ/", "topic_before_class", "a flag on a pole in a school yard", "I see the flag."),
    ("board", "noun", "/bɔːd/", "topic_before_class", "a notice board with papers pinned to it", "Look at the board."),
    # topic_in_class
    ("word", "noun", "/wɜːd/", "topic_in_class", "a single word written on a whiteboard", "Write the word."),
    ("letter", "noun", "/ˈlet.ər/", "topic_in_class", "the letter A drawn in bright red on paper", "This is the letter A."),
    ("number", "noun", "/ˈnʌm.bər/", "topic_in_class", "the number five written on a school board", "Write the number."),
    ("line", "noun", "/laɪn/", "topic_in_class", "a straight line drawn with a ruler on paper", "Draw a line."),
    ("shape", "noun", "/ʃeɪp/", "topic_in_class", "simple colourful shapes on a worksheet", "What shape is this?"),
    ("colour", "noun", "/ˈkʌl.ər/", "topic_in_class", "a row of colourful crayons side by side", "What colour is it?"),
    ("draw", "verb", "/drɔː/", "topic_in_class", "a child drawing a house with a pencil", "Draw a house."),
    ("copy", "verb", "/ˈkɒp.i/", "topic_in_class", "a student copying words from the board", "Copy the words."),
    ("match", "verb", "/mætʃ/", "topic_in_class", "two matching pictures connected with a line", "Match the pictures."),
    ("fill", "verb", "/fɪl/", "topic_in_class", "a blank worksheet with spaces to fill in", "Fill in the blank."),
    ("circle", "verb", "/ˈsɜː.kəl/", "topic_in_class", "a pencil circling the correct answer", "Circle the answer."),
    ("tick", "verb", "/tɪk/", "topic_in_class", "a green tick next to a correct answer", "Tick the box."),
    ("name", "noun", "/neɪm/", "topic_in_class", "a name written at the top of a paper", "Write your name."),
    ("right", "adjective", "/raɪt/", "topic_in_class", "a correct answer marked with a green tick", "That is right."),
    ("wrong", "adjective", "/rɒŋ/", "topic_in_class", "a red cross next to an incorrect answer", "That is wrong."),
    # topic_giving_instructions
    ("stop", "verb", "/stɒp/", "topic_giving_instructions", "a red stop sign on a white background", "Stop now, please."),
    ("go", "verb", "/ɡəʊ/", "topic_giving_instructions", "a green go sign with an arrow forward", "Go to the board."),
    ("come", "verb", "/kʌm/", "topic_giving_instructions", "a teacher gesturing students to come forward", "Come here, please."),
    ("touch", "verb", "/tʌtʃ/", "topic_giving_instructions", "a finger touching a picture on a board", "Touch the picture."),
    ("point", "verb", "/pɔɪnt/", "topic_giving_instructions", "a hand pointing at a word on the board", "Point to the word."),
    ("hold", "verb", "/həʊld/", "topic_giving_instructions", "two hands holding up a book", "Hold the book up."),
    ("put", "verb", "/pʊt/", "topic_giving_instructions", "a pen being placed on a desk", "Put it down."),
    ("take", "verb", "/teɪk/", "topic_giving_instructions", "a hand taking a pencil from a case", "Take a pencil."),
    ("pick", "verb", "/pɪk/", "topic_giving_instructions", "a hand picking up a card from a table", "Pick up the card."),
    ("turn", "verb", "/tɜːn/", "topic_giving_instructions", "hands turning a book to a new page", "Turn the page."),
    ("walk", "verb", "/wɔːk/", "topic_giving_instructions", "students walking calmly in a school corridor", "Walk, don't run."),
    ("run", "verb", "/rʌn/", "topic_giving_instructions", "a child running with backpack in school yard", "Don't run in class."),
    ("close", "verb", "/kləʊz/", "topic_giving_instructions", "a hand closing a notebook on a desk", "Close your book."),
    ("open", "verb", "/ˈəʊ.pən/", "topic_giving_instructions", "hands opening a colourful textbook", "Open your book."),
    ("show", "verb", "/ʃəʊ/", "topic_giving_instructions", "a student showing homework to the teacher", "Show me your work."),
    ("write", "verb", "/raɪt/", "topic_giving_instructions", "a hand writing on lined paper with a pen", "Write your name."),
    # topic_checking_understanding
    ("yes", "interjection", "/jes/", "topic_checking_understanding", "a smiling face nodding yes", "Yes, I understand."),
    ("no", "interjection", "/nəʊ/", "topic_checking_understanding", "a face shaking no with a gentle smile", "No, I don't know."),
    ("know", "verb", "/nəʊ/", "topic_checking_understanding", "a student tapping their head showing knowledge", "I know it."),
    ("see", "verb", "/siː/", "topic_checking_understanding", "a student looking carefully at a worksheet", "I see it."),
    ("try", "verb", "/traɪ/", "topic_checking_understanding", "a student trying to write an answer carefully", "Try again."),
    ("more", "adverb", "/mɔːr/", "topic_checking_understanding", "a speech bubble saying 'more please'", "More, please."),
    ("help", "verb", "/help/", "topic_checking_understanding", "a teacher helping a student with a notebook", "Help me, please."),
    ("again", "adverb", "/əˈɡen/", "topic_checking_understanding", "a circular arrow pointing around again", "Say it again."),
    ("slow", "adjective", "/sləʊ/", "topic_checking_understanding", "a turtle walking slowly on a path", "Go slow, please."),
    ("loud", "adjective", "/laʊd/", "topic_checking_understanding", "a speaker icon with sound waves", "Speak loud."),
    # topic_praise_correction
    ("bravo", "interjection", "/ˈbrɑː.vəʊ/", "topic_praise_correction", "a teacher clapping hands with a big smile", "Bravo! Very good!"),
    ("wow", "interjection", "/waʊ/", "topic_praise_correction", "a student looking amazed at a gold star", "Wow! That is great!"),
    ("star", "noun", "/stɑːr/", "topic_praise_correction", "a shiny gold star sticker on a notebook", "A star for you!"),
    ("super", "adjective", "/ˈsuː.pər/", "topic_praise_correction", "a superhero thumb-up with a yellow star badge", "Super! Well done!"),
    ("correct", "adjective", "/kəˈrekt/", "topic_praise_correction", "a green tick mark next to the correct answer", "Yes, that is correct."),
    ("wrong", "adjective", "/rɒŋ/", "topic_praise_correction", "a red cross next to an incorrect answer box", "That is wrong. Try again."),
    ("better", "adjective", "/ˈbet.ər/", "topic_praise_correction", "two versions of a drawing, the second one better", "This is better."),
    ("smart", "adjective", "/smɑːt/", "topic_praise_correction", "a student wearing glasses with a bright idea lightbulb", "You are smart!"),
    ("nice", "adjective", "/naɪs/", "topic_praise_correction", "a teacher giving a thumbs up to a student", "Very nice work!"),
    ("well", "adverb", "/wel/", "topic_praise_correction", "a student smiling proudly with a completed worksheet", "Well done!"),
    # topic_school_communication
    ("class", "noun", "/klɑːs/", "topic_school_communication", "a class of students sitting in rows", "This is my class."),
    ("grade", "noun", "/ɡreɪd/", "topic_school_communication", "a report card with letter grades A and B", "She has a good grade."),
    ("visit", "verb", "/ˈvɪz.ɪt/", "topic_school_communication", "a parent visiting a teacher at school", "Please visit us."),
    ("letter", "noun", "/ˈlet.ər/", "topic_school_communication", "a folded letter in an envelope on a desk", "Read the letter."),
    ("send", "verb", "/send/", "topic_school_communication", "a hand dropping a letter into a post box", "Send this letter."),
    ("read", "verb", "/riːd/", "topic_school_communication", "a student reading a book at their desk", "Read this, please."),
    ("sign", "verb", "/saɪn/", "topic_school_communication", "a hand signing a paper with a pen", "Sign the paper."),
    ("meet", "verb", "/miːt/", "topic_school_communication", "two people shaking hands at a school entrance", "Nice to meet you."),
    ("speak", "verb", "/spiːk/", "topic_school_communication", "a person speaking to a small group", "Please speak now."),
    ("ask", "verb", "/ɑːsk/", "topic_school_communication", "a student with hand raised asking a question", "Please ask me."),
    # topic_market
    ("apple", "noun", "/ˈæp.əl/", "topic_market", "a shiny red apple on a market stall", "I want an apple."),
    ("banana", "noun", "/bəˈnɑː.nə/", "topic_market", "a bunch of yellow bananas on a market stall", "Buy a banana."),
    ("egg", "noun", "/eɡ/", "topic_market", "a basket of white eggs at a market stall", "I need one egg."),
    ("milk", "noun", "/mɪlk/", "topic_market", "a carton of fresh milk on a wooden shelf", "I like milk."),
    ("bread", "noun", "/bred/", "topic_market", "a freshly baked round loaf of bread", "I want bread."),
    ("meat", "noun", "/miːt/", "topic_market", "fresh cuts of meat on a market counter", "I buy meat."),
    ("fish", "noun", "/fɪʃ/", "topic_market", "fresh fish on ice at a wet market", "I like fish."),
    ("onion", "noun", "/ˈʌn.jən/", "topic_market", "a pile of purple onions at a market stall", "I buy onions."),
    ("tomato", "noun", "/təˈmɑː.təʊ/", "topic_market", "red ripe tomatoes in a basket at the market", "I see tomatoes."),
    ("carrot", "noun", "/ˈkær.ət/", "topic_market", "bright orange carrots tied in a bundle", "I like carrots."),
    ("cheap", "adjective", "/tʃiːp/", "topic_market", "a price tag with a low price and a smile", "It is cheap."),
    ("fresh", "adjective", "/freʃ/", "topic_market", "bright green fresh vegetables glistening with water", "It is fresh."),
    ("bag", "noun", "/bæɡ/", "topic_market", "a plastic bag full of market vegetables", "A bag of rice."),
    # topic_restaurant
    ("food", "noun", "/fuːd/", "topic_restaurant", "a colourful plate of Vietnamese food", "I like food."),
    ("water", "noun", "/ˈwɔː.tər/", "topic_restaurant", "a tall glass of clear water with ice", "Water, please."),
    ("eat", "verb", "/iːt/", "topic_restaurant", "a person eating a bowl of soup with chopsticks", "I want to eat."),
    ("drink", "verb", "/drɪŋk/", "topic_restaurant", "a person drinking juice through a straw", "I want to drink."),
    ("hungry", "adjective", "/ˈhʌŋ.ɡri/", "topic_restaurant", "a cartoon stomach growling with an empty face", "I am hungry."),
    ("full", "adjective", "/fʊl/", "topic_restaurant", "a happy face with a full stomach after eating", "I am full."),
    ("order", "verb", "/ˈɔː.dər/", "topic_restaurant", "a waiter writing an order in a notepad", "I want to order."),
    ("table", "noun", "/ˈteɪ.bəl/", "topic_restaurant", "a small round table with two chairs at a cafe", "Sit at the table."),
    ("glass", "noun", "/ɡlɑːs/", "topic_restaurant", "a clear glass of orange juice on a table", "A glass of juice."),
    ("cup", "noun", "/kʌp/", "topic_restaurant", "a white ceramic cup of hot tea", "A cup of tea."),
    ("noodle", "noun", "/ˈnuː.dəl/", "topic_restaurant", "a bowl of noodle soup with chopsticks", "I like noodles."),
    ("soup", "noun", "/suːp/", "topic_restaurant", "a steaming bowl of clear broth soup", "I want soup."),
    ("sweet", "adjective", "/swiːt/", "topic_restaurant", "a smiling face tasting something sweet", "It is sweet."),
    # topic_travel
    ("bus", "noun", "/bʌs/", "topic_travel", "a yellow school bus parked on a road", "Take the bus."),
    ("car", "noun", "/kɑːr/", "topic_travel", "a small red car driving on a sunny road", "Go by car."),
    ("road", "noun", "/rəʊd/", "topic_travel", "a wide straight road with lane markings", "Cross the road."),
    ("near", "adjective", "/nɪər/", "topic_travel", "two houses close together on a quiet street", "It is near here."),
    ("far", "adjective", "/fɑːr/", "topic_travel", "a person looking at a distant mountain", "Is it far?"),
    ("here", "adverb", "/hɪər/", "topic_travel", "a hand pointing downward to a spot on a map", "Come here."),
    ("there", "adverb", "/ðeər/", "topic_travel", "an arm pointing to a destination on a map", "Go there."),
    ("map", "noun", "/mæp/", "topic_travel", "a folded paper map with roads and buildings", "Look at the map."),
    ("left", "adverb", "/left/", "topic_travel", "a left turn arrow on a blue road sign", "Turn left."),
    ("right", "adverb", "/raɪt/", "topic_travel", "a right turn arrow on a blue road sign", "Turn right."),
    ("straight", "adverb", "/streɪt/", "topic_travel", "a straight ahead arrow on a road sign", "Go straight."),
    ("stop", "noun", "/stɒp/", "topic_travel", "a bus stop sign with a bench beside it", "This is the stop."),
    # topic_phone
    ("phone", "noun", "/fəʊn/", "topic_phone", "a white smartphone on a wooden desk", "My phone rings."),
    ("number", "noun", "/ˈnʌm.bər/", "topic_phone", "a phone screen showing a mobile number", "What is the number?"),
    ("ring", "verb", "/rɪŋ/", "topic_phone", "a phone with sound waves showing it ringing", "My phone rings."),
    ("talk", "verb", "/tɔːk/", "topic_phone", "two people talking on the phone and smiling", "I talk to my friend."),
    ("hear", "verb", "/hɪər/", "topic_phone", "a person holding a phone to their ear", "Can you hear me?"),
    ("loud", "adjective", "/laʊd/", "topic_phone", "a speaker with large sound waves coming out", "Speak loud, please."),
    # topic_health
    ("hurt", "verb", "/hɜːt/", "topic_health", "a cartoon character holding their arm in pain", "My arm hurts."),
    ("pain", "noun", "/peɪn/", "topic_health", "a red lightning bolt symbol indicating pain", "I feel pain."),
    ("cold", "noun", "/kəʊld/", "topic_health", "a person sneezing into a tissue", "I have a cold."),
    ("hot", "adjective", "/hɒt/", "topic_health", "a face with a fever and a red thermometer", "I feel hot."),
    ("rest", "verb", "/rest/", "topic_health", "a person lying comfortably in bed resting", "Please rest."),
    ("sleep", "verb", "/sliːp/", "topic_health", "a person sleeping peacefully in a bed", "Go to sleep."),
    ("head", "noun", "/hed/", "topic_health", "a cartoon head with a star showing a headache", "My head hurts."),
    ("stomach", "noun", "/ˈstʌm.ək/", "topic_health", "a cartoon stomach with a pain signal", "My stomach hurts."),
    ("tooth", "noun", "/tuːθ/", "topic_health", "a cartoon tooth with a sad face", "My tooth hurts."),
    ("arm", "noun", "/ɑːm/", "topic_health", "a raised arm showing a simple bandage", "My arm hurts."),
    ("leg", "noun", "/leɡ/", "topic_health", "a cartoon leg with a bandage wrapped around", "My leg hurts."),
    ("eye", "noun", "/aɪ/", "topic_health", "a close-up of a friendly cartoon eye", "My eye hurts."),
    ("ear", "noun", "/ɪər/", "topic_health", "a cartoon ear with a small music note", "My ear hurts."),
    ("fever", "noun", "/ˈfiː.vər/", "topic_health", "a thermometer showing high temperature in red", "I have a fever."),
    ("medicine", "noun", "/ˈmed.ɪ.sɪn/", "topic_health", "a bottle of medicine with a spoon beside it", "Take the medicine."),
    ("nurse", "noun", "/nɜːs/", "topic_health", "a nurse in white uniform smiling at a patient", "The nurse helps."),
    # topic_social
    ("friend", "noun", "/frend/", "topic_social", "two children holding hands and smiling together", "She is my friend."),
    ("happy", "adjective", "/ˈhæp.i/", "topic_social", "a bright smiley face on a sunny background", "I am happy."),
    ("sad", "adjective", "/sæd/", "topic_social", "a cartoon face with a downturned mouth", "He is sad."),
    ("like", "verb", "/laɪk/", "topic_social", "a thumb-up icon with a heart", "I like it."),
    ("love", "verb", "/lʌv/", "topic_social", "a red heart surrounded by smaller hearts", "I love school."),
    ("family", "noun", "/ˈfæm.ɪ.li/", "topic_social", "a cartoon family of four standing together", "This is my family."),
    ("home", "noun", "/həʊm/", "topic_social", "a small house with a garden and smoke from chimney", "I go home."),
    ("play", "verb", "/pleɪ/", "topic_social", "children playing a ball game in a sunny park", "Let us play."),
    ("fun", "noun", "/fʌn/", "topic_social", "children laughing while playing a game together", "School is fun."),
    ("today", "noun", "/təˈdeɪ/", "topic_social", "a calendar page with a circle around today", "See you today."),
    ("sunny", "adjective", "/ˈsʌn.i/", "topic_social", "a bright sun shining with rays on a blue sky", "It is sunny today."),
    ("weather", "noun", "/ˈweð.ər/", "topic_social", "icons showing sun rain and cloud side by side", "The weather is nice."),
    ("mother", "noun", "/ˈmʌð.ər/", "topic_social", "a warm mother and child hugging at a school gate", "My mother is here."),
    ("father", "noun", "/ˈfɑː.ðər/", "topic_social", "a father and child walking together with backpacks", "My father walks."),
    ("sister", "noun", "/ˈsɪs.tər/", "topic_social", "two girls in matching school uniforms smiling", "This is my sister."),
    ("brother", "noun", "/ˈbrʌð.ər/", "topic_social", "two boys with matching backpacks outside school", "He is my brother."),
    ("red", "adjective", "/red/", "topic_social", "a bright red crayon on a white background", "It is red."),
    ("blue", "adjective", "/bluː/", "topic_social", "a bright blue crayon next to a blue shape", "My pen is blue."),
    ("green", "adjective", "/ɡriːn/", "topic_social", "a green leaf on a sunny background", "Grass is green."),
    ("yellow", "adjective", "/ˈjel.əʊ/", "topic_social", "a bright yellow banana in sunlight", "It is yellow."),
    ("big", "adjective", "/bɪɡ/", "topic_social", "a large elephant next to a tiny mouse", "It is big."),
    ("small", "adjective", "/smɔːl/", "topic_social", "a tiny mouse next to a large elephant", "It is small."),
    ("new", "adjective", "/njuː/", "topic_social", "a brand new pencil in its original packaging", "This is new."),
    ("old", "adjective", "/əʊld/", "topic_social", "a worn old book with a faded cover", "This book is old."),
],

# ═══════════════════════════════════════════════════════════════════════════
# MOVERS — A1+/A2 vocabulary (daily actions, comparatives, past events)
# ═══════════════════════════════════════════════════════════════════════════
"movers": [
    # topic_before_class
    ("prepare", "verb", "/prɪˈpeər/", "topic_before_class", "a teacher arranging books and papers on a desk", "I prepared the lesson yesterday."),
    ("timetable", "noun", "/ˈtaɪm.teɪ.bəl/", "topic_before_class", "a weekly school timetable with coloured subjects", "Check the timetable."),
    ("meeting", "noun", "/ˈmiː.tɪŋ/", "topic_before_class", "teachers sitting around a table in discussion", "We had a meeting."),
    ("plan", "noun", "/plæn/", "topic_before_class", "a lesson plan sheet on a clipboard", "She prepared a plan."),
    ("print", "verb", "/prɪnt/", "topic_before_class", "a printer printing out lesson worksheets", "Please print the sheets."),
    ("folder", "noun", "/ˈfəʊl.dər/", "topic_before_class", "a blue paper folder with documents inside", "Put it in the folder."),
    ("board", "noun", "/bɔːd/", "topic_before_class", "a teacher writing on a whiteboard before class", "She cleaned the board."),
    ("marker", "noun", "/ˈmɑː.kər/", "topic_before_class", "a black dry-erase marker on a whiteboard shelf", "I need a marker."),
    ("chalk", "noun", "/tʃɔːk/", "topic_before_class", "white chalk sticks in a small tray below a blackboard", "Use the chalk."),
    ("worksheet", "noun", "/ˈwɜːk.ʃiːt/", "topic_before_class", "a printed worksheet with exercises on a desk", "Prepare the worksheets."),
    ("eraser", "noun", "/ɪˈreɪ.zər/", "topic_before_class", "a white board eraser on a whiteboard ledge", "I cleaned the board."),
    ("ruler", "noun", "/ˈruː.lər/", "topic_before_class", "a yellow plastic ruler on a teacher's desk", "She has a ruler."),
    ("stapler", "noun", "/ˈsteɪ.plər/", "topic_before_class", "a red stapler on an office desk", "Use the stapler."),
    ("notice", "noun", "/ˈnəʊ.tɪs/", "topic_before_class", "a notice pinned to a school announcement board", "Read the notice."),
    ("arrive", "verb", "/əˈraɪv/", "topic_before_class", "a teacher arriving at school early in the morning", "She arrived early."),
    ("early", "adverb", "/ˈɜː.li/", "topic_before_class", "an alarm clock ringing early in the morning", "I arrived early."),
    ("late", "adverb", "/leɪt/", "topic_before_class", "a clock showing 8:30 with a worried person rushing", "He arrived late."),
    # topic_in_class
    ("homework", "noun", "/ˈhəʊm.wɜːk/", "topic_in_class", "a student's neatly written homework notebook", "Did you do the homework?"),
    ("exercise", "noun", "/ˈek.sə.saɪz/", "topic_in_class", "a worksheet page with numbered exercises", "Do the exercise."),
    ("answer", "noun", "/ˈɑːn.sər/", "topic_in_class", "a worksheet with answers neatly written in", "Write the answer."),
    ("question", "noun", "/ˈkwes.tʃən/", "topic_in_class", "a question mark on a whiteboard with a teacher pointing", "Ask a question."),
    ("group", "noun", "/ɡruːp/", "topic_in_class", "four students sitting together at a round table", "Work in a group."),
    ("partner", "noun", "/ˈpɑːt.nər/", "topic_in_class", "two students working together side by side", "Work with your partner."),
    ("activity", "noun", "/ækˈtɪv.ɪ.ti/", "topic_in_class", "students engaged in a hands-on learning activity", "Do the activity."),
    ("sentence", "noun", "/ˈsen.təns/", "topic_in_class", "a complete sentence written on a whiteboard", "Read the sentence."),
    ("practice", "verb", "/ˈpræk.tɪs/", "topic_in_class", "a student repeatedly practising writing", "Practice saying it."),
    ("repeat", "verb", "/rɪˈpiːt/", "topic_in_class", "a teacher pointing to a student to repeat a phrase", "Repeat after me."),
    ("learn", "verb", "/lɜːn/", "topic_in_class", "a lightbulb above a student's head showing learning", "We learn English."),
    ("understand", "verb", "/ˌʌn.dəˈstænd/", "topic_in_class", "a student nodding their head in understanding", "Do you understand?"),
    ("explain", "verb", "/ɪkˈspleɪn/", "topic_in_class", "a teacher gesturing while explaining at the board", "Can you explain this?"),
    ("score", "noun", "/skɔːr/", "topic_in_class", "a test paper with a 9/10 score written at the top", "Good score!"),
    ("test", "noun", "/test/", "topic_in_class", "a printed test paper with questions and answer spaces", "We have a test."),
    ("quiz", "noun", "/kwɪz/", "topic_in_class", "a colourful quiz question on a classroom screen", "Do the quiz."),
    ("dictionary", "noun", "/ˈdɪk.ʃən.ər.i/", "topic_in_class", "a thick English dictionary lying open on a desk", "Use the dictionary."),
    ("story", "noun", "/ˈstɔː.ri/", "topic_in_class", "an illustrated children's storybook open on a desk", "Read the story."),
    # topic_giving_instructions
    ("follow", "verb", "/ˈfɒl.əʊ/", "topic_giving_instructions", "students following instructions from a worksheet", "Follow the steps."),
    ("complete", "verb", "/kəmˈpliːt/", "topic_giving_instructions", "a student completing the last item on a worksheet", "Complete the task."),
    ("underline", "verb", "/ˌʌn.dəˈlaɪn/", "topic_giving_instructions", "a hand underlining a word in a sentence", "Underline the word."),
    ("colour", "verb", "/ˈkʌl.ər/", "topic_giving_instructions", "crayons colouring in a picture on a worksheet", "Colour the picture."),
    ("paste", "verb", "/peɪst/", "topic_giving_instructions", "a glue stick and cut-out pictures being pasted", "Paste the picture."),
    ("cut", "verb", "/kʌt/", "topic_giving_instructions", "scissors cutting along a dotted line on paper", "Cut along the line."),
    ("number", "verb", "/ˈnʌm.bər/", "topic_giving_instructions", "a hand writing numbers 1 2 3 next to items", "Number the pictures."),
    ("order", "verb", "/ˈɔː.dər/", "topic_giving_instructions", "pictures being arranged in the correct sequence", "Put them in order."),
    ("careful", "adjective", "/ˈkeə.fəl/", "topic_giving_instructions", "a student working carefully with a pencil", "Be careful."),
    ("slow", "adverb", "/sləʊ/", "topic_giving_instructions", "a person walking slowly along a path", "Go slowly."),
    ("quickly", "adverb", "/ˈkwɪk.li/", "topic_giving_instructions", "a fast running figure with motion lines", "Do it quickly."),
    # topic_checking_understanding
    ("check", "verb", "/tʃek/", "topic_checking_understanding", "a teacher checking a student's work with a pen", "Check your answer."),
    ("correct", "verb", "/kəˈrekt/", "topic_checking_understanding", "a teacher correcting a mistake with a red pen", "Correct the mistake."),
    ("mistake", "noun", "/mɪˈsteɪk/", "topic_checking_understanding", "a crossed-out word with a correction above it", "Find the mistake."),
    ("idea", "noun", "/aɪˈdɪə/", "topic_checking_understanding", "a lightbulb above a person's head", "Good idea!"),
    ("meaning", "noun", "/ˈmiː.nɪŋ/", "topic_checking_understanding", "a dictionary entry showing a word and its meaning", "What is the meaning?"),
    ("true", "adjective", "/truː/", "topic_checking_understanding", "a green tick next to a true statement", "That is true."),
    ("false", "adjective", "/fɒls/", "topic_checking_understanding", "a red cross next to an incorrect statement", "That is false."),
    ("sure", "adjective", "/ʃɔːr/", "topic_checking_understanding", "a confident person with thumbs up", "Are you sure?"),
    ("confused", "adjective", "/kənˈfjuːzd/", "topic_checking_understanding", "a student looking confused with question marks above", "He looks confused."),
    ("slowly", "adverb", "/ˈsləʊ.li/", "topic_checking_understanding", "a turtle with a speech bubble showing slow speech", "Speak slowly, please."),
    ("difficult", "adjective", "/ˈdɪf.ɪ.kəlt/", "topic_checking_understanding", "a student looking at a hard test with a worried face", "It is difficult."),
    ("easy", "adjective", "/ˈiː.zi/", "topic_checking_understanding", "a student smiling at a simple worksheet", "This is easy."),
    # topic_praise_correction
    ("excellent", "adjective", "/ˈek.səl.ənt/", "topic_praise_correction", "a trophy with EXCELLENT written on a gold banner", "Excellent work today!"),
    ("perfect", "adjective", "/ˈpɜː.fekt/", "topic_praise_correction", "a gold star with a 100 percent score", "That is perfect!"),
    ("wonderful", "adjective", "/ˈwʌn.də.fəl/", "topic_praise_correction", "a teacher looking delighted at a student's work", "Wonderful drawing!"),
    ("improve", "verb", "/ɪmˈpruːv/", "topic_praise_correction", "an upward arrow showing progress on a chart", "You can improve."),
    ("praise", "noun", "/preɪz/", "topic_praise_correction", "a teacher smiling and giving a thumbs up to a student", "She got praise."),
    ("reward", "noun", "/rɪˈwɔːd/", "topic_praise_correction", "a gold star reward sticker on a child's notebook", "A reward for you!"),
    ("effort", "noun", "/ˈef.ət/", "topic_praise_correction", "a student working hard at their desk with focus", "Good effort!"),
    ("clever", "adjective", "/ˈklev.ər/", "topic_praise_correction", "a clever student holding a trophy and wearing glasses", "You are clever!"),
    # topic_school_communication
    ("email", "noun", "/ˈiː.meɪl/", "topic_school_communication", "a laptop screen showing an email message inbox", "She sent an email."),
    ("report", "noun", "/rɪˈpɔːt/", "topic_school_communication", "a printed school report card with marks", "I wrote the report."),
    ("parent", "noun", "/ˈpeə.rənt/", "topic_school_communication", "a parent and teacher meeting at a school table", "The parent came."),
    ("absence", "noun", "/ˈæb.səns/", "topic_school_communication", "an attendance book with a student's absence marked", "He has an absence."),
    ("sick", "adjective", "/sɪk/", "topic_school_communication", "a student at home in bed looking unwell", "He is sick today."),
    ("holiday", "noun", "/ˈhɒl.ɪ.deɪ/", "topic_school_communication", "a calendar with a holiday marked with a star", "It is a holiday."),
    ("event", "noun", "/ɪˈvent/", "topic_school_communication", "a school event poster with date and venue", "We have an event."),
    ("principal", "noun", "/ˈprɪn.sɪ.pəl/", "topic_school_communication", "a principal standing at the school entrance smiling", "See the principal."),
    ("contact", "verb", "/ˈkɒn.tækt/", "topic_school_communication", "a person on the phone next to a contact list", "Please contact us."),
    ("share", "verb", "/ʃeər/", "topic_school_communication", "two people sharing a paper document at a table", "Share the paper."),
    # topic_market
    ("vegetable", "noun", "/ˈvedʒ.tə.bəl/", "topic_market", "a pile of fresh mixed vegetables at a market stall", "I bought vegetables."),
    ("mango", "noun", "/ˈmæŋ.ɡəʊ/", "topic_market", "ripe yellow-green mangoes hanging on a tree", "I want a mango."),
    ("pork", "noun", "/pɔːk/", "topic_market", "slices of fresh pork on a market butcher counter", "She bought pork."),
    ("pepper", "noun", "/ˈpep.ər/", "topic_market", "red green and yellow peppers at a vegetable stall", "I like pepper."),
    ("garlic", "noun", "/ˈɡɑː.lɪk/", "topic_market", "a bunch of fresh garlic bulbs on a wooden board", "Buy some garlic."),
    ("lemon", "noun", "/ˈlem.ən/", "topic_market", "bright yellow lemons in a basket at the market", "She bought lemons."),
    ("grape", "noun", "/ɡreɪp/", "topic_market", "a bunch of purple grapes on a market fruit stall", "I like grapes."),
    ("price", "noun", "/praɪs/", "topic_market", "a price tag on a vegetable at a market stall", "What is the price?"),
    ("change", "noun", "/tʃeɪndʒ/", "topic_market", "coins and notes as change on a market counter", "Here is your change."),
    ("kilo", "noun", "/ˈkɪl.əʊ/", "topic_market", "a market scale showing one kilogram of vegetables", "One kilo, please."),
    ("pay", "verb", "/peɪ/", "topic_market", "a hand handing money to a market seller", "I need to pay."),
    # topic_restaurant
    ("menu", "noun", "/ˈmen.juː/", "topic_restaurant", "an open menu with food pictures and prices", "Can I see the menu?"),
    ("waiter", "noun", "/ˈweɪ.tər/", "topic_restaurant", "a smiling waiter in uniform holding a notepad", "The waiter came."),
    ("bill", "noun", "/bɪl/", "topic_restaurant", "a small bill folder on a restaurant table", "Can I have the bill?"),
    ("dish", "noun", "/dɪʃ/", "topic_restaurant", "a beautiful dish of Vietnamese food on a plate", "The dish is good."),
    ("taste", "verb", "/teɪst/", "topic_restaurant", "a person tasting food with a thoughtful expression", "Taste this dish."),
    ("delicious", "adjective", "/dɪˈlɪʃ.əs/", "topic_restaurant", "a person looking overjoyed at a plate of food", "It is delicious!"),
    ("spicy", "adjective", "/ˈspaɪ.si/", "topic_restaurant", "a bowl of red chilli soup with steam rising", "It is too spicy."),
    ("sour", "adjective", "/saʊər/", "topic_restaurant", "a face making a sour expression after tasting lemon", "It is sour."),
    ("hot", "adjective", "/hɒt/", "topic_restaurant", "a steaming bowl of hot noodle soup", "The soup is hot."),
    ("beef", "noun", "/biːf/", "topic_restaurant", "a beef noodle dish in a bowl with chopsticks", "I want beef noodles."),
    ("tofu", "noun", "/ˈtəʊ.fuː/", "topic_restaurant", "white squares of tofu in a bamboo steamer", "I like tofu."),
    # topic_travel
    ("train", "noun", "/treɪn/", "topic_travel", "a passenger train arriving at a station platform", "We took the train."),
    ("station", "noun", "/ˈsteɪ.ʃən/", "topic_travel", "a busy train station with arrivals board", "Go to the station."),
    ("airport", "noun", "/ˈeə.pɔːt/", "topic_travel", "an airport terminal with planes visible outside", "We went to the airport."),
    ("plane", "noun", "/pleɪn/", "topic_travel", "an aeroplane taking off into a clear blue sky", "She flew by plane."),
    ("boat", "noun", "/bəʊt/", "topic_travel", "a small wooden boat on a calm river in Vietnam", "I went by boat."),
    ("motorbike", "noun", "/ˈməʊ.tə.baɪk/", "topic_travel", "a motorbike parked outside a school gate", "He rode a motorbike."),
    ("bicycle", "noun", "/ˈbaɪ.sɪ.kəl/", "topic_travel", "a bicycle with a basket parked against a tree", "She rode a bicycle."),
    ("direction", "noun", "/daɪˈrek.ʃən/", "topic_travel", "a road with direction arrows pointing different ways", "Ask for directions."),
    ("turn", "noun", "/tɜːn/", "topic_travel", "a road turning left shown on a map", "Take the first turn."),
    ("cross", "verb", "/krɒs/", "topic_travel", "a person carefully crossing a pedestrian crossing", "Cross the road."),
    ("kilometre", "noun", "/ˈkɪl.ə.miː.tər/", "topic_travel", "a road sign showing 5 km to the city centre", "It is 3 kilometres."),
    ("walk", "verb", "/wɔːk/", "topic_travel", "a person walking along a tree-lined path", "She walked to school."),
    ("ride", "verb", "/raɪd/", "topic_travel", "a person riding a bicycle on a path", "He rode a bicycle."),
    # topic_phone
    ("call", "verb", "/kɔːl/", "topic_phone", "a person making a phone call at home", "Please call me."),
    ("answer", "verb", "/ˈɑːn.sər/", "topic_phone", "a hand picking up a ringing phone", "Answer the phone."),
    ("message", "noun", "/ˈmes.ɪdʒ/", "topic_phone", "a phone screen showing a text message notification", "Leave a message."),
    ("busy", "adjective", "/ˈbɪz.i/", "topic_phone", "a phone screen showing a busy tone symbol", "She is busy now."),
    ("voicemail", "noun", "/ˈvɔɪs.meɪl/", "topic_phone", "a phone voicemail icon with a number badge", "Leave a voicemail."),
    ("mobile", "noun", "/ˈməʊ.baɪl/", "topic_phone", "a modern mobile phone on a wooden table", "My mobile rang."),
    ("contact", "noun", "/ˈkɒn.tækt/", "topic_phone", "a contacts list on a phone screen", "Add the contact."),
    ("battery", "noun", "/ˈbæt.ər.i/", "topic_phone", "a phone showing a nearly empty battery symbol", "The battery is low."),
    # topic_health
    ("temperature", "noun", "/ˈtem.prɪ.tʃər/", "topic_health", "a digital thermometer showing a reading", "Check the temperature."),
    ("headache", "noun", "/ˈhed.eɪk/", "topic_health", "a person holding their head in pain", "I have a headache."),
    ("hungry", "adjective", "/ˈhʌŋ.ɡri/", "topic_health", "a cartoon stomach with a growling empty expression", "I am hungry."),
    ("tired", "adjective", "/ˈtaɪəd/", "topic_health", "a person yawning with heavy drooping eyes", "She is tired."),
    ("well", "adjective", "/wel/", "topic_health", "a smiling healthy person with rosy cheeks", "I feel well today."),
    ("better", "adjective", "/ˈbet.ər/", "topic_health", "a patient sitting up and smiling in hospital bed", "He feels better."),
    ("weak", "adjective", "/wiːk/", "topic_health", "a tired person sitting down looking pale", "She feels weak."),
    ("strong", "adjective", "/strɒŋ/", "topic_health", "a person flexing a muscle showing strength", "He feels strong."),
    ("sore", "adjective", "/sɔːr/", "topic_health", "a person holding their throat looking uncomfortable", "My throat is sore."),
    ("allergy", "noun", "/ˈæl.ər.dʒi/", "topic_health", "a person sneezing near flowers showing allergy", "She has an allergy."),
    # topic_social
    ("weekend", "noun", "/ˈwiːk.end/", "topic_social", "a calendar showing Saturday and Sunday circled", "See you at the weekend."),
    ("morning", "noun", "/ˈmɔː.nɪŋ/", "topic_social", "a sunrise over a quiet neighbourhood", "Good morning!"),
    ("afternoon", "noun", "/ˌɑːf.təˈnuːn/", "topic_social", "a bright afternoon sky with scattered clouds", "Good afternoon!"),
    ("evening", "noun", "/ˈiːv.nɪŋ/", "topic_social", "an orange sunset over buildings", "Good evening!"),
    ("night", "noun", "/naɪt/", "topic_social", "a dark sky with a bright full moon and stars", "Good night!"),
    ("tomorrow", "noun", "/təˈmɒr.əʊ/", "topic_social", "a calendar page being turned to the next day", "See you tomorrow."),
    ("yesterday", "noun", "/ˈjes.tə.deɪ/", "topic_social", "a calendar page with yesterday circled", "I saw you yesterday."),
    ("rain", "noun", "/reɪn/", "topic_social", "rain falling on a window with grey clouds outside", "It rained yesterday."),
    ("wind", "noun", "/wɪnd/", "topic_social", "trees bending in a strong wind", "The wind is strong."),
    ("cold", "adjective", "/kəʊld/", "topic_social", "a person in a scarf and coat looking cold", "It is very cold."),
    ("warm", "adjective", "/wɔːm/", "topic_social", "a person smiling in warm sunshine", "The weather is warm."),
    ("busy", "adjective", "/ˈbɪz.i/", "topic_social", "a street full of people going in many directions", "The street is busy."),
    ("quiet", "adjective", "/ˈkwaɪ.ɪt/", "topic_social", "an empty peaceful park on a calm morning", "It is quiet here."),
    ("interesting", "adjective", "/ˈɪn.trɪ.stɪŋ/", "topic_social", "a student looking fascinated at a book", "That is interesting."),
    ("boring", "adjective", "/ˈbɔː.rɪŋ/", "topic_social", "a person yawning at a dull grey screen", "It was boring."),
    ("excited", "adjective", "/ɪkˈsaɪ.tɪd/", "topic_social", "a happy excited person jumping with arms raised", "I am excited."),
    ("hobby", "noun", "/ˈhɒb.i/", "topic_social", "various hobby items like a book camera and basketball", "What is your hobby?"),
    ("sport", "noun", "/spɔːt/", "topic_social", "a football, tennis racket and swimming goggles together", "I like sport."),
    ("music", "noun", "/ˈmjuː.zɪk/", "topic_social", "musical notes floating above a guitar", "I love music."),
    ("film", "noun", "/fɪlm/", "topic_social", "a popcorn box and cinema screen in the dark", "Let us watch a film."),
    ("book", "noun", "/bʊk/", "topic_social", "a stack of colourful books in a library", "She loves reading books."),
],

# ═══════════════════════════════════════════════════════════════════════════
# FLYERS — A2 vocabulary (wider range, some abstract, opinions)
# ═══════════════════════════════════════════════════════════════════════════
"flyers": [
    # topic_before_class
    ("schedule", "noun", "/ˈʃed.juːl/", "topic_before_class", "a weekly schedule printed on a wall chart", "Check the schedule."),
    ("agenda", "noun", "/əˈdʒen.də/", "topic_before_class", "a meeting agenda document on a desk", "Read the agenda."),
    ("briefing", "noun", "/ˈbriː.fɪŋ/", "topic_before_class", "a group of teachers getting a morning briefing", "We had a briefing."),
    ("staff", "noun", "/stɑːf/", "topic_before_class", "a group of school staff standing for a photo", "The staff arrived."),
    ("session", "noun", "/ˈseʃ.ən/", "topic_before_class", "a teaching session in progress in a classroom", "The session starts soon."),
    ("update", "verb", "/ʌpˈdeɪt/", "topic_before_class", "a person updating a schedule on a whiteboard", "Please update the schedule."),
    ("inform", "verb", "/ɪnˈfɔːm/", "topic_before_class", "a teacher informing colleagues about changes", "She informed the staff."),
    ("review", "verb", "/rɪˈvjuː/", "topic_before_class", "a person reviewing documents at a desk", "Review the plan."),
    ("confirm", "verb", "/kənˈfɜːm/", "topic_before_class", "a person ticking a confirmation box on a form", "Please confirm the time."),
    ("procedure", "noun", "/prəˈsiː.dʒər/", "topic_before_class", "a step-by-step procedure list on a wall", "Follow the procedure."),
    ("routine", "noun", "/ruːˈtiːn/", "topic_before_class", "a morning routine checklist on a clipboard", "She has a good routine."),
    ("coordinator", "noun", "/kəʊˈɔː.dɪ.neɪ.tər/", "topic_before_class", "a coordinator managing a school schedule", "She is the coordinator."),
    ("handout", "noun", "/ˈhæn.daʊt/", "topic_before_class", "a teacher distributing printed handouts to students", "Take a handout."),
    ("resource", "noun", "/rɪˈzɔːs/", "topic_before_class", "teaching resources laid out on a prep table", "We need resources."),
    # topic_in_class
    ("grammar", "noun", "/ˈɡræm.ər/", "topic_in_class", "a grammar exercise book open on a desk", "Study the grammar."),
    ("vocabulary", "noun", "/vəˈkæb.jʊ.lər.i/", "topic_in_class", "a notebook with new vocabulary words listed", "Learn the vocabulary."),
    ("pronunciation", "noun", "/prəˌnʌn.siˈeɪ.ʃən/", "topic_in_class", "mouth diagrams showing pronunciation of sounds", "Check the pronunciation."),
    ("listening", "noun", "/ˈlɪs.ən.ɪŋ/", "topic_in_class", "students with headphones doing a listening task", "Do the listening."),
    ("speaking", "noun", "/ˈspiː.kɪŋ/", "topic_in_class", "two students speaking together in a dialogue activity", "Practice speaking."),
    ("reading", "noun", "/ˈriː.dɪŋ/", "topic_in_class", "a student reading a passage in a textbook", "Do the reading task."),
    ("writing", "noun", "/ˈraɪ.tɪŋ/", "topic_in_class", "a student carefully writing an essay", "Improve your writing."),
    ("passage", "noun", "/ˈpæs.ɪdʒ/", "topic_in_class", "a reading passage with highlighted key sentences", "Read the passage."),
    ("comprehension", "noun", "/ˌkɒm.prɪˈhen.ʃən/", "topic_in_class", "comprehension questions written under a reading text", "Answer the comprehension."),
    ("task", "noun", "/tɑːsk/", "topic_in_class", "a student focused on completing a task", "Finish the task."),
    ("project", "noun", "/ˈprɒdʒ.ekt/", "topic_in_class", "students working on a group project together", "Work on the project."),
    ("presentation", "noun", "/ˌprez.ənˈteɪ.ʃən/", "topic_in_class", "a student presenting to the class at the front", "Good presentation!"),
    ("topic", "noun", "/ˈtɒp.ɪk/", "topic_in_class", "a topic heading written on the board", "What is the topic?"),
    # topic_giving_instructions
    ("instruction", "noun", "/ɪnˈstrʌk.ʃən/", "topic_giving_instructions", "a numbered instruction list on a worksheet", "Read the instructions."),
    ("guideline", "noun", "/ˈɡaɪd.laɪn/", "topic_giving_instructions", "a set of guidelines posted on a classroom wall", "Follow the guidelines."),
    ("rule", "noun", "/ruːl/", "topic_giving_instructions", "classroom rules displayed on a colorful poster", "Follow the rules."),
    ("must", "verb", "/mʌst/", "topic_giving_instructions", "a must-do list with bold tick boxes", "You must follow rules."),
    ("should", "verb", "/ʃʊd/", "topic_giving_instructions", "a suggestion list on a classroom whiteboard", "You should try again."),
    ("must not", "phrase", "/ˈmʌst nɒt/", "topic_giving_instructions", "a red prohibition sign on a classroom door", "You must not run."),
    ("remember", "verb", "/rɪˈmem.bər/", "topic_giving_instructions", "a sticky note reminder on a desk", "Remember the rules."),
    ("attention", "noun", "/əˈten.ʃən/", "topic_giving_instructions", "a teacher tapping the board for students' attention", "Pay attention."),
    ("signal", "noun", "/ˈsɪɡ.nəl/", "topic_giving_instructions", "a teacher using a hand signal in class", "Watch for the signal."),
    ("organize", "verb", "/ˈɔː.ɡən.aɪz/", "topic_giving_instructions", "a person organizing materials on a desk", "Organize your work."),
    # topic_checking_understanding
    ("progress", "noun", "/ˈprəʊ.ɡres/", "topic_checking_understanding", "an upward progress chart on a classroom wall", "You are making progress."),
    ("feedback", "noun", "/ˈfiːd.bæk/", "topic_checking_understanding", "a teacher writing feedback on a student's work", "Good feedback!"),
    ("monitor", "verb", "/ˈmɒn.ɪ.tər/", "topic_checking_understanding", "a teacher walking between desks monitoring students", "She monitors progress."),
    ("assess", "verb", "/əˈses/", "topic_checking_understanding", "a teacher using a rubric to assess student work", "Assess the work."),
    ("evaluate", "verb", "/ɪˈvæl.jʊ.eɪt/", "topic_checking_understanding", "a person comparing two pieces of work", "Evaluate the answer."),
    ("concept", "noun", "/ˈkɒn.sept/", "topic_checking_understanding", "a concept map drawn with bubbles and arrows", "Explain the concept."),
    ("definition", "noun", "/ˌdef.ɪˈnɪʃ.ən/", "topic_checking_understanding", "a dictionary page showing a word definition", "What is the definition?"),
    ("example", "noun", "/ɪɡˈzɑːm.pəl/", "topic_checking_understanding", "a teacher pointing to an example on the board", "Give an example."),
    # topic_praise_correction
    ("encouragement", "noun", "/ɪnˈkʌr.ɪdʒ.mənt/", "topic_praise_correction", "a teacher giving an encouraging smile to a student", "Give encouragement."),
    ("correction", "noun", "/kəˈrek.ʃən/", "topic_praise_correction", "a marked paper with corrections in red ink", "Make the correction."),
    ("achievement", "noun", "/əˈtʃiːv.mənt/", "topic_praise_correction", "a student holding a certificate of achievement", "A great achievement!"),
    ("motivation", "noun", "/ˌməʊ.tɪˈveɪ.ʃən/", "topic_praise_correction", "an energised student raising their hand confidently", "She has motivation."),
    ("confidence", "noun", "/ˈkɒn.fɪ.dəns/", "topic_praise_correction", "a confident student standing tall and speaking", "Build your confidence."),
    ("mistake", "noun", "/mɪˈsteɪk/", "topic_praise_correction", "a crossed-out word with a neatly written correction above", "Correct the mistake."),
    ("apologise", "verb", "/əˈpɒl.ə.dʒaɪz/", "topic_praise_correction", "a student saying sorry to a teacher with a bow", "Please apologise."),
    # topic_school_communication
    ("colleague", "noun", "/ˈkɒl.iːɡ/", "topic_school_communication", "two teachers chatting in a staff room", "My colleague helped me."),
    ("appointment", "noun", "/əˈpɔɪnt.mənt/", "topic_school_communication", "a diary with an appointment time circled", "I have an appointment."),
    ("discussion", "noun", "/dɪˈskʌʃ.ən/", "topic_school_communication", "a small group in a discussion at a round table", "We had a discussion."),
    ("notice", "verb", "/ˈnəʊ.tɪs/", "topic_school_communication", "a person reading a notice pinned to a board", "Did you notice this?"),
    ("announce", "verb", "/əˈnaʊns/", "topic_school_communication", "a principal making an announcement over a microphone", "She announced the news."),
    ("policy", "noun", "/ˈpɒl.ɪ.si/", "topic_school_communication", "a printed school policy document on a table", "Read the policy."),
    ("behaviour", "noun", "/bɪˈheɪ.vjər/", "topic_school_communication", "a student behaving well with good posture in class", "Good behaviour today."),
    ("award", "noun", "/əˈwɔːd/", "topic_school_communication", "a student receiving an award certificate on stage", "She received an award."),
    # topic_market
    ("organic", "adjective", "/ɔːˈɡæn.ɪk/", "topic_market", "organic vegetables with a green organic label", "Buy organic food."),
    ("fresh", "adjective", "/freʃ/", "topic_market", "glistening fresh vegetables at an outdoor market", "The food is fresh."),
    ("expensive", "adjective", "/ɪkˈspen.sɪv/", "topic_market", "a price tag with a high price on a product", "It is too expensive."),
    ("discount", "noun", "/ˈdɪs.kaʊnt/", "topic_market", "a sale sign showing 20 percent discount", "I got a discount."),
    ("vendor", "noun", "/ˈven.dər/", "topic_market", "a smiling market vendor behind a stall of goods", "The vendor helped me."),
    ("stall", "noun", "/stɔːl/", "topic_market", "a colourful market stall with produce on display", "Visit the stall."),
    ("weigh", "verb", "/weɪ/", "topic_market", "a market scale weighing vegetables", "Weigh the vegetables."),
    ("total", "noun", "/ˈtəʊ.təl/", "topic_market", "a receipt showing item prices and a total", "What is the total?"),
    ("receipt", "noun", "/rɪˈsiːt/", "topic_market", "a printed market receipt with items listed", "Keep the receipt."),
    # topic_restaurant
    ("reservation", "noun", "/ˌrez.əˈveɪ.ʃən/", "topic_restaurant", "a restaurant booking confirmation on a phone screen", "I made a reservation."),
    ("vegetarian", "adjective", "/ˌvedʒ.ɪˈteə.ri.ən/", "topic_restaurant", "a green leaf symbol on a restaurant menu item", "I am vegetarian."),
    ("recommend", "verb", "/ˌrek.əˈmend/", "topic_restaurant", "a waiter pointing to a recommended dish on the menu", "Can you recommend something?"),
    ("portion", "noun", "/ˈpɔː.ʃən/", "topic_restaurant", "a well-plated portion of food on a white plate", "A large portion, please."),
    ("appetiser", "noun", "/ˈæp.ɪ.taɪ.zər/", "topic_restaurant", "small appetiser dishes arranged on a restaurant table", "Order an appetiser."),
    ("dessert", "noun", "/dɪˈzɜːt/", "topic_restaurant", "a dessert of fresh fruit and cream on a plate", "I want dessert."),
    ("ingredient", "noun", "/ɪnˈɡriː.di.ənt/", "topic_restaurant", "fresh cooking ingredients laid out on a kitchen table", "List the ingredients."),
    ("flavour", "noun", "/ˈfleɪ.vər/", "topic_restaurant", "a person tasting food and looking surprised", "What flavour is this?"),
    # topic_travel
    ("journey", "noun", "/ˈdʒɜː.ni/", "topic_travel", "a person with a suitcase at the start of a journey", "It was a long journey."),
    ("destination", "noun", "/ˌdes.tɪˈneɪ.ʃən/", "topic_travel", "a pin on a map marking a destination", "What is your destination?"),
    ("departure", "noun", "/dɪˈpɑː.tʃər/", "topic_travel", "a departures board at an airport terminal", "Check the departure time."),
    ("arrival", "noun", "/əˈraɪ.vəl/", "topic_travel", "an arrivals board at an airport", "Check the arrival time."),
    ("passport", "noun", "/ˈpɑːs.pɔːt/", "topic_travel", "a travel passport and boarding pass on a table", "Show your passport."),
    ("luggage", "noun", "/ˈlʌɡ.ɪdʒ/", "topic_travel", "colourful luggage suitcases on a trolley at airport", "Check your luggage."),
    ("platform", "noun", "/ˈplæt.fɔːm/", "topic_travel", "a train platform with passengers waiting", "Go to platform 3."),
    ("delay", "noun", "/dɪˈleɪ/", "topic_travel", "a departure board showing a flight delay notification", "There is a delay."),
    ("transfer", "noun", "/ˈtræns.fɜːr/", "topic_travel", "a passenger transferring between buses at a stop", "Do you need a transfer?"),
    # topic_phone
    ("urgent", "adjective", "/ˈɜː.dʒənt/", "topic_phone", "a phone flashing with an urgent message notification", "It is urgent."),
    ("callback", "noun", "/ˈkɔːl.bæk/", "topic_phone", "a phone with a callback request on the screen", "I need a callback."),
    ("confirm", "verb", "/kənˈfɜːm/", "topic_phone", "a person confirming a phone meeting by nodding", "Please confirm by phone."),
    ("interrupt", "verb", "/ˌɪn.təˈrʌpt/", "topic_phone", "a person accidentally interrupting another's phone call", "Do not interrupt."),
    ("extension", "noun", "/ɪkˈsten.ʃən/", "topic_phone", "an office phone with extension number buttons", "What is the extension?"),
    ("polite", "adjective", "/pəˈlaɪt/", "topic_phone", "a person speaking politely on the phone smiling", "Be polite on the phone."),
    # topic_health
    ("prescription", "noun", "/prɪˈskrɪp.ʃən/", "topic_health", "a doctor handing a prescription slip to a patient", "Take the prescription."),
    ("symptom", "noun", "/ˈsɪmp.təm/", "topic_health", "a medical chart showing common cold symptoms", "Describe the symptom."),
    ("clinic", "noun", "/ˈklɪn.ɪk/", "topic_health", "a small medical clinic with a green cross sign", "Go to the clinic."),
    ("appointment", "noun", "/əˈpɔɪnt.mənt/", "topic_health", "a medical diary with an appointment time circled", "Make an appointment."),
    ("recover", "verb", "/rɪˈkʌv.ər/", "topic_health", "a smiling patient recovering in a hospital bed", "She recovered quickly."),
    ("prevent", "verb", "/prɪˈvent/", "topic_health", "a vaccine injection preventing illness", "Prevent the illness."),
    ("treatment", "noun", "/ˈtriːt.mənt/", "topic_health", "a nurse explaining a treatment plan to a patient", "Start the treatment."),
    ("injury", "noun", "/ˈɪn.dʒər.i/", "topic_health", "a bandaged ankle showing a sports injury", "He has an injury."),
    # topic_social
    ("invitation", "noun", "/ˌɪn.vɪˈteɪ.ʃən/", "topic_social", "a colourful party invitation card on a table", "I sent an invitation."),
    ("garden", "noun", "/ˈɡɑː.dən/", "topic_social", "a colourful garden with flowers and a bench", "I love gardening."),
    ("cooking", "noun", "/ˈkʊk.ɪŋ/", "topic_social", "a person cooking in a bright kitchen", "Cooking is my hobby."),
    ("reading", "noun", "/ˈriː.dɪŋ/", "topic_social", "a person reading a book in a cosy chair", "I enjoy reading."),
    ("hiking", "noun", "/ˈhaɪ.kɪŋ/", "topic_social", "two hikers walking up a green mountain path", "I love hiking."),
    ("opinion", "noun", "/əˈpɪn.jən/", "topic_social", "two people in a friendly discussion sharing opinions", "Share your opinion."),
    ("suggestion", "noun", "/səˈdʒes.tʃən/", "topic_social", "a lightbulb above a person making a suggestion", "A good suggestion!"),
    ("meeting", "noun", "/ˈmiː.tɪŋ/", "topic_social", "friends meeting at a coffee shop", "Nice meeting you."),
    ("introduce", "verb", "/ˌɪn.trəˈdjuːs/", "topic_social", "a person introducing two friends to each other", "Let me introduce you."),
    ("describe", "verb", "/dɪˈskraɪb/", "topic_social", "a person gesturing while describing something", "Describe your hobby."),
    ("prefer", "verb", "/prɪˈfɜːr/", "topic_social", "a person choosing between two activities", "I prefer reading."),
    ("enjoy", "verb", "/ɪnˈdʒɔɪ/", "topic_social", "a happy person enjoying a weekend activity outdoors", "I enjoy teaching."),
    ("share", "verb", "/ʃeər/", "topic_social", "two people sharing an umbrella in the rain", "Share your idea."),
],

# ═══════════════════════════════════════════════════════════════════════════
# KET — B1 vocabulary (professional, academic, nuanced)
# ═══════════════════════════════════════════════════════════════════════════
"ket": [
    # topic_before_class
    ("coordination", "noun", "/kəʊˌɔː.dɪˈneɪ.ʃən/", "topic_before_class", "a group coordinating tasks at a whiteboard", "Good coordination today."),
    ("preparation", "noun", "/ˌprep.ərˈeɪ.ʃən/", "topic_before_class", "a teacher thoroughly preparing lesson materials", "Preparation is key."),
    ("collaboration", "noun", "/kəˌlæb.əˈreɪ.ʃən/", "topic_before_class", "two teachers collaborating over a lesson plan", "She values collaboration."),
    ("implement", "verb", "/ˈɪm.plɪ.ment/", "topic_before_class", "a teacher implementing a new lesson plan strategy", "Implement the plan."),
    ("adapt", "verb", "/əˈdæpt/", "topic_before_class", "a teacher adapting materials for different students", "Adapt the lesson."),
    ("modify", "verb", "/ˈmɒd.ɪ.faɪ/", "topic_before_class", "a teacher modifying a lesson plan at their desk", "Modify the schedule."),
    ("allocate", "verb", "/ˈæl.ə.keɪt/", "topic_before_class", "a timetable showing time allocated per subject", "Allocate time for this."),
    ("efficient", "adjective", "/ɪˈfɪʃ.ənt/", "topic_before_class", "a clock and ticked checklist showing efficiency", "Be more efficient."),
    ("professional", "adjective", "/prəˈfeʃ.ən.əl/", "topic_before_class", "a teacher in professional attire greeting a parent", "Act professional."),
    # topic_in_class
    ("engagement", "noun", "/ɪnˈɡeɪdʒ.mənt/", "topic_in_class", "students eagerly engaged in a classroom discussion", "High student engagement."),
    ("interaction", "noun", "/ˌɪn.tərˈæk.ʃən/", "topic_in_class", "students interacting in pairs during a language task", "Good interaction!"),
    ("participate", "verb", "/pɑːˈtɪs.ɪ.peɪt/", "topic_in_class", "a student raising their hand to participate", "Please participate."),
    ("contribute", "verb", "/kənˈtrɪb.juːt/", "topic_in_class", "a student contributing an idea to a group discussion", "Contribute your idea."),
    ("demonstrate", "verb", "/ˈdem.ən.streɪt/", "topic_in_class", "a teacher demonstrating a task on the board", "Demonstrate the step."),
    ("develop", "verb", "/dɪˈvel.əp/", "topic_in_class", "a student's skills visibly developing over time chart", "Develop your skills."),
    ("strategy", "noun", "/ˈstræt.ɪ.dʒi/", "topic_in_class", "a diagram showing a learning strategy map", "Use a good strategy."),
    ("approach", "noun", "/əˈprəʊtʃ/", "topic_in_class", "a teacher using a student-centred approach", "Try a new approach."),
    ("outcome", "noun", "/ˈaʊt.kʌm/", "topic_in_class", "a checklist of learning outcomes on a board", "Check the outcome."),
    ("objective", "noun", "/əbˈdʒek.tɪv/", "topic_in_class", "lesson objectives written on a whiteboard", "State the objective."),
    # topic_giving_instructions
    ("requirement", "noun", "/rɪˈkwaɪər.mənt/", "topic_giving_instructions", "a requirements list for a classroom task", "Read the requirements."),
    ("clarify", "verb", "/ˈklær.ɪ.faɪ/", "topic_giving_instructions", "a teacher clarifying an instruction to a student", "Please clarify this."),
    ("emphasise", "verb", "/ˈem.fə.saɪz/", "topic_giving_instructions", "a teacher underlining a key instruction on the board", "Emphasise the rules."),
    ("priority", "noun", "/praɪˈɒr.ɪ.ti/", "topic_giving_instructions", "a numbered priority list on a whiteboard", "Set the priority."),
    ("deadline", "noun", "/ˈded.laɪn/", "topic_giving_instructions", "a calendar with a deadline circled in red", "The deadline is Friday."),
    ("submission", "noun", "/səbˈmɪʃ.ən/", "topic_giving_instructions", "a student handing in a completed submission folder", "Submit by the deadline."),
    # topic_checking_understanding
    ("analyse", "verb", "/ˈæn.ə.laɪz/", "topic_checking_understanding", "a person carefully analysing a text with a highlighter", "Analyse the results."),
    ("summarise", "verb", "/ˈsʌm.ər.aɪz/", "topic_checking_understanding", "a student writing a short summary of a passage", "Summarise the text."),
    ("interpret", "verb", "/ɪnˈtɜː.prɪt/", "topic_checking_understanding", "a person interpreting a graph or data chart", "Interpret the data."),
    ("identify", "verb", "/aɪˈden.tɪ.faɪ/", "topic_checking_understanding", "a student identifying the correct answer on a sheet", "Identify the mistake."),
    ("comprehend", "verb", "/ˌkɒm.prɪˈhend/", "topic_checking_understanding", "a student nodding after comprehending a text", "Can you comprehend this?"),
    ("retention", "noun", "/rɪˈten.ʃən/", "topic_checking_understanding", "a brain with a memory retention symbol", "Improve retention."),
    # topic_praise_correction
    ("constructive", "adjective", "/kənˈstrʌk.tɪv/", "topic_praise_correction", "a teacher giving constructive written feedback", "Give constructive feedback."),
    ("substantial", "adjective", "/səbˈstæn.ʃəl/", "topic_praise_correction", "a student's substantial amount of work on a desk", "Substantial improvement!"),
    ("consistent", "adjective", "/kənˈsɪs.tənt/", "topic_praise_correction", "a student consistently getting good marks over time", "Be consistent."),
    ("particular", "adjective", "/pəˈtɪk.jʊ.lər/", "topic_praise_correction", "a teacher highlighting a particular area to improve", "Improve this particular part."),
    ("recognise", "verb", "/ˈrek.əɡ.naɪz/", "topic_praise_correction", "a teacher recognising excellent student work", "Recognise good effort."),
    # topic_school_communication
    ("documentation", "noun", "/ˌdɒk.jʊ.menˈteɪ.ʃən/", "topic_school_communication", "a stack of official school documentation", "Complete the documentation."),
    ("administration", "noun", "/ədˌmɪn.ɪˈstreɪ.ʃən/", "topic_school_communication", "a school administration office with staff inside", "Contact administration."),
    ("committee", "noun", "/kəˈmɪt.i/", "topic_school_communication", "a school committee meeting around a conference table", "Join the committee."),
    ("resolution", "noun", "/ˌrez.əˈluː.ʃən/", "topic_school_communication", "two parties reaching a resolution with handshake", "Find a resolution."),
    ("negotiate", "verb", "/nɪˈɡəʊ.ʃi.eɪt/", "topic_school_communication", "two people negotiating terms at a meeting table", "Negotiate the terms."),
    ("represent", "verb", "/ˌrep.rɪˈzent/", "topic_school_communication", "a person representing the school at an event", "She represents the school."),
    # topic_market
    ("negotiate", "verb", "/nɪˈɡəʊ.ʃi.eɪt/", "topic_market", "a buyer and seller negotiating a price at a stall", "Negotiate the price."),
    ("inflation", "noun", "/ɪnˈfleɪ.ʃən/", "topic_market", "a rising price chart showing inflation", "Prices rose with inflation."),
    ("affordable", "adjective", "/əˈfɔː.də.bəl/", "topic_market", "a market stall with reasonable low prices", "It is affordable."),
    ("compare", "verb", "/kəmˈpeər/", "topic_market", "a person comparing prices at two market stalls", "Compare the prices."),
    ("transaction", "noun", "/trænˈzæk.ʃən/", "topic_market", "a market transaction with cash being exchanged", "Complete the transaction."),
    ("bargain", "verb", "/ˈbɑː.ɡɪn/", "topic_market", "a buyer bargaining at a market stall", "Bargain for a lower price."),
    ("purchase", "verb", "/ˈpɜː.tʃəs/", "topic_market", "a person purchasing goods at a market counter", "I purchased vegetables."),
    # topic_restaurant
    ("dietary", "adjective", "/ˈdaɪ.ə.tri/", "topic_restaurant", "a menu with dietary restriction labels", "Any dietary needs?"),
    ("allergy", "noun", "/ˈæl.ər.dʒi/", "topic_restaurant", "a restaurant menu with allergy warning symbols", "I have an allergy."),
    ("gluten", "noun", "/ˈɡluː.tən/", "topic_restaurant", "a gluten-free label on a restaurant menu item", "Is it gluten-free?"),
    ("vegan", "adjective", "/ˈviː.ɡən/", "topic_restaurant", "a green vegan symbol on a restaurant menu", "Is there a vegan option?"),
    ("cuisine", "noun", "/kwɪˈziːn/", "topic_restaurant", "a variety of dishes representing Vietnamese cuisine", "I love Vietnamese cuisine."),
    ("atmosphere", "noun", "/ˈæt.mə.sfɪər/", "topic_restaurant", "a warm cosy restaurant with soft lighting", "The atmosphere is nice."),
    ("satisfaction", "noun", "/ˌsæt.ɪsˈfæk.ʃən/", "topic_restaurant", "a happy customer leaving a restaurant with satisfaction", "Customer satisfaction is key."),
    # topic_travel
    ("itinerary", "noun", "/aɪˈtɪn.ər.ər.i/", "topic_travel", "a printed travel itinerary with dates and places", "Plan the itinerary."),
    ("accommodation", "noun", "/əˌkɒm.əˈdeɪ.ʃən/", "topic_travel", "a comfortable hotel room with a view", "Book accommodation."),
    ("immigration", "noun", "/ˌɪm.ɪˈɡreɪ.ʃən/", "topic_travel", "an immigration desk at an international airport", "Go through immigration."),
    ("currency", "noun", "/ˈkʌr.ən.si/", "topic_travel", "various international currency notes spread out", "Exchange the currency."),
    ("customs", "noun", "/ˈkʌs.təmz/", "topic_travel", "a customs inspection desk at an airport", "Declare at customs."),
    ("transit", "noun", "/ˈtræn.zɪt/", "topic_travel", "a transit area in a modern airport terminal", "We are in transit."),
    ("confirmation", "noun", "/ˌkɒn.fəˈmeɪ.ʃən/", "topic_travel", "a booking confirmation email on a phone screen", "Get a confirmation."),
    # topic_phone
    ("professional", "adjective", "/prəˈfeʃ.ən.əl/", "topic_phone", "a professional person making a business phone call", "Sound professional."),
    ("tone", "noun", "/təʊn/", "topic_phone", "a sound wave icon representing tone of voice", "Use a polite tone."),
    ("voicemail", "noun", "/ˈvɔɪs.meɪl/", "topic_phone", "a phone showing a voicemail notification", "Leave a voicemail."),
    ("switchboard", "noun", "/ˈswɪtʃ.bɔːd/", "topic_phone", "a telephone switchboard in an office", "Transfer to the switchboard."),
    ("enquiry", "noun", "/ɪnˈkwaɪər.i/", "topic_phone", "a person making an enquiry on the phone", "Make an enquiry."),
    # topic_health
    ("diagnosis", "noun", "/ˌdaɪ.əɡˈnəʊ.sɪs/", "topic_health", "a doctor making a diagnosis after examining a patient", "Wait for the diagnosis."),
    ("chronic", "adjective", "/ˈkrɒn.ɪk/", "topic_health", "a patient at a long-term chronic care clinic", "It is a chronic condition."),
    ("emergency", "noun", "/ɪˈmɜː.dʒən.si/", "topic_health", "an ambulance rushing to a hospital emergency entrance", "This is an emergency."),
    ("surgery", "noun", "/ˈsɜː.dʒər.i/", "topic_health", "a doctor performing surgery in an operating theatre", "She had surgery."),
    ("vaccination", "noun", "/ˌvæk.sɪˈneɪ.ʃən/", "topic_health", "a nurse giving a vaccination injection to a patient", "Get a vaccination."),
    ("specialist", "noun", "/ˈspeʃ.əl.ɪst/", "topic_health", "a medical specialist reviewing a patient's records", "See a specialist."),
    # topic_social
    ("perspective", "noun", "/pəˈspek.tɪv/", "topic_social", "two people looking at the same thing from different angles", "Share your perspective."),
    ("community", "noun", "/kəˈmjuː.nɪ.ti/", "topic_social", "a diverse community of people working together", "Help the community."),
    ("relationship", "noun", "/rɪˈleɪ.ʃən.ʃɪp/", "topic_social", "two colleagues smiling and shaking hands", "Build a relationship."),
    ("network", "noun", "/ˈnet.wɜːk/", "topic_social", "a diagram of connected people representing a network", "Expand your network."),
    ("impression", "noun", "/ɪmˈpreʃ.ən/", "topic_social", "a person making a great first impression at a meeting", "Make a good impression."),
    ("voluntary", "adjective", "/ˈvɒl.ən.tri/", "topic_social", "volunteers working together at a community event", "It is voluntary."),
    ("culture", "noun", "/ˈkʌl.tʃər/", "topic_social", "people from different cultures celebrating together", "Respect the culture."),
    ("tradition", "noun", "/trəˈdɪʃ.ən/", "topic_social", "a traditional Vietnamese festival with lanterns", "A lovely tradition."),
],

# ═══════════════════════════════════════════════════════════════════════════
# PET — B2 vocabulary (sophisticated, nuanced, professional)
# ═══════════════════════════════════════════════════════════════════════════
"pet": [
    # topic_before_class
    ("methodology", "noun", "/ˌmeθ.əˈdɒl.ə.dʒi/", "topic_before_class", "a textbook open to a teaching methodology chapter", "Study the methodology."),
    ("curriculum", "noun", "/kəˈrɪk.jʊ.ləm/", "topic_before_class", "a structured curriculum document on a teacher's desk", "Review the curriculum."),
    ("objective", "noun", "/əbˈdʒek.tɪv/", "topic_before_class", "lesson objectives neatly listed on a classroom board", "State the objectives."),
    ("assessment", "noun", "/əˈses.mənt/", "topic_before_class", "a teacher assessing student work against criteria", "Prepare the assessment."),
    ("autonomy", "noun", "/ɔːˈtɒn.ə.mi/", "topic_before_class", "a self-directed learner working independently", "Encourage autonomy."),
    ("scaffolding", "noun", "/ˈskæf.əl.dɪŋ/", "topic_before_class", "a teacher providing a scaffolded writing template", "Use scaffolding."),
    ("differentiation", "noun", "/ˌdɪf.ər.en.ʃiˈeɪ.ʃən/", "topic_before_class", "different task levels provided for students", "Apply differentiation."),
    ("syllabus", "noun", "/ˈsɪl.ə.bəs/", "topic_before_class", "a printed syllabus for an English course", "Read the syllabus."),
    # topic_in_class
    ("critical", "adjective", "/ˈkrɪt.ɪ.kəl/", "topic_in_class", "a student thinking critically while reading a text", "Think critically."),
    ("analytical", "adjective", "/ˌæn.əˈlɪt.ɪ.kəl/", "topic_in_class", "a person solving an analytical problem on a board", "Use analytical skills."),
    ("coherent", "adjective", "/kəʊˈhɪər.ənt/", "topic_in_class", "a well-organised essay with clear paragraph structure", "Be coherent."),
    ("elaborate", "verb", "/ɪˈlæb.ər.eɪt/", "topic_in_class", "a student adding detail to a short written answer", "Please elaborate."),
    ("paraphrase", "verb", "/ˈpær.ə.freɪz/", "topic_in_class", "two versions of the same sentence in different words", "Paraphrase the sentence."),
    ("infer", "verb", "/ɪnˈfɜːr/", "topic_in_class", "a student inferring meaning from context clues", "Infer the meaning."),
    ("deduce", "verb", "/dɪˈdjuːs/", "topic_in_class", "a person deducing an answer from clues", "Deduce the answer."),
    ("hypothesis", "noun", "/haɪˈpɒθ.ɪ.sɪs/", "topic_in_class", "a hypothesis written on a whiteboard for testing", "Form a hypothesis."),
    # topic_giving_instructions
    ("constraint", "noun", "/kənˈstreɪnt/", "topic_giving_instructions", "a list of constraints next to a task description", "Note the constraints."),
    ("criteria", "noun", "/kraɪˈtɪər.i.ə/", "topic_giving_instructions", "an assessment criteria rubric for a task", "Follow the criteria."),
    ("specification", "noun", "/ˌspes.ɪ.fɪˈkeɪ.ʃən/", "topic_giving_instructions", "a technical specification document on a desk", "Read the specification."),
    ("comply", "verb", "/kəmˈplaɪ/", "topic_giving_instructions", "a student complying with classroom regulations", "Comply with the rules."),
    ("adhere", "verb", "/ədˈhɪər/", "topic_giving_instructions", "a person adhering to a strict set of guidelines", "Adhere to guidelines."),
    # topic_checking_understanding
    ("reflection", "noun", "/rɪˈflek.ʃən/", "topic_checking_understanding", "a student writing a reflective journal entry", "Write a reflection."),
    ("evaluation", "noun", "/ɪˌvæl.jʊˈeɪ.ʃən/", "topic_checking_understanding", "a teacher conducting a lesson evaluation form", "Complete the evaluation."),
    ("implication", "noun", "/ˌɪm.plɪˈkeɪ.ʃən/", "topic_checking_understanding", "a diagram showing implications flowing from a decision", "Consider the implications."),
    ("insight", "noun", "/ˈɪn.saɪt/", "topic_checking_understanding", "a lightbulb moment with a creative thought bubble", "Share your insight."),
    ("nuance", "noun", "/ˈnjuː.ɑːns/", "topic_checking_understanding", "two similar words with subtle differences highlighted", "Notice the nuance."),
    # topic_praise_correction
    ("acknowledgement", "noun", "/əkˈnɒl.ɪdʒ.mənt/", "topic_praise_correction", "a teacher acknowledging a student's contribution", "Give acknowledgement."),
    ("exemplary", "adjective", "/ɪɡˈzem.plər.i/", "topic_praise_correction", "a student's exemplary work displayed on the wall", "Exemplary effort!"),
    ("critique", "noun", "/krɪˈtiːk/", "topic_praise_correction", "a written critique with detailed comments in red ink", "Write a critique."),
    ("rephrase", "verb", "/ˌriːˈfreɪz/", "topic_praise_correction", "a teacher suggesting a better way to phrase a sentence", "Please rephrase this."),
    ("misconception", "noun", "/ˌmɪs.kənˈsep.ʃən/", "topic_praise_correction", "a student realising a misconception while studying", "Address the misconception."),
    # topic_school_communication
    ("mediation", "noun", "/ˌmiː.diˈeɪ.ʃən/", "topic_school_communication", "a mediator helping two parties reach an agreement", "Use mediation."),
    ("protocol", "noun", "/ˈprəʊ.tə.kɒl/", "topic_school_communication", "a school communication protocol document", "Follow the protocol."),
    ("stakeholder", "noun", "/ˈsteɪk.həʊl.dər/", "topic_school_communication", "parents and teachers as school stakeholders in a meeting", "Involve the stakeholders."),
    ("transparency", "noun", "/trænsˈpær.ən.si/", "topic_school_communication", "open communication represented by a clear glass barrier", "Maintain transparency."),
    ("accountability", "noun", "/əˌkaʊn.təˈbɪl.ɪ.ti/", "topic_school_communication", "a teacher accountable for their students' progress", "Show accountability."),
    ("formal", "adjective", "/ˈfɔː.məl/", "topic_school_communication", "a formal letter on headed school paper", "Write a formal letter."),
    # topic_market
    ("fluctuation", "noun", "/ˌflʌk.tʃuˈeɪ.ʃən/", "topic_market", "a price chart showing price fluctuations over time", "Note the fluctuation."),
    ("commodity", "noun", "/kəˈmɒd.ɪ.ti/", "topic_market", "a range of basic food commodities at a market", "Buy basic commodities."),
    ("surplus", "noun", "/ˈsɜː.pləs/", "topic_market", "a market stall with an excess surplus of produce", "There is a surplus."),
    ("shortage", "noun", "/ˈʃɔː.tɪdʒ/", "topic_market", "an empty market shelf showing a shortage", "There is a shortage."),
    ("wholesale", "adjective", "/ˈhəʊl.seɪl/", "topic_market", "large boxes of wholesale goods in a warehouse", "Buy at wholesale price."),
    # topic_restaurant
    ("ambiance", "noun", "/ˈæm.bi.ɑːns/", "topic_restaurant", "a beautifully lit restaurant with warm ambiance", "I love the ambiance."),
    ("complimentary", "adjective", "/ˌkɒm.plɪˈmen.tri/", "topic_restaurant", "a waiter bringing a complimentary drink to a table", "It is complimentary."),
    ("fusion", "noun", "/ˈfjuː.ʒən/", "topic_restaurant", "a fusion dish blending two cultural food styles", "Try the fusion menu."),
    ("sommelier", "noun", "/ˈsɒm.əl.jeɪ/", "topic_restaurant", "a sommelier presenting a wine bottle at the table", "Ask the sommelier."),
    ("patron", "noun", "/ˈpeɪ.trən/", "topic_restaurant", "regular patrons enjoying dinner at a favourite restaurant", "A loyal patron."),
    # topic_travel
    ("expedition", "noun", "/ˌek.spɪˈdɪʃ.ən/", "topic_travel", "a group on an expedition through a mountain landscape", "Plan the expedition."),
    ("excursion", "noun", "/ɪkˈskɜː.ʒən/", "topic_travel", "a school excursion group on a coach bus", "Join the excursion."),
    ("itinerary", "noun", "/aɪˈtɪn.ər.ər.i/", "topic_travel", "a detailed travel itinerary in a leather planner", "Follow the itinerary."),
    ("visa", "noun", "/ˈviː.zə/", "topic_travel", "a passport open to a page with a visa stamp", "Apply for a visa."),
    ("disruption", "noun", "/dɪsˈrʌp.ʃən/", "topic_travel", "a travel disruption sign at an airport departure gate", "Report the disruption."),
    ("embark", "verb", "/ɪmˈbɑːk/", "topic_travel", "passengers embarking on a cruise ship", "We will embark soon."),
    # topic_phone
    ("correspondence", "noun", "/ˌkɒr.ɪˈspɒn.dəns/", "topic_phone", "a series of email or written correspondence messages", "Review the correspondence."),
    ("grievance", "noun", "/ˈɡriː.vəns/", "topic_phone", "a person filing a grievance formally at a desk", "Address the grievance."),
    ("resolution", "noun", "/ˌrez.əˈluː.ʃən/", "topic_phone", "two parties reaching a phone call resolution", "Find a resolution."),
    ("concise", "adjective", "/kənˈsaɪs/", "topic_phone", "a short concise message on a phone screen", "Be concise."),
    ("articulate", "verb", "/ɑːˈtɪk.jʊ.leɪt/", "topic_phone", "a person speaking articulately and clearly", "Articulate clearly."),
    # topic_health
    ("rehabilitation", "noun", "/ˌriː.həˌbɪl.ɪˈteɪ.ʃən/", "topic_health", "a patient undergoing rehabilitation exercises", "Start rehabilitation."),
    ("deteriorate", "verb", "/dɪˈtɪər.i.ər.eɪt/", "topic_health", "a health chart showing a deteriorating condition", "Do not let it deteriorate."),
    ("holistic", "adjective", "/həʊˈlɪs.tɪk/", "topic_health", "a holistic health diagram showing mind body and spirit", "Take a holistic approach."),
    ("chronic", "adjective", "/ˈkrɒn.ɪk/", "topic_health", "a long-term chronic pain patient at a specialist clinic", "It is a chronic issue."),
    ("sedentary", "adjective", "/ˈsed.ən.tri/", "topic_health", "a person sitting at a desk all day with no exercise", "Avoid a sedentary lifestyle."),
    ("nourishment", "noun", "/ˈnʌr.ɪʃ.mənt/", "topic_health", "a balanced meal providing full nourishment", "Get proper nourishment."),
    # topic_social
    ("phenomenon", "noun", "/fɪˈnɒm.ɪ.nɒn/", "topic_social", "a striking natural phenomenon shown in a photo", "An interesting phenomenon."),
    ("discourse", "noun", "/ˈdɪs.kɔːs/", "topic_social", "people engaged in an intellectual discourse at a table", "Join the discourse."),
    ("consensus", "noun", "/kənˈsen.səs/", "topic_social", "a group of people nodding in agreement and consensus", "We reached a consensus."),
    ("empathy", "noun", "/ˈem.pə.θi/", "topic_social", "a person listening compassionately to another person", "Show empathy."),
    ("resilience", "noun", "/rɪˈzɪl.i.əns/", "topic_social", "a person bouncing back from a setback with a smile", "Build resilience."),
    ("initiative", "noun", "/ɪˈnɪʃ.ɪ.tɪv/", "topic_social", "a person taking the initiative to lead a project", "Take initiative."),
    ("articulate", "adjective", "/ɑːˈtɪk.jʊ.lət/", "topic_social", "a confident speaker presenting to an audience", "She is very articulate."),
    ("introspective", "adjective", "/ˌɪn.trəˈspek.tɪv/", "topic_social", "a person in quiet thought and introspection", "Be introspective."),
],
}


def main():
    print("=" * 60)
    print("TinySteps — Vocabulary Top-Up Script")
    print("=" * 60)

    # Load existing words from all levels
    existing: dict[str, list] = {}
    global_seen: set[str] = set()

    for level in LEVELS:
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        data = json.load(open(path, encoding="utf-8"))
        existing[level] = data["words"]
        for w in data["words"]:
            global_seen.add(w["word"].lower())

    print(f"\nExisting words: {sum(len(v) for v in existing.values())}")
    print(f"Global unique: {len(global_seen)}\n")

    # Top up each level
    for level in LEVELS:
        target = TARGETS[level]
        current = len(existing[level])
        gap = target - current

        if gap <= 0:
            print(f"{level}: already at {current}/{target}, skipping.")
            continue

        pool = WORD_BANK.get(level, [])
        added = []

        for entry in pool:
            if len(added) >= gap:
                break
            word, pos, ipa, topic, image_hint, example = entry
            key = word.lower()
            if key in global_seen:
                continue
            # Build the vocab entry
            idx = current + len(added) + 1
            added.append({
                "id":               f"{level}_vocab_{idx:03d}",
                "word":             word,
                "ipa":              ipa,
                "pos":              pos,
                "topic_ids":        [topic],
                "example_sentence": example,
                "image_hint":       image_hint,
                "frequency_rank":   idx,
            })
            global_seen.add(key)

        # Merge and save
        merged = existing[level] + added
        # Renumber sequentially
        for i, w in enumerate(merged, 1):
            w["id"] = f"{level}_vocab_{i:03d}"

        payload = {"level": level, "total_words": len(merged), "words": merged}
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        remaining = max(0, target - len(merged))
        flag = "✓" if remaining == 0 else f"⚠ still need +{remaining}"
        print(f"{level}: +{len(added)} words → {len(merged)}/{target}  {flag}")

    # Update topics.json with new vocab IDs by topic
    print("\nUpdating topics.json vocabulary references...")
    _update_topics_refs()
    print("Done. Run validate_data.py to verify.")


def _update_topics_refs():
    """Add valid vocabulary IDs to topics.json spiral entries by topic."""
    # Build topic → [vocab_id] map from all vocab files
    topic_vocab_map: dict[str, list[str]] = {}
    for level in LEVELS:
        path = os.path.join(VOCAB_DIR, f"{level}.json")
        data = json.load(open(path, encoding="utf-8"))
        for w in data["words"]:
            for tid in w.get("topic_ids", []):
                topic_vocab_map.setdefault(tid, []).append(w["id"])

    topics_data = json.load(open(TOPICS_FILE, encoding="utf-8"))
    for topic in topics_data["topics"]:
        topic_id = topic["id"]
        relevant_ids = topic_vocab_map.get(topic_id, [])
        for spiral_entry in topic.get("spiral", []):
            lvl = spiral_entry.get("level")
            # Only add IDs that belong to this level
            level_ids = [v for v in relevant_ids if v.startswith(lvl)]
            spiral_entry["vocabulary_ids"] = level_ids[:6]  # max 6 per spiral entry

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
