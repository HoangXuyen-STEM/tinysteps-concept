# Match Exercise Illustration Asset Contract

## Purpose

`image_hint` is a prompt/brief for an illustration. It is **not** display copy. The Match UI must show an image and reserve the text only for `alt` accessibility metadata.

## Asset identity

A Match item gets a deterministic `assetKey` at content-build time:

```text
match/<lesson-id>/exercise-<zero-based-index>/item-<zero-based-index>
```

Example for a first item in the first Match exercise of `starters_lesson_001`:

```text
match/starters_lesson_001/exercise-0/item-0
```

This is scene-specific: two items whose answer is `book` can still use different illustrations.

## Files and manifest

- Local, runtime-served asset: `public/illustrations/match/<lesson-id>/exercise-<n>/item-<n>.webp`
- Build manifest: `public/illustrations/match/manifest.json`
- Production asset base: a versioned Supabase Storage/CDN URL, injected through `NEXT_PUBLIC_ASSET_BASE_URL` during Phase 07.

`manifest.json` is generated, not hand-maintained:

```json
{
  "version": 1,
  "assets": {
    "match/starters_lesson_001/exercise-0/item-0": {
      "localPath": "/illustrations/match/starters_lesson_001/exercise-0/item-0.webp",
      "alt": "An open English textbook on a desk",
      "fallbackIcon": "book-open"
    }
  }
}
```

## UI resolution and fallback

1. Resolve `assetKey` to the local path in development, or to CDN/Storage in production.
2. Render the image with `alt` from the manifest. Never render `image_hint` as visible exercise content.
3. On a missing manifest entry or image load error, render a semantic SVG icon (`BookOpen` for this proof-of-concept), with the same accessible alt label.
4. If there is no safe semantic icon mapping, use a neutral image placeholder icon; do not show `correct_answer` or `image_hint` as the fallback body because that can disclose the answer.

## Illustration brief / QA rules

- The target concept must be the largest, clearest visual element.
- Do not include readable words, letters, labels, brand marks, watermarks, or answer text.
- Avoid distractor objects that are also answer options. For the current `book / teacher / pen` exercise: show only the open book and the desk.
- Keep a stable warm, classroom-friendly visual style and 1:1 aspect ratio.
- Human QA must approve each generated batch for target clarity, safety, duplicate scenes, and accidental text before it becomes a runtime asset.

## Rollout

1. Add the resolver + icon fallback behind the existing Match component.
2. Add this proof-of-concept asset and verify local rendering/error fallback.
3. Build a content scanner that emits a CSV/JSON generation queue from all Match items.
4. Generate in small batches, QA, then publish a versioned manifest.
5. In Phase 07, upload approved assets and manifest to Storage/CDN; keep the same asset keys so application code does not change.
