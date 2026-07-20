# Gemini Image API — TinySteps Feasibility Notes

## Credential safety

- A Gemini Developer API key conventionally begins with `AIza`. The credential shared in chat did **not** match that prefix, so it must not be sent to a guessed API endpoint.
- Because it appeared in a chat transcript, treat it as exposed: revoke/rotate it at the provider and use a replacement only through a masked secret input or the system keychain.
- Never place the replacement key in source code, prompts, shell history, generated reports, or client-side environment variables.

## Current capability assessment

Google's current Gemini documentation describes native image generation under the **Nano Banana** family (including Gemini image-generation models). This makes Gemini a plausible API route for TinySteps illustrations.

Caveats to validate with a fresh, correctly scoped key before adoption:

1. Model availability, quota, regional access, and billing tier are account-specific.
2. Image-generation outputs may need local validation and conversion to the project’s required 1:1 `.webp` output.
3. Image-capable models have image-per-minute quotas; generation must be serialized with retry/backoff on HTTP 429.
4. Pricing is output-token based and can vary by model/resolution. Do not run the 525-image workload without an approved cost ceiling.

## Recommended pilot (not yet authorized)

Generate 5–10 items from `starters_lesson_001` only, using full lesson-id asset paths, then manually QA every item for target clarity, accidental text, distractors, style, and output-path correctness. The first generated Batch 01 showed a QA failure for a book image, so no bulk approval is appropriate.

### Pilot runbook

1. Rotate the exposed credential and provide a replacement only through a masked field after confirming the selected Gemini image model and a spending ceiling.
2. Select five scenes that cover the risk profile: greeting people, sunrise/morning, book, pen, and teacher/classroom.
3. Generate **one image per request**; do not parallelize. Save raw outputs outside `public/` until QA passes.
4. Reject and regenerate any image with readable text, page illustrations competing with the target object, branded objects, duplicate concepts, or an incorrect square crop.
5. Convert only approved assets to square WebP and write them under `public/illustrations/match/starters_lesson_001/exercise-0/item-<n>.webp`.
6. Create a pilot report with prompt/model, raw-output reference, approved output path, and QA verdict. Do not integrate into the UI or upload Storage in the pilot.

### Proposed stop conditions

Stop before bulk generation if the pilot lacks model access, hits quota/billing restrictions, has more than one rejected image out of five, or cannot consistently produce a clear target without text/distractors.
