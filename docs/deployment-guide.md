# Deployment Guide — TinySteps

MVP deploy target: Vercel (app) + Supabase (auth/DB/audio storage). Infrastructure is
owned by the user (plan.md decision 5) — this guide is the runbook for those steps.
Code-side work (upload scripts, env wiring) is already built and locally verified;
what's left is dashboard/CLI actions only you can run.

## Prerequisites
- Migrations `000001`, `000002`, `000003` already applied to your real Supabase
  project (phases 03/04/05 runbooks). If not done yet, do that first — this guide
  assumes the schema exists.
- A Vercel account you own, with this repo accessible (GitHub/GitLab/Bitbucket).

## 1. Upload audio to Supabase Storage

Run locally, once, from `tinysteps-app/`:

```bash
SUPABASE_URL="https://<ref>.supabase.co" \
SUPABASE_SERVICE_ROLE_KEY="<service role key, Project Settings → API>" \
node scripts/upload-audio-to-storage.mjs
```

- Creates a public bucket named `audio` if it doesn't exist, then uploads all 6126
  MP3s from `tinysteps-data/audio/`. Idempotent — safe to re-run (skips existing
  objects), so re-running after a content top-up only uploads what's new.
- Takes roughly 1 minute against a local Supabase instance; expect longer against a
  real remote project (network latency per file).
- **Never** put `SUPABASE_SERVICE_ROLE_KEY` in `.env.local` or any file read by the
  Next.js app — export it in your shell for this one command only. It has full
  database/storage access and must never reach the client bundle or Vercel's env.

## 2. Set the audio base URL

**Critical — read this before setting the env var.** The manifest's paths already
start with `audio/` (e.g. `audio/vocabulary/starters/starters_vocab_001_word.mp3`), and
`audioUrl()` (`lib/content/audio-manifest.ts`) does `${base}/${relativePath}`. So the
base must be the Storage root **without** a trailing `/audio` — that segment comes
from the manifest path itself, which happens to equal the bucket name by convention.

```
NEXT_PUBLIC_AUDIO_BASE_URL=https://<ref>.supabase.co/storage/v1/object/public
```

(NOT `.../object/public/audio` — that duplicates the segment and every audio URL
404s. Verified locally 2026-07-14: the correct form 200s, the `/audio`-suffixed form
400s.)

Set this in `tinysteps-app/.env.local` for local testing against the real bucket, and
in Vercel's project env vars (step 4) for prod.

## 1b. Match illustrations

Content-generation pipeline docs: `docs/antigravity-match-illustration-prompt-pack.md`,
`docs/match-illustration-asset-contract.md`. Not required for the pilot launch — the
Match exercise still works with its text caption until this ships. When ready:

```bash
cd tinysteps-app
node scripts/build-illustration-manifest.mjs   # rebuilds manifest.json from Approved QA rows
SUPABASE_URL="https://<ref>.supabase.co" \
SUPABASE_SERVICE_ROLE_KEY="<service role key>" \
node scripts/upload-illustrations-to-storage.mjs
```

Same base-URL convention as audio: `NEXT_PUBLIC_ASSET_BASE_URL` (a separate env var
from audio's) must be the Storage root without a trailing `/illustrations` — the
manifest's own `illustrations/` path prefix supplies that segment. The Match UI reads
the bundled QA-approved manifest and resolves each image through this base URL.

Verify all approved illustrations after upload:

```bash
ASSET_BASE_URL="https://<ref>.supabase.co/storage/v1/object/public" \
node scripts/verify-illustration-coverage.mjs
```

## 3. Verify upload coverage

```bash
AUDIO_BASE_URL="https://<ref>.supabase.co/storage/v1/object/public" \
node scripts/verify-audio-coverage.mjs
```

HEADs every manifest entry through the exact URL the app would build. Must report
`Missing: 0` before deploying — a non-zero count means step 1 or step 2 has a problem
(re-check the base URL first; it's the most common mistake here).

## 4. Deploy to Vercel

1. Vercel dashboard → New Project → import this repo.
2. **Root Directory: `tinysteps-app`** (this is a multi-app repo; Vercel must build
   only the Next.js app, not the repo root).
3. Framework preset: Next.js (auto-detected).
4. Environment variables (Production + Preview):
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_AUDIO_BASE_URL` (from step 2 — no trailing `/audio`)
   - `NEXT_PUBLIC_ASSET_BASE_URL` (same Storage root — no trailing `/illustrations`)
   - `NEXT_PUBLIC_SITE_URL` (your prod domain, e.g. `https://tinysteps.vercel.app`)
   - `NEXT_PUBLIC_FEEDBACK_FORM_URL` (optional — pilot feedback Google Form; nav link
     hides itself if unset)
   - Do **NOT** set `SUPABASE_SERVICE_ROLE_KEY` here — it's a local-only tool used in
     step 1, never needed at runtime.
5. Deploy. `npm run prebuild` (→ `prepare-content.mjs`) runs automatically before
   `next build` — it regenerates the lesson index and, on Vercel, explicitly **skips**
   the `public/audio` symlink (`process.env.VERCEL` guard), so no MP3s are traced into
   the deploy output.
   Before deploying, run `npm run check:launch` with the intended production env to
   catch missing payment/CDN settings without printing their values.
6. Content import path: already resolved in phase 02 — `prepare-content.mjs` copies
   vocab/topics/lessons into `tinysteps-app/.content/` (not a parent-directory import),
   so there is no Vercel serverless `fs`-read risk. Nothing to change here.

## 5. Point Supabase Auth at the prod domain

Dashboard → Authentication → URL Configuration:
- Site URL → your Vercel prod domain.
- Redirect URLs → add the prod domain (keep `http://localhost:3000` too for local dev).

Re-verify the Magic Link email template still points at
`{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email&next=/dashboard`
(phase 03 Runbook E) — the Site URL change alone doesn't touch the template.

## 6. Smoke test (prod URL)

- [ ] Public signup rejected; magic link to an unknown email creates no account.
- [ ] Dashboard-created pilot account logs in (password + magic link via custom SMTP).
- [ ] Open a lesson → audio plays; network tab shows the Storage URL, 200.
- [ ] Complete a lesson → refresh → still shows completed.
- [ ] Review a card → refresh → schedule persisted.
- [ ] Dashboard shows correct completion / due-today / streak.
- [ ] Second account cannot see the first account's data (RLS).
- [ ] Usable at 360px viewport width.
- [ ] `curl` the built JS bundle (or DevTools → Sources) and confirm no service-role
      key or other secret appears anywhere in client code.

## 7. Pilot operations (after smoke test passes)

- Auth → confirm "Allow new users to sign up" is OFF on the prod project.
- Send a magic link to one external (non-team) mailbox — confirms custom SMTP works
  end-to-end on the prod domain, not just locally.
- Create the 10 pilot accounts (Auth → Users → Add user, with password) — profile rows
  should appear automatically (trigger from migration `000001`).
- Engagement check (no admin page — YAGNI for 10 users), run in SQL Editor:
  ```sql
  select activity_date, count(*) filter (where learning_day) as active_users, sum(cards_reviewed) as cards
  from daily_activity group by 1 order by 1 desc limit 14;
  ```

## Rollback

- Bad deploy: Vercel dashboard → Deployments → promote the previous working
  deployment ("Redeploy" / "Instant Rollback"). No DB rollback needed for a bad
  frontend deploy — schema is versioned separately via `supabase/migrations/`.
- Bad migration: write a new forward migration to fix it (per team convention — never
  edit an already-applied migration file). Restore from Supabase's automatic backups
  only as a last resort (dashboard → Database → Backups).
