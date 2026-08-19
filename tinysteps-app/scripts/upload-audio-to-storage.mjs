// Upload all local MP3s to Supabase Storage.
//
// Run locally only, never in Vercel: SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
//   node scripts/upload-audio-to-storage.mjs [--overwrite] [relative/file.mp3 ...]
//
// Audio is split across two buckets along the paywall:
//
//   audio       private  every recording; reads require an active paid grant
//   audio-free  public   the trial subset, duplicated here so it can be served as plain
//                        cacheable CDN URLs without signing
//
// "audio" stays the complete canonical set, so a file is never moved or deleted when the
// free list changes — only the public copy is added.
//
// By default an object already in a bucket is left alone, which keeps repeat runs cheap.
// Pass --overwrite after correcting a word or example sentence and regenerating its
// audio: without it the bucket keeps the old recording while the app shows the new text,
// and the learner hears something different from what is on screen.
//
// Object keys are the file's path relative to tinysteps-data/audio (e.g.
// "vocabulary/starters/starters_vocab_001_word.mp3") — NOT prefixed with "audio/". That
// prefix is the bucket segment, supplied when lib/content/audio-access.ts builds a URL
// from the manifest path. NEXT_PUBLIC_AUDIO_BASE_URL must therefore be the Storage root
// with no bucket suffix (`.../storage/v1/object/public`).
import { createClient } from "@supabase/supabase-js";
import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { readFreeAudioKeys } from "./free-audio-keys.mjs";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const repositoryDirectory = join(appDirectory, "..");
const audioRoot = join(repositoryDirectory, "tinysteps-data", "audio");
const PRIVATE_BUCKET = "audio";
const PUBLIC_BUCKET = "audio-free";

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


async function ensureBucket(name, isPublic) {
  const { error } = await supabase.storage.createBucket(name, { public: isPublic });
  if (error && !/already exists/i.test(error.message)) {
    throw new Error(`createBucket ${name} failed: ${error.message}`);
  }
  // An existing bucket keeps its old visibility, so state it explicitly: this is what
  // flips a previously public "audio" bucket closed.
  const { error: updateError } = await supabase.storage.updateBucket(name, { public: isPublic });
  if (updateError) throw new Error(`updateBucket ${name} failed: ${updateError.message}`);
}

async function main() {
  await ensureBucket(PRIVATE_BUCKET, false);
  await ensureBucket(PUBLIC_BUCKET, true);
  const freeKeys = await readFreeAudioKeys();
  console.log(`${freeKeys.size} trial recordings also go to the public "${PUBLIC_BUCKET}" bucket.`);

  let uploaded = 0;
  let skipped = 0;
  let failed = 0;
  let selected = 0;
  if (overwrite) console.log("--overwrite: replacing objects that already exist.");
  if (requestedKeys.size > 0) console.log(`Selective upload: ${requestedKeys.size} requested files.`);

  const filePaths = [];
  for await (const filePath of walkMp3(audioRoot)) {
    filePaths.push(filePath);
  }

  console.log(`Found ${filePaths.length} MP3 files locally. Uploading with concurrency=25...`);

  const concurrency = 25;
  let processed = 0;

  async function uploadOne(filePath) {
    const key = relative(audioRoot, filePath).replaceAll("\\", "/");
    if (requestedKeys.size > 0 && !requestedKeys.has(key)) return;
    selected++;
    const body = await readFile(filePath);

    const targets = freeKeys.has(key) ? [PRIVATE_BUCKET, PUBLIC_BUCKET] : [PRIVATE_BUCKET];
    let error = null;
    for (const bucket of targets) {
      const result = await supabase.storage
        .from(bucket)
        .upload(key, body, { contentType: "audio/mpeg", upsert: overwrite });
      if (result.error && !/already exists|Duplicate/i.test(result.error.message)) {
        error = result.error;
        break;
      }
      if (result.error && !error) error = result.error;
    }

    if (!error) {
      uploaded++;
    } else if (/already exists|Duplicate/i.test(error.message)) {
      skipped++;
    } else {
      failed++;
      console.error(`FAILED ${key}: ${error.message}`);
    }

    processed++;
    if (processed % 500 === 0 || processed === filePaths.length) {
      console.log(`Progress: ${processed}/${filePaths.length} (uploaded ${uploaded}, skipped ${skipped}, failed ${failed})`);
    }
  }

  for (let i = 0; i < filePaths.length; i += concurrency) {
    const chunk = filePaths.slice(i, i + concurrency);
    await Promise.all(chunk.map(uploadOne));
  }

  if (requestedKeys.size > 0 && selected !== requestedKeys.size) {
    failed += requestedKeys.size - selected;
    console.error(`${requestedKeys.size - selected} requested files were not found under ${audioRoot}.`);
  }
  console.log(`Finished! Uploaded ${uploaded}, skipped (already present) ${skipped}, failed ${failed}.`);
  if (failed > 0) process.exit(1);
}

main();
