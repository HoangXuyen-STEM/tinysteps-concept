import "server-only";
import manifest from "@data/audio/manifest.json";
import { parseAudioManifest } from "./content-schemas";

const audioManifest = parseAudioManifest(manifest);
type AudioSection = "vocabulary" | "lessons";

// Manifest paths all start with "audio/" (e.g. "audio/vocabulary/starters/...") — that
// leading segment is the bucket name, supplied once the path is concatenated onto the
// Storage root. These functions return the manifest path only; turning it into a URL is
// entitlement-dependent and lives in audio-access.ts, because paid audio sits in a
// private bucket and has to be signed.
export function audioPath(section: AudioSection, id: string, type: string): string | undefined {
  return audioManifest[section][id]?.[type];
}

/** manifest.listening is flat (exercise id -> path), one mp3 per exercise — no `type` key. */
export function listeningAudioPath(exerciseId: string): string | undefined {
  return audioManifest.listening[exerciseId];
}

export const getAudioManifest = () => audioManifest;