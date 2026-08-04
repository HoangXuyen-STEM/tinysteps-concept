import "server-only";
import { createClient } from "@/utils/supabase/server";
import { getAudioManifest } from "./audio-manifest";
import { FREE_LESSON_IDS, FREE_LISTENING_IDS } from "@/lib/access/paid-access";
import { getFreeVocabIds } from "@/lib/access/unlocked-vocab";

/**
 * Audio lives in two Storage buckets, and the bucket boundary *is* the paywall:
 *
 *   audio-free  public   trial content — the free lessons, the free listening exercise
 *                        and the words those lessons teach
 *   audio       private  every recording, read-gated by a storage policy that requires
 *                        an active paid_access row
 *
 * Splitting them this way keeps the trial fast (plain CDN URLs, cached normally by the
 * browser) and pays the signing cost only for content behind the paywall. A single
 * public bucket previously served every recording to anyone who guessed a filename, and
 * the names are sequential.
 */
const PRIVATE_BUCKET = "audio";
const PUBLIC_BUCKET = "audio-free";

/**
 * Long enough to cover a lesson sitting, short enough that a copied link dies quickly.
 * Signed URLs are minted per render, so within one page the URLs are stable and the
 * browser caches replays; revisiting re-signs.
 */
const SIGNED_URL_TTL_SECONDS = 60 * 60;

const manifest = getAudioManifest();

/**
 * The recordings that belong to trial content, derived from the same free-content lists
 * the rest of the paywall uses so the two cannot drift. Mirrors what
 * scripts/upload-audio-to-storage.mjs puts in the public bucket.
 */
const freeAudioPaths: ReadonlySet<string> = new Set([
  ...FREE_LESSON_IDS.flatMap((id) => Object.values(manifest.lessons[id] ?? {})),
  ...FREE_LISTENING_IDS.map((id) => manifest.listening[id]).filter(Boolean),
  ...[...getFreeVocabIds()].flatMap((id) => Object.values(manifest.vocabulary[id] ?? {})),
]);

export const isFreeAudioPath = (manifestPath: string): boolean => freeAudioPaths.has(manifestPath);

/** Strip the leading "audio/" segment: inside a bucket, keys are stored without it. */
const toStorageKey = (manifestPath: string) => manifestPath.replace(/^audio\//, "");

/**
 * Resolve manifest paths to playable URLs, signing the paid ones in a single batch.
 *
 * Callers must already have established that the learner may open the surrounding
 * lesson/exercise — this resolves URLs, it does not authorize. Paths that fail to sign
 * are omitted, so a caller mapping over its own keys gets null rather than a dead URL.
 */
export async function resolveAudioUrls(
  manifestPaths: readonly (string | undefined)[],
): Promise<Map<string, string>> {
  const paths = [...new Set(manifestPaths.filter((path): path is string => Boolean(path)))];
  const resolved = new Map<string, string>();
  if (paths.length === 0) return resolved;

  // Without a Storage root configured (local dev) the app serves from the public/audio
  // symlink, where both buckets are just one folder tree.
  const baseUrl = process.env.NEXT_PUBLIC_AUDIO_BASE_URL?.replace(/\/$/, "");
  if (!baseUrl) {
    for (const path of paths) resolved.set(path, `/${path}`);
    return resolved;
  }

  const paidPaths: string[] = [];
  for (const path of paths) {
    if (isFreeAudioPath(path)) {
      resolved.set(path, `${baseUrl}/${PUBLIC_BUCKET}/${toStorageKey(path)}`);
    } else {
      paidPaths.push(path);
    }
  }
  if (paidPaths.length === 0) return resolved;

  // One round trip for every locked recording on the page. The anon-key client signs
  // under the learner's own session, so the storage policy — not this code — decides
  // whether a signature is issued; a free account simply gets nothing back.
  const supabase = await createClient();
  const { data, error } = await supabase.storage
    .from(PRIVATE_BUCKET)
    .createSignedUrls(paidPaths.map(toStorageKey), SIGNED_URL_TTL_SECONDS);

  if (error) {
    console.error("resolveAudioUrls: failed to sign paid audio", error);
    return resolved;
  }

  for (const entry of data ?? []) {
    if (!entry.signedUrl || entry.error) continue;
    // createSignedUrls echoes back the key it was given, so re-add the "audio/" prefix
    // to look the result up under the manifest path the caller passed in.
    resolved.set(`audio/${entry.path?.replace(/^\/+/, "")}`, entry.signedUrl);
  }
  return resolved;
}

/** Single-path convenience wrapper around resolveAudioUrls. */
export async function resolveAudioUrl(
  manifestPath: string | undefined,
): Promise<string | undefined> {
  if (!manifestPath) return undefined;
  return (await resolveAudioUrls([manifestPath])).get(manifestPath);
}
