# Using a Friend's Google AI Ultra Account for TinySteps Image Generation

## Short answer

A friend's **Google AI Ultra** subscription can increase their limits in Gemini, AI Studio, and Antigravity, but it is **not automatically a shared Gemini Developer API budget** for your project. Google changes plan bundles, so the account owner must verify their current entitlement in **AI Studio → Get API key** and confirm whether the selected project shows Free Tier or Paid Tier access.

For programmatic image generation, use a **Gemini API key tied to a Google AI Studio / Google Cloud project**. API billing, quota, audit logs, and responsibility follow that project and its billing account—not simply the friend's consumer Ultra subscription.

## Credential safety / Security checklist

- The `AQ...` token previously shared in chat should be treated as exposed and rotated. **Correction:** Google is transitioning from older `AIza...` traffic keys to newer `AQ...` authorization keys, so an `AQ...` value can be a valid Gemini API credential. Its validity and model/billing entitlement must be checked safely against the intended AI Studio project; do not infer either from its prefix alone.
- The TinySteps session also previously exposed Supabase service-role and access tokens. Rotate those in Supabase immediately: the **service-role key bypasses RLS** and is the highest-priority rotation.
- Never paste a replacement API key in normal chat, source code, browser code, shell commands, or reports. Use only a masked secret field for a short, explicitly approved pilot.
- The friend's key means the friend's bill, quota, account responsibility, and audit trail. Set a hard project budget and billing alerts before sharing it; there is no per-user spend isolation.

## Recommended collaboration setup

The account owner should do these steps themselves:

1. Sign in to **Google AI Studio** with the account they control.
2. Create a **dedicated Google Cloud project** for `TinySteps illustrations`; do not reuse their personal/default project.
3. In AI Studio, create a Gemini API key for that dedicated project. The standard developer key commonly begins with `AIza`.
4. Link billing to that project if the selected image model/usage requires the Paid Tier. Google documents that paid-tier access is enabled per project/key after billing is set up.
5. Set a project-level budget, billing alert(s), and a conservative API quota before making any image calls.
6. The owner should retain ownership of the billing account and revoke the dedicated key immediately when the pilot completes.
7. Share the key only through a masked secret field in the authorized TinySteps pilot flow. Do not share their Google account password, browser cookies, OAuth/session tokens, or consumer subscription credentials.

## What to confirm before a paid pilot

Ask the owner to confirm all four items:

- The dedicated project name/ID and that billing is linked to **that** project.
- The exact Gemini image-generation model enabled for the project.
- A hard spending cap for the image pilot and alerts below it.
- Permission to use the key for a limited TinySteps pilot only—not open-ended generation.

## TinySteps-safe pilot

- Limit: 5–10 images, serialized one at a time.
- Scope: one ungenerated lesson; do not overwrite Antigravity assets already created.
- Output: inspect raw image, QA for text/logo/distractors, then convert only approved files to square WebP.
- Audit: log no secret values; record asset key, model, timestamp, cost signal, regenerate count, and QA verdict.
- Stop: on quota/billing error, unexpected cost, or more than one quality rejection in five images.

## Better alternative already available

`gpt_image` is already available in this workspace and produced the initial approved TinySteps proof-of-concept. It needs no friend’s credential, keeps the account/billing boundary clear, and is the lower-friction route. Use the friend's Gemini API only if the account owner explicitly accepts the dedicated-project billing and audit arrangement above.

## Sources to verify with the account owner

- Google AI plans: https://one.google.com/intl/en/about/google-ai-plans/
- Gemini API billing: https://ai.google.dev/gemini-api/docs/billing
- Gemini API key guidance: https://ai.google.dev/gemini-api/docs/api-key
