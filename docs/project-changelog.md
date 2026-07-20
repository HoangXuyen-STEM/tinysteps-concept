# Project Changelog — TinySteps

## 2026-07-14

### Phase 07 — Deploy scripts + guide (code-complete)
- Added `scripts/upload-audio-to-storage.mjs` (idempotent MP3 upload to Supabase Storage) and `scripts/verify-audio-coverage.mjs` (HEAD-checks every manifest entry through the app's own URL-building logic).
- **Fixed a bug in the phase-07 plan's own documented env var**: `NEXT_PUBLIC_AUDIO_BASE_URL` must be the Storage root without a trailing `/audio` — the manifest's paths already start with `audio/`, so a base ending in `/audio` doubles the segment and 404s everything. Verified against a local Storage instance (correct form 200s, plan's original form 400s) before writing the guide.
- Added `docs/deployment-guide.md`.

### Local-test blockers fixed (dev audio 404, arrange grading always-wrong)
- `tinysteps-app/public/audio` symlink was documented in phase 02 but never implemented — all dev audio 404'd. Fixed via an idempotent symlink step in `prepare-content.mjs`, skipped on Vercel (`process.env.VERCEL` guard) so prod never traces 150MB of MP3 into the build.
- Arrange exercises graded every correct answer as wrong: lesson data ships end punctuation as its own word chip, so the chip-joined answer has a space before the period that `correct_answer` doesn't. Fixed by extending the shared `normalize()` (`lib/exercises/check-answer.ts`) to strip spaces before `.,!?;:`. Verified against all 525 real arrange items across 175 lessons.
- See `plans/260714-1628-fix-dev-audio-serving-and-arrange-grading/` for the full investigation and fix plan.

### Phase 06 — Progress dashboard + polish (code-complete)
Dashboard (level progress, streak, due-today, continue-learning CTA), Vietnamese nav with pilot feedback link, `/` redirect to `/dashboard`. See `plans/reports/build-phase-06-progress-dashboard-and-polish-report.md`.

### Phase 05 — SRS vocabulary review (code-complete)
ts-fsrs v5.3.x review flow. Found and fixed two schema gaps missed by initial research: a missing `learning_steps` column (ts-fsrs 5.3+ Card field) and missing `authenticated` DML grants on `srs_cards`/`profiles` (migration `000001` only had default REFERENCES/TRIGGER/TRUNCATE — would have blocked all SRS reads/writes and the phase-03 RLS runbook). Migration `000003`. See `plans/reports/build-phase-05-srs-vocabulary-review-report.md`.

### Phase 03/04 — Auth, DB schema, lesson player (code-complete, committed)
Committed as checkpoints `71719a9` (phase 03) and `25638c4` (phase 04). Security review found and fixed an open redirect in `/auth/confirm`. Code review of the phase-04 build found and fixed a latent listen-choose audio indexing bug and removed a debug script that hardcoded a JWT signing secret and DB superuser connection string. See `plans/reports/security-review-phase-03-supabase-auth-and-migration-report.md`, `plans/reports/code-review-phase-04-lesson-player-gemini-build-report.md`, `plans/reports/hardening-review-phase-03-04-pre-commit-report.md`.

### Phase 01/02 — Audio pipeline, Next.js scaffold + content layer (completed, committed)
6126 MP3s generated (2100 vocab × 2 + lesson dialogue/listen audio). Server-only content loaders, zod-validated.
