# TinySteps P0 Editorial QA Report

## Scope and evidence

- Sample: **24 representative lessons, 1 lesson per topic**, distributed across Starters (5), Movers (5), Flyers (5), KET (5), PET (4).
- This is a **heuristic + focused editorial scan**, not a full expert review of all 175 lessons.
- No lesson content was changed during this QA pass.

## Structural findings

- Exact scenario duplicates remaining: **0** (previously 40 groups were rewritten).
- Duplicate AI opening groups across corpus: **12**.
- Takeaway count: **173 lessons with 4 lines, 2 with 3 lines**.
- Validation baseline: `validate_data` 0 errors, CEFR audit 0 violations, `prepare-content` pass, Vitest 155/155.

## Priority findings

### P1 — AI opening vẫn clone ở level cao

- `Teacher, can you help me? I don't understand the task` → 11 lessons: flyers_lesson_038, flyers_lesson_014, flyers_lesson_002, flyers_lesson_026, ket_lesson_014, ket_lesson_002, ket_lesson_026, pet_lesson_038, pet_lesson_014, pet_lesson_002, pet_lesson_026
- `Welcome! What would you like to order today?` → 9 lessons: flyers_lesson_020, flyers_lesson_008, flyers_lesson_032, ket_lesson_020, ket_lesson_008, ket_lesson_032, pet_lesson_020, pet_lesson_008, pet_lesson_032
- `Teacher, should we open our books or start writing?` → 11 lessons: flyers_lesson_003, flyers_lesson_039, flyers_lesson_027, flyers_lesson_015, ket_lesson_003, ket_lesson_027, ket_lesson_015, pet_lesson_003, pet_lesson_039, pet_lesson_027, pet_lesson_015
- `Teacher, are we supposed to explain or just write it?` → 11 lessons: flyers_lesson_016, flyers_lesson_004, flyers_lesson_028, flyers_lesson_040, ket_lesson_016, ket_lesson_004, ket_lesson_028, pet_lesson_016, pet_lesson_004, pet_lesson_028, pet_lesson_040
- `Hi! What a nice day. What are your plans for the weekend?` → 8 lessons: flyers_lesson_036, flyers_lesson_012, flyers_lesson_024, ket_lesson_012, ket_lesson_024, pet_lesson_036, pet_lesson_012, pet_lesson_024
- `Hello! This is Minh calling. Can we confirm the schedule?` → 9 lessons: flyers_lesson_034, flyers_lesson_022, flyers_lesson_010, ket_lesson_034, ket_lesson_022, ket_lesson_010, pet_lesson_034, pet_lesson_022, pet_lesson_010
- `Teacher, did I do a good job on my homework?` → 9 lessons: flyers_lesson_005, flyers_lesson_029, flyers_lesson_017, ket_lesson_005, ket_lesson_029, ket_lesson_017, pet_lesson_005, pet_lesson_029, pet_lesson_017
- `Good morning! Have you finished the lesson preparation?` → 11 lessons: flyers_lesson_013, flyers_lesson_037, flyers_lesson_025, flyers_lesson_001, ket_lesson_013, ket_lesson_025, ket_lesson_001, pet_lesson_013, pet_lesson_037, pet_lesson_025, pet_lesson_001

Recommendation: rewrite AI openings by level/topic before calling this layer editorially complete.

### P1 — Takeaway auto-extraction cần human curation

- Heuristic flags do not mean every greeting/question is wrong; they identify lines needing context judgment.
- In the 24-sample, several takeaways are dialogue replies or greetings rather than teacher-ready lines (for example starters lesson 001, 004, 006; movers lesson 002; pet lesson 005).
- Do not enforce “only imperatives”; functional questions and polite parent communication can also be valid takeaways.

### P1 — Scenario ↔ dialogue alignment

- Some scenarios describe a specific situation while the dialogue starts from a broader or different moment. This is a content coherence risk, not a schema error.
- Highest-risk examples should be reviewed together with the full dialogue, not only line 0.

## Sample matrix

