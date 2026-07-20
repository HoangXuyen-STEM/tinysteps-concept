# TinySteps Illustration Sourcing Decision

## Decision

Use **ChatGPT image generation (`gpt_image`) as the primary producer** for TinySteps Match illustrations. Do not use generic web-image search as the primary production source.

## Why generated illustrations fit the product

- **Pedagogy:** the asset contract requires one clear target concept and prohibits readable text and competing distractors. Generation can explicitly constrain all three.
- **Style:** a single consistent prompt/style can match the approved “open English textbook on a desk” proof-of-concept. Mixed stock sources cannot reliably do this.
- **Coverage:** many lesson hints are abstract or instructional (for example, pronunciation, assessment, guidelines, colleague). Suitable stock photographs often do not exist.
- **Rights:** OpenAI states it does not claim copyright over content generated through its API. This does not eliminate all legal review, but avoids tracking hundreds of third-party licensors.
- **Operational fit:** the existing queue, 25-item batch reports, approved-only manifest builder, and Storage upload flow can remain unchanged; only the generator changes.

## Why web sourcing is not a primary path

Unsplash and Pexels offer permissive commercial-use licenses, but license compliance alone does not meet the learning requirement:

- source photos frequently contain text, branding, worksheets, book covers, signage, or unwanted people/objects;
- hundreds of photographers/styles create an inconsistent learning experience;
- each downloaded asset needs a provenance record (source URL, author, license snapshot, date, and any attribution obligation);
- Wikimedia Commons requires per-file license/attribution analysis and is unsuitable for bulk selection.

Web assets may be considered only as a **manual exception** for a small number of concrete, non-branded concepts where a clearly licensed image passes the same human QA gate. Never download arbitrary search-engine results.

## Production safeguards

1. **Choose one producer partition before generating anything else.** Antigravity already has corrected `starters_lesson_*` output through at least lesson 018. Either stop Antigravity and hand the *remaining* queue to `gpt_image`, or assign separate full levels to each producer. Never let both generators write the same asset key.
2. Keep the paused Batch 01 rename as a separate prerequisite before the manifest builder runs again: its legacy `001/`, `002/`, and `003/` paths must be moved to full `starters_lesson_*` paths or remain intentionally excluded as orphaned assets.
3. Run a `gpt_image` pilot of 10–15 images from one ungenerated lesson before any 525-image order. Include a side-by-side visual comparison with approved Antigravity output so human QA can accept or reject mixed-generator style.
4. Triage unusable or vague `image_hint` values before prompting (for example, abstract terms that cannot produce a single unambiguous visual scene).
5. Keep output to 1:1 WebP, correct full lesson-id asset paths, and 25-item review batches.
6. Human QA must reject text, branding, distractors, unclear target concepts, or inconsistent style.
7. Build the manifest and upload only approved report rows; do not bulk-publish a filesystem directory.

## Cost and approval

A full 525-image run is a paid workload. The pilot must log actual cost per image, regeneration count, and reject rate. Set a cost ceiling and explicitly approve the resulting empirical scale estimate before bulk generation. No bulk run should begin from this decision document alone.
