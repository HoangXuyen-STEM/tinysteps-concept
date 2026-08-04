// Post-upload check on the two audio buckets. Asserts the paywall boundary in both
// directions, which a coverage-only check cannot do:
//
//   trial recordings  must be publicly readable from the "audio-free" bucket
//   paid recordings   must NOT be publicly readable from either bucket
//
// The second half is the one that matters: the whole library used to sit in one public
// bucket under sequential filenames, so anyone could walk it without an account. If a
// future upload lands paid audio in the public bucket, this fails.
//
// Run: AUDIO_BASE_URL=https://<ref>.supabase.co/storage/v1/object/public \
//   node scripts/verify-audio-coverage.mjs
import { readAudioManifest, readFreeAudioKeys, toStorageKey } from "./free-audio-keys.mjs";

const PRIVATE_BUCKET = "audio";
const PUBLIC_BUCKET = "audio-free";

const baseUrl = (process.env.AUDIO_BASE_URL ?? process.env.NEXT_PUBLIC_AUDIO_BASE_URL)?.replace(
  /\/+$/,
  "",
);
if (!baseUrl) {
  console.error("Set AUDIO_BASE_URL (the value you plan to use for NEXT_PUBLIC_AUDIO_BASE_URL).");
  process.exit(1);
}

async function isPubliclyReadable(url) {
  try {
    const res = await fetch(url, { method: "HEAD" });
    return res.ok;
  } catch {
    return false;
  }
}

/** Bounded pool: the production set is ~6k files and Storage should not be spiked. */
async function checkAll(urls, expectReadable) {
  const concurrency = 10;
  const failures = [];
  for (let index = 0; index < urls.length; index += concurrency) {
    const batch = urls.slice(index, index + concurrency);
    const results = await Promise.all(batch.map(isPubliclyReadable));
    results.forEach((readable, batchIndex) => {
      if (readable !== expectReadable) failures.push(batch[batchIndex]);
    });
  }
  return failures;
}

async function main() {
  const manifest = await readAudioManifest();
  const freeKeys = await readFreeAudioKeys(manifest);

  const allKeys = [];
  for (const section of [manifest.vocabulary, manifest.lessons]) {
    for (const entry of Object.values(section)) {
      for (const path of Object.values(entry)) allKeys.push(toStorageKey(path));
    }
  }
  // manifest.listening is flat: { exerciseId: "audio/listening/level/id.mp3" }.
  for (const path of Object.values(manifest.listening ?? {})) allKeys.push(toStorageKey(path));

  const paidKeys = allKeys.filter((key) => !freeKeys.has(key));

  const missingFree = await checkAll(
    [...freeKeys].map((key) => `${baseUrl}/${PUBLIC_BUCKET}/${key}`),
    true,
  );
  // Paid audio is checked against BOTH buckets: the private one must reject an unsigned
  // read, and the public one must not hold a copy at all.
  const exposedPaid = await checkAll(
    paidKeys.flatMap((key) => [
      `${baseUrl}/${PRIVATE_BUCKET}/${key}`,
      `${baseUrl}/${PUBLIC_BUCKET}/${key}`,
    ]),
    false,
  );

  console.log(`Trial recordings publicly readable: ${freeKeys.size - missingFree.length}/${freeKeys.size}`);
  console.log(`Paid recordings kept private: ${paidKeys.length * 2 - exposedPaid.length}/${paidKeys.length * 2} checks`);

  if (missingFree.length > 0) {
    console.error(`\n${missingFree.length} trial recording(s) NOT publicly readable. First 10:`);
    missingFree.slice(0, 10).forEach((url) => console.error(`  ${url}`));
  }
  if (exposedPaid.length > 0) {
    console.error(`\n${exposedPaid.length} PAID recording(s) publicly readable. First 10:`);
    exposedPaid.slice(0, 10).forEach((url) => console.error(`  ${url}`));
  }
  if (missingFree.length > 0 || exposedPaid.length > 0) process.exit(1);
}

main();
