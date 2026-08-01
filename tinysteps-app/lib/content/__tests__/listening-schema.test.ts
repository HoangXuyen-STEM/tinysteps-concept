import { describe, expect, it } from "vitest";
import startersListening from "../../../.content/listening/starters.json";
import { parseListeningDocument } from "../content-schemas";

describe("listening content schema", () => {
  it("parses three ordered Starters exercises with five mapped blanks each, covering all 4 categories", () => {
    const document = parseListeningDocument(startersListening, "starters test");
    expect(document.exercises).toHaveLength(3);
    expect(document.exercises.every((exercise) => exercise.blanks.length === 5)).toBe(true);
    for (const exercise of document.exercises) {
      const categories = new Set(exercise.blanks.map((blank) => blank.category));
      expect(categories).toEqual(new Set(["number", "color", "address", "age"]));
    }
  });

  it("rejects duplicate or missing placeholders", () => {
    const invalid = structuredClone(startersListening);
    invalid.exercises[0].passage = invalid.exercises[0].passage.replace("{{b2}}", "{{b1}}");
    expect(() => parseListeningDocument(invalid, "invalid test")).toThrow("Each blank must have exactly one unique placeholder");
  });

  it("rejects an exercise missing a required category", () => {
    const invalid = structuredClone(startersListening);
    // Exercise 1's blanks are age/color/number/address/color — collapsing every
    // blank onto "age" leaves color/number/address all missing.
    invalid.exercises[0].blanks.forEach((blank: { category: string }) => {
      blank.category = "age";
    });
    expect(() => parseListeningDocument(invalid, "invalid test")).toThrow("Must cover all 4 categories");
  });

  it("rejects audio_text/transcript with a leftover placeholder", () => {
    const invalid = structuredClone(startersListening);
    invalid.exercises[0].audio_text = invalid.exercises[0].passage;
    expect(() => parseListeningDocument(invalid, "invalid test")).toThrow();
  });
});
