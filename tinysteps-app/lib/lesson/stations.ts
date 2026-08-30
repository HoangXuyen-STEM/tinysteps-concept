import type { Lesson } from "@/lib/types/content-types";

export type StationId = "look" | "say" | "practice" | "takeaway";

/**
 * Returns station sequence for a lesson.
 * v1 lessons (no schema_version) get the default 4 stations.
 * v2 lessons can customize via `stations` field.
 */
export function stationsFor(lesson: Lesson): StationId[] {
  const raw = lesson as Record<string, unknown>;
  if (
    raw.schema_version === 2 &&
    Array.isArray(raw.stations) &&
    raw.stations.length > 0
  ) {
    return raw.stations as StationId[];
  }
  return ["look", "say", "practice", "takeaway"];
}

/**
 * Returns takeaway lines for end-of-lesson display.
 * v2 lessons have curated `takeaway_lines`.
 * v1 lessons use the first 4 dialogue lines (practical fallback).
 */
export function takeawayLines(lesson: Lesson): string[] {
  const raw = lesson as Record<string, unknown>;
  if (Array.isArray(raw.takeaway_lines) && raw.takeaway_lines.length > 0) {
    return raw.takeaway_lines as string[];
  }
  return lesson.dialogue.lines.slice(0, 4).map((line) => line.text);
}
