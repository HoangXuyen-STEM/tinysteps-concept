import { describe, expect, it } from "vitest";
import startersWriting from "../../../.content/writing/starters.json";
import { parseWritingDocument } from "../content-schemas";

describe("writing content schema", () => {
  it("parses five ordered Starters exercises with five mapped blanks each", () => {
    const document = parseWritingDocument(startersWriting, "starters test");
    expect(document.exercises).toHaveLength(5);
    expect(document.exercises.every((exercise) => exercise.blanks.length === 5)).toBe(true);
  });

  it("rejects duplicate or missing placeholders", () => {
    const invalid = structuredClone(startersWriting);
    invalid.exercises[0].passage = invalid.exercises[0].passage.replace("{{b2}}", "{{b1}}");
    expect(() => parseWritingDocument(invalid, "invalid test")).toThrow("Each blank must have exactly one unique placeholder");
  });
});
