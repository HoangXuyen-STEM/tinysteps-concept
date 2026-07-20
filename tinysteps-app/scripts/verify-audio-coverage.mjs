// Post-upload check: for every entry in the audio manifest, resolve it through the
// SAME audioUrl() logic the app uses and HEAD it. Catches both missing uploads and
// base-URL/key mismatches (the exact bug this script's design caught during phase 07:
// a base URL with a trailing "/audio" doubles up against the manifest's own "audio/"
// prefix and 404s everything).
//
// Run: AUDIO_BASE_URL=https://<ref>.supabase.co/storage/v1/object/public \
//   node scripts/verify-audio-coverage.mjs
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const repositoryDirectory = join(appDirectory, "..");
const manifestPath = join(repositoryDirectory, "tinysteps-data", "audio", "manifest.json");

const baseUrl = (process.env.AUDIO_BASE_URL ?? process.env.NEXT_PUBLIC_AUDIO_BASE_URL)?.replace(
  /\/+$/,
  "",
);
if (!baseUrl) {
  console.error("Set AUDIO_BASE_URL (the value you plan to use for NEXT_PUBLIC_AUDIO_BASE_URL).");
  process.exit(1);
}

function resolveUrl(relativePath) {
  return `${baseUrl}/${relativePath}`;
}

async function headOk(url) {
  try {
    const res = await fetch(url, { method: "HEAD" });
    return res.ok;
  } catch {
    return false;
  }
}

async function main() {
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const relativePaths = [];
  const misses = [];

  const sections = [manifest.vocabulary, manifest.lessons];
  for (const section of sections) {
    for (const entry of Object.values(section)) {
      for (const relativePath of Object.values(entry)) {
        relativePaths.push(relativePath);
      }
    }
  }

  // A small bounded pool makes the 6k-file production check practical without
  // creating an unbounded request spike against Storage.
  const concurrency = 10;
  for (let index = 0; index < relativePaths.length; index += concurrency) {
    const urls = relativePaths.slice(index, index + concurrency).map(resolveUrl);
    const results = await Promise.all(urls.map(headOk));
    results.forEach((ok, resultIndex) => {
      if (!ok) misses.push(urls[resultIndex]);
    });
  }

  console.log(`Checked ${relativePaths.length} audio URLs. Missing: ${misses.length}.`);
  if (misses.length > 0) {
    console.error("First 10 misses:");
    misses.slice(0, 10).forEach((url) => console.error(`  ${url}`));
    process.exit(1);
  }
}

main();
