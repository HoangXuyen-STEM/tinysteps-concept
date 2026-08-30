import { describe, expect, test } from "vitest";
import { stationsFor, takeawayLines } from "../stations";

const v1Lesson = {
  id: "starters_lesson_001",
  level: "starters",
  dialogue: {
    lines: [
      { character_id: "a", text: "Good morning!" },
      { character_id: "b", text: "Open your book." },
      { character_id: "a", text: "Sit down, please." },
      { character_id: "b", text: "Yes, teacher." },
    ],
  },
  exercises: [],
  // fixture
} as unknown as import("@/lib/types/content-types").Lesson;

const v2Lesson = {
  ...v1Lesson,
  schema_version: 2,
  stations: ["look", "practice", "takeaway"],
  takeaway_lines: ["Sit down, please.", "Open your book."],
} as unknown as import("@/lib/types/content-types").Lesson;

describe("stationsFor", () => {
  test("v1 lesson gets default 4 stations", () => {
    expect(stationsFor(v1Lesson)).toEqual(["look", "say", "practice", "takeaway"]);
  });

  test("v2 lesson uses custom stations", () => {
    expect(stationsFor(v2Lesson)).toEqual(["look", "practice", "takeaway"]);
  });
});

describe("takeawayLines", () => {
  test("v1 takeaway uses first 4 dialogue lines", () => {
    expect(takeawayLines(v1Lesson)).toEqual([
      "Good morning!",
      "Open your book.",
      "Sit down, please.",
      "Yes, teacher.",
    ]);
  });

  test("v2 takeaway uses curated lines", () => {
    expect(takeawayLines(v2Lesson)).toEqual([
      "Sit down, please.",
      "Open your book.",
    ]);
  });
});
