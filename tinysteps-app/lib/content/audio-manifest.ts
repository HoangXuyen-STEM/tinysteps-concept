import "server-only";
import manifest from "@data/audio/manifest.json";
import { parseAudioManifest } from "./content-schemas";

const audioManifest = parseAudioManifest(manifest);
type AudioSection = "vocabulary" | "lessons";

// relativePath already starts with "audio/" (e.g. "audio/vocabulary/starters/...").
// In dev that maps straight onto the public/audio symlink. In prod, NEXT_PUBLIC_AUDIO_BASE_URL
// must be the Storage root WITHOUT a trailing "/audio" (`.../object/public`, not
// `.../object/public/audio`) — the manifest's own "audio/" segment supplies the bucket
// name once concatenated. Verified in phase 07: a base ending in "/audio" doubles the
// segment and 404s. See scripts/upload-audio-to-storage.mjs for the upload-side half.
export function audioUrl(section: AudioSection, id: string, type: string): string | undefined {
  const relativePath = audioManifest[section][id]?.[type];
  if (!relativePath) return undefined;
  const baseUrl = process.env.NEXT_PUBLIC_AUDIO_BASE_URL?.replace(/\/$/, "");
  return baseUrl ? `${baseUrl}/${relativePath}` : `/${relativePath}`;
}

export const getAudioManifest = () => audioManifest;