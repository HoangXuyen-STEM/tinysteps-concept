import "server-only";
import manifest from "@data/audio/manifest.json";
import { parseAudioManifest } from "./content-schemas";

const audioManifest = parseAudioManifest(manifest);
type AudioSection = "vocabulary" | "lessons";

export function audioUrl(section: AudioSection, id: string, type: string): string | undefined {
  const relativePath = audioManifest[section][id]?.[type];
  if (!relativePath) return undefined;
  const baseUrl = process.env.NEXT_PUBLIC_AUDIO_BASE_URL?.replace(/\/$/, "");
  return baseUrl ? `${baseUrl}/${relativePath}` : `/${relativePath}`;
}

export const getAudioManifest = () => audioManifest;