// Upload QA-approved match illustrations to the Supabase Storage "illustrations"
// bucket. Only uploads what's listed in public/illustrations/match/manifest.json
// (run build-illustration-manifest.mjs first) — never walks the filesystem directly,
// so a rejected/deleted image or an unapproved stray file can never reach Storage.
//
// Run locally only, never in Vercel: SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
//   node scripts/upload-illustrations-to-storage.mjs
//
// Object keys match the manifest's own "path" field (e.g.
// "illustrations/match/starters_lesson_001/exercise-0/item-1.webp"), so
// NEXT_PUBLIC_ASSET_BASE_URL follows the exact same convention already verified for
// audio in phase 07: the Storage root WITHOUT a trailing bucket-name segment
// (".../object/public", not ".../object/public/illustrations") — the manifest path's
// own "illustrations/" prefix supplies that segment once concatenated.
import { createClient } from "@supabase/supabase-js";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const manifestPath = join(appDirectory, "public", "illustrations", "match", "manifest.json");
const BUCKET = "illustrations";

const supabaseUrl = process.env.SUPABASE_URL;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!supabaseUrl || !serviceRoleKey) {
  console.error("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (service role — local env only).");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, serviceRoleKey);

async function main() {
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const assets = Object.values(manifest.assets);

  const { error: bucketError } = await supabase.storage.createBucket(BUCKET, { public: true });
  if (bucketError && !/already exists/i.test(bucketError.message)) {
    throw new Error(`createBucket failed: ${bucketError.message}`);
  }

  let uploaded = 0;
  let failed = 0;

  for (const asset of assets) {
    // asset.path is "illustrations/match/...webp"; the bucket already supplies the
    // "illustrations" segment, so the object key drops that leading directory.
    const key = asset.path.replace(/^illustrations\//, "");
    const body = await readFile(join(appDirectory, "public", asset.path));
    // upsert: true — a rejected image gets deleted+regenerated under the SAME key, so
    // re-approving it must overwrite the old Storage object, not skip it.
    const { error } = await supabase.storage
      .from(BUCKET)
      .upload(key, body, { contentType: "image/webp", upsert: true });

    if (!error) uploaded++;
    else {
      failed++;
      console.error(`FAILED ${key}: ${error.message}`);
    }
  }

  console.log(`Uploaded/updated ${uploaded}, failed ${failed} (of ${assets.length} approved assets).`);
  if (failed > 0) process.exit(1);
}

main();
