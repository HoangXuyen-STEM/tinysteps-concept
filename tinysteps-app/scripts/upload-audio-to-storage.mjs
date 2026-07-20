// Upload all local MP3s to the Supabase Storage "audio" bucket.
//
// Run locally only, never in Vercel: SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
//   node scripts/upload-audio-to-storage.mjs [--overwrite] [relative/file.mp3 ...]
//
// By default an object already in the bucket is left alone, which keeps repeat runs
// cheap. Pass --overwrite after correcting a word or example sentence and regenerating
// its audio: without it the bucket keeps the old recording while the app shows the new
// text, and the learner hears something different from what is on screen.
//
// Object keys are the file's path relative to tinysteps-data/audio (e.g.
// "vocabulary/starters/starters_vocab_001_word.mp3") — NOT prefixed with "audio/".
// That prefix is supplied by the bucket name itself. This matters: audioUrl()
// (lib/content/audio-manifest.ts) builds `${NEXT_PUBLIC_AUDIO_BASE_URL}/${relativePath}`,
// where relativePath already starts with "audio/" (as stored in manifest.json). So
// NEXT_PUBLIC_AUDIO_BASE_URL must be the Storage root WITHOUT a "/audio" suffix
// (`.../storage/v1/object/public`) — the manifest's own "audio/" segment supplies the
// bucket name when concatenated. Verified locally: a base ending in "/audio" produces
// a doubled "/audio/audio/..." path and 400s; the no-suffix base 200s.
import { createClient } from "@supabase/supabase-js";
import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const repositoryDirectory = join(appDirectory, "..");
const audioRoot = join(repositoryDirectory, "tinysteps-data", "audio");
const BUCKET = "audio";

const supabaseUrl = process.env.SUPABASE_URL;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!supabaseUrl || !serviceRoleKey) {
  console.error("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (service role — local env only).");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, serviceRoleKey);
const overwrite = process.argv.includes("--overwrite");
const requestedKeys = new Set(process.argv.slice(2).filter((argument) => !argument.startsWith("--")));

for (const key of requestedKeys) {
  if (key.startsWith("/") || key.includes("..") || !key.endsWith(".mp3")) {
    console.error(`Invalid relative MP3 path: ${key}`);
    process.exit(1);
  }
}

async function* walkMp3(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) yield* walkMp3(full);
    else if (entry.name.endsWith(".mp3")) yield full;
  }
}

async function main() {
  const { error: bucketError } = await supabase.storage.createBucket(BUCKET, { public: true });
  if (bucketError && !/already exists/i.test(bucketError.message)) {
    throw new Error(`createBucket failed: ${bucketError.message}`);
  }

  let uploaded = 0;
  let skipped = 0;
  let failed = 0;
  let selected = 0;
  if (overwrite) console.log("--overwrite: replacing objects that already exist.");
  if (requestedKeys.size > 0) console.log(`Selective upload: ${requestedKeys.size} requested files.`);

  for await (const filePath of walkMp3(audioRoot)) {
    const key = relative(audioRoot, filePath).replaceAll("\\", "/");
    if (requestedKeys.size > 0 && !requestedKeys.has(key)) continue;
    selected++;
    const body = await readFile(filePath);
    const { error } = await supabase.storage
      .from(BUCKET)
      .upload(key, body, { contentType: "audio/mpeg", upsert: overwrite });

    if (!error) {
      uploaded++;
    } else if (/already exists|Duplicate/i.test(error.message)) {
      skipped++;
    } else {
      failed++;
      console.error(`FAILED ${key}: ${error.message}`);
    }
  }

  if (requestedKeys.size > 0 && selected !== requestedKeys.size) {
    failed += requestedKeys.size - selected;
    console.error(`${requestedKeys.size - selected} requested files were not found under ${audioRoot}.`);
  }
  console.log(`Uploaded ${uploaded}, skipped (already present) ${skipped}, failed ${failed}.`);
  if (failed > 0) process.exit(1);
}

main();
