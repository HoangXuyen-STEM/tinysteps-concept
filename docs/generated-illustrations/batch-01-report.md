# Batch 01 Report — Starters

Retroactively reconciled 2026-07-14 after fixing a key-collision bug (see prompt-pack
doc): originally-generated assets used the bare lesson filename number
(`match/001/...`, `match/002/...`, `match/003/...`) instead of the lesson content id,
which collides across levels. Corrected paths below reflect where each surviving image
now actually lives; QA was performed by direct inspection of the files.

| Asset Key | Image Hint | Output Path | Status | QA |
|---|---|---|---|---|
| match/starters_lesson_001/exercise-0/item-0 | two teachers waving and smiling at each other | tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-0.webp | Not generated | Pending |
| match/starters_lesson_001/exercise-0/item-1 | the sun rising over a school building | tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_001/exercise-0/item-2 | a female teacher smiling at the front of a class | tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-2.webp | Not generated | Pending |
| match/starters_lesson_002/exercise-0/item-0 | an open English textbook on a desk | tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-0.webp | Generated, then deleted | Rejected: pages illustrated with a tree, two birds, a cat, and a sun icon — distractor clutter, target concept ("book") not the clearest element |
| match/starters_lesson_002/exercise-0/item-1 | a blue ink pen lying on a notebook | tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_002/exercise-0/item-2 | a female teacher smiling at the front of a class | tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-2.webp | Not generated (report claimed Generated but no file existed on disk) | Pending |
| match/starters_lesson_003/exercise-0/item-0 | an open English textbook on a desk | tinysteps-app/public/illustrations/match/starters_lesson_003/exercise-0/item-0.webp | Generated, then deleted | Rejected: same distractor-clutter failure as lesson_002/item-0, plus an unrelated map/scene illustration on the facing page |
| match/starters_lesson_003/exercise-0/item-1 | a blue ink pen lying on a notebook | tinysteps-app/public/illustrations/match/starters_lesson_003/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_003/exercise-0/item-2 | a classroom full of students sitting at desks | tinysteps-app/public/illustrations/match/starters_lesson_003/exercise-0/item-2.webp | Generated | Approved |

**4 approved, 2 rejected, 3 not yet generated.** Re-run
`python3 tinysteps-data/generate_match_illustration_queue.py` to see the current batch-01
queue (21 pending items: the 3 "not generated" above plus all of items 4-25).
| match/starters_lesson_001/exercise-0/item-0 | two teachers waving and smiling at each other | tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_001/exercise-0/item-2 | a female teacher smiling at the front of a class | tinysteps-app/public/illustrations/match/starters_lesson_001/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_002/exercise-0/item-0 | an open English textbook on a desk | tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_002/exercise-0/item-2 | a female teacher smiling at the front of a class | tinysteps-app/public/illustrations/match/starters_lesson_002/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_003/exercise-0/item-0 | an open English textbook on a desk | tinysteps-app/public/illustrations/match/starters_lesson_003/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_004/exercise-0/item-0 | a student cupping their hand to their ear | tinysteps-app/public/illustrations/match/starters_lesson_004/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_004/exercise-0/item-1 | an action illustration showing a person to comprehend | tinysteps-app/public/illustrations/match/starters_lesson_004/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_004/exercise-0/item-2 | a clean graphic illustration of a quiz | tinysteps-app/public/illustrations/match/starters_lesson_004/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_005/exercise-0/item-0 | a young student raising their hand in class | tinysteps-app/public/illustrations/match/starters_lesson_005/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_005/exercise-0/item-1 | a thumbs-up icon with a gold star | tinysteps-app/public/illustrations/match/starters_lesson_005/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_005/exercise-0/item-2 | a simple, clear colorful visualization of nice | tinysteps-app/public/illustrations/match/starters_lesson_005/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_006/exercise-0/item-0 | a clean graphic illustration of a report | tinysteps-app/public/illustrations/match/starters_lesson_006/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_006/exercise-0/item-1 | a clean graphic illustration of a behavior | tinysteps-app/public/illustrations/match/starters_lesson_006/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_006/exercise-0/item-2 | a clean graphic illustration of a colleague | tinysteps-app/public/illustrations/match/starters_lesson_006/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_007/exercise-0/item-0 | a bustling fresh food market in Vietnam | tinysteps-app/public/illustrations/match/starters_lesson_007/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_007/exercise-0/item-1 | a steaming bowl of white jasmine rice | tinysteps-app/public/illustrations/match/starters_lesson_007/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_007/exercise-0/item-2 | an action illustration showing a person to buy | tinysteps-app/public/illustrations/match/starters_lesson_007/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_008/exercise-0/item-0 | a steaming bowl of white jasmine rice | tinysteps-app/public/illustrations/match/starters_lesson_008/exercise-0/item-0.webp | Generated | Approved |
| match/starters_lesson_008/exercise-0/item-1 | a clean glass of water on a table | tinysteps-app/public/illustrations/match/starters_lesson_008/exercise-0/item-1.webp | Generated | Approved |
| match/starters_lesson_008/exercise-0/item-2 | a clean graphic illustration of a meat | tinysteps-app/public/illustrations/match/starters_lesson_008/exercise-0/item-2.webp | Generated | Approved |
| match/starters_lesson_009/exercise-0/item-0 | a clean graphic illustration of a direction | tinysteps-app/public/illustrations/match/starters_lesson_009/exercise-0/item-0.webp | Generated | Approved |