| Lesson | Level | Topic | Flags | Scenario | Dialogue opening | Takeaway | AI opening |
|---|---|---|---|---|---|---|---|
| `starters_lesson_001` | starters | topic_before_class | P1:weak_takeaway | Monday morning. You open the classroom door and start the lesson. | good morning, class. | Good morning, class. / Sit down, please. / Open your book. / Look at the board. | Good morning, teacher! What do we do first? |
| `flyers_lesson_001` | flyers | topic_before_class | P1:weak_takeaway | Before period one, you prepare materials and check the timetable with a colleague. | good morning. i want to check the school schedule before class. | Good morning. I want to check the school schedule before class. / Sure. The principal updated the timetable this morning. / We should inform the other teachers about the change. / I have already sent them an email with the new details. | Good morning! Have you finished the lesson preparation? |
| `movers_lesson_002` | movers | topic_in_class | P1:weak_takeaway | Period two starts. You check books and ask a student to read aloud. | did you bring your book today? | I am reading it now. / Good. Open it to page twelve. / Excellent. Very good progress! / Yes, teacher. Here is my book. | Teacher, which page should I open? |
| `ket_lesson_002` | ket | topic_in_class | — | Beginning the lesson, you introduce classroom communication topics to students. | today we are going to discuss classroom communication. | Today we are going to discuss classroom communication. / I think now about ways to improve my speaking. / That is great. You should also focus on listening carefully. / Could you recommend some practice activities? | Teacher, can you help me? I don't understand the task |
| `flyers_lesson_003` | flyers | topic_giving_instructions | P1:weak_takeaway | You explain the next activity and make sure students know each step. | you must follow the instructions carefully during the test. | You must follow the instructions carefully during the test. / Understood, teacher. Should we write our names on the paper? / Yes, write your full name at the top of the page. / Can we use a dictionary for the reading section? | Teacher, should we open our books or start writing? |
| `pet_lesson_003` | pet | topic_giving_instructions | P1:weak_takeaway | Administering a test, you emphasize following instructions and test policies. | you must follow the instructions carefully during the test. | You must follow the instructions carefully during the test. / Understood, teacher. Should we write our names on the paper? / Yes, write your full name at the top of the page. / Could we use a dictionary for the reading section? | Teacher, should we open our books or start writing? |
| `ket_lesson_004` | ket | topic_checking_understanding | — | You pause the listening session to confirm students followed the recording. | let's check if everyone understood the listening exercise. | Let's check if everyone understood the listening exercise. / I followed the main idea, but missed some details. / That is fine for now. What was the main topic? / The speakers were discussing a school event. | Teacher, are we supposed to explain or just write it? |
| `starters_lesson_004` | starters | topic_checking_understanding | P1:weak_takeaway | The class looks confused after your question. You check if they understand. | listen to me. look at the board. | Listen to me. Look at the board. / Yes! He is a very good student. / Yes, teacher. We look. / Is this a good student? | Teacher, do we look at the board now? |
| `pet_lesson_005` | pet | topic_praise_correction | P1:weak_takeaway | A student answers well. You praise the work and help with one minor mistake. | you have made excellent progress in your writing this month. | You have made excellent progress in your writing this month. / Thank you. I practised a lot during the weekend. / Your paragraph structure is clear and logical. / However, I think I used the wrong tense in one sentence. | Teacher, did I do a good job on my homework? |
| `movers_lesson_005` | movers | topic_praise_correction | — | A student answers well. You praise the work and help with one small mistake. | that is a great answer, lan! | You did a great job on your homework. / That is a great answer, Lan! / It is okay. Mistakes help us learn. / I made one small mistake, I think. | Teacher, did I do better on my homework today? |
| `starters_lesson_006` | starters | topic_school_communication | P1:weak_takeaway | After school, you meet a parent at the gate and greet them politely. | hello! i am ms. lan. i am nam's teacher. | I am Nam's teacher. / Nice to meet you. / Thank you for coming today. / Let's talk about your child. | Hello, teacher. How is Nam in class? |
| `flyers_lesson_006` | flyers | topic_school_communication | P1:weak_takeaway | In a short parent meeting, you share an update about the student. | i want to discuss the feedback from last week's parent meeting. | I want to discuss the feedback from last week's parent meeting. / Yes, several parents raised concerns about homework volume. / I understand. We should adjust our policy accordingly. / I drafted a new homework schedule for your review. | Hello, teacher. I wanted to ask about my child's progress |
| `movers_lesson_007` | movers | topic_market | — | You go to the market after school and buy fruit for your family. | i want to buy some fruit, please. | I want to buy some fruit, please. / The fruit is very fresh. I bought it this morning. / Okay, I will buy two kilos. / It is thirty thousand dong per kilo. | Excuse me. How much are these apples? |
| `ket_lesson_007` | ket | topic_market | — | You ask a seller at the market for item prices before buying. | could i see the price list for these items, please? | Could I see the price list for these items, please? / Of course. Here is today's price list. / The price for organic vegetables is quite high. / I apologise, but the quality is excellent. | Fresh vegetables here! Would you like to buy some? |
| `flyers_lesson_008` | flyers | topic_restaurant | — | Finishing your meal at a restaurant, you ask the server for the bill. | good afternoon. can we have the bill, please? | Good afternoon. Can we have the bill, please? / Of course. is everything satisfactory today? / The food was excellent, but the service was a bit slow. / I apologise for that. We were very busy this evening. | Welcome! What would you like to order today? |
| `pet_lesson_008` | pet | topic_restaurant | — | After dining with colleagues, you request the check and review payment. | good afternoon. could we have the bill, please? | Good afternoon. Could we have the bill, please? / Of course. Was everything satisfactory today? / The food was excellent, but the service was a bit slow. / I apologise for that. We were very busy this evening. | Welcome! What would you like to order today? |
| `ket_lesson_009` | ket | topic_travel | — | At a ticket window, you ask to purchase a train ticket to Hue. | i would like to buy a train ticket to hue, please. | I would like to buy a train ticket to Hue, please. / Certainly. When would you like to travel? / This Saturday morning, if possible. / There is a train at eight thirty that arrives at noon. | Hello! Where are you traveling to today? |
| `starters_lesson_009` | starters | topic_travel | P1:weak_takeaway | You ask for directions because you want to go to the market. | hello! i want to go to the market. | Hello! I want to go to the market. / The market is very near here. / Have a good trip. Goodbye! / Thank you! I go there every morning. | Excuse me. Where is the market? |
| `pet_lesson_010` | pet | topic_phone | P1:weak_takeaway | Calling another department, you report a delay and confirm next steps. | i am calling to apologise for the delay in sending the report. | I am calling to apologise for the delay in sending the report. / No problem. I understand you were very busy last week. / I will submit the completed report by tomorrow morning. / Thank you. Could you also send a digital copy by email? | Hello! This is Minh calling. Can we confirm the schedule? |
| `movers_lesson_010` | movers | topic_phone | P1:weak_takeaway | You call a parent to confirm a school meeting time. | hello, this is mr. minh. can i speak to the principal? | Please tell her to call me about Friday's meeting. / Sorry, the principal is busy right now. / I will pass on the message. Goodbye! / Hello, this is Mr. Minh. Can I speak to the principal? | Hello, this is Ms. Lan. Can we confirm the meeting? |
| `starters_lesson_011` | starters | topic_health | P1:weak_takeaway | You feel bad today. You visit the doctor and say your symptoms. | hello, doctor! i feel bad today. | I am not fine. I have a headache. / Hello, doctor! I feel bad today. / Take this medicine and rest at home. / Hello! How are you? | Hello, doctor. I feel bad today. |
| `flyers_lesson_011` | flyers | topic_health | P1:weak_takeaway | At the clinic, you explain symptoms and ask what to do next. | good morning. i have a terrible headache and a high fever. | Good morning. I have a terrible headache and a high fever. / I am sorry to hear that. How long have you had these symptoms? / The fever started two days ago and has not improved. / I see. I will write a prescription for you. | Hello. Please sit down. What are your symptoms today? |
| `movers_lesson_012` | movers | topic_social | P1:weak_takeaway | You meet a colleague after class and talk about weekend plans. | hello! how was your weekend? | Good idea! Let's meet for a walk next Saturday. / Yes! I also helped my mother clean the house. / That is wonderful. The weather was very nice on Sunday. / It was great! I went to the park with my family. | Hi! What are your plans for the weekend? |
| `ket_lesson_012` | ket | topic_social | P1:weak_takeaway | Leaving the classroom, you ask a fellow teacher about their upcoming weekend. | what a lovely afternoon! how have you been lately? | What a lovely afternoon! How have you been lately? / Very well, thank you. I have been quite busy with school. / I understand. I work now on a new project. / What kind of project? It sounds interesting. | Hi! What a nice day. What are your plans for the weekend? |

## Recommended remediation order

1. Rewrite duplicate/meta AI openings in Flyers/KET/PET; no audio impact.
2. Human-curate takeaway lines, starting with flagged Starters/Movers and then level high.
3. Review scenario↔dialogue coherence and rewrite only mismatched cases.
4. Only then start C2 dialogue rewrite + audio regeneration in batches of 5–10 lessons.

## Status

**Schema v2 and structural validation complete. Editorial QA is not complete; P1 AI opening uniqueness, takeaway curation, and context coherence remain.**
