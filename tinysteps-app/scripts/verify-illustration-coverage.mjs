// Post-upload check for every QA-approved Match illustration in the runtime manifest.
// The base URL is the Storage public root, without a trailing "/illustrations".
//
// Run: ASSET_BASE_URL=https://<ref>.supabase.co/storage/v1/object/public \
//   node scripts/verify-illustration-coverage.mjs
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const manifestPath = join(appDirectory, "public", "illustrations", "match", "manifest.json");
const baseUrl = (process.env.ASSET_BASE_URL ?? process.env.NEXT_PUBLIC_ASSET_BASE_URL)?.replace(
  /\/+$/,
  "",
);

if (!baseUrl) {
  console.error("Set ASSET_BASE_URL (the value used for NEXT_PUBLIC_ASSET_BASE_URL).");
  process.exit(1);
}

async function checkAsset(asset) {
  const url = `${baseUrl}/${asset.path}`;
  try {
    const response = await fetch(url, { method: "HEAD" });
    return response.ok ? null : `${response.status} ${url}`;
  } catch (error) {
    return `NETWORK ${url} (${error instanceof Error ? error.message : String(error)})`;
  }
}

async function main() {
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const assets = Object.values(manifest.assets);
  const misses = [];
  const concurrency = 10;

  for (let index = 0; index < assets.length; index += concurrency) {
    const results = await Promise.all(assets.slice(index, index + concurrency).map(checkAsset));
    misses.push(...results.filter(Boolean));
  }

  console.log(`Checked ${assets.length} illustration URLs. Missing: ${misses.length}.`);
  if (misses.length > 0) {
    console.error("First 10 misses:");
    misses.slice(0, 10).forEach((miss) => console.error(`  ${miss}`));
    process.exit(1);
  }
}

main();
