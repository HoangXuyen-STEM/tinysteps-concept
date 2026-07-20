import { describe, it, expect } from "vitest";
import { dueStatePriority, sortDueRows, type DueRow } from "../queue-ordering";

describe("dueStatePriority", () => {
  it("orders Learning < Relearning < Review < New", () => {
    expect(dueStatePriority(1)).toBeLessThan(dueStatePriority(3)); // Learning < Relearning
    expect(dueStatePriority(3)).toBeLessThan(dueStatePriority(2)); // Relearning < Review
    expect(dueStatePriority(2)).toBeLessThan(dueStatePriority(0)); // Review < New
  });
});

describe("sortDueRows", () => {
  it("sorts by state priority, then earliest due first", () => {
    const rows: DueRow[] = [
      { vocab_id: "review_old", state: 2, due: "2026-07-10T00:00:00Z" },
      { vocab_id: "relearning", state: 3, due: "2026-07-14T00:00:00Z" },
      { vocab_id: "learning_late", state: 1, due: "2026-07-14T00:00:00Z" },
      { vocab_id: "learning_early", state: 1, due: "2026-07-12T00:00:00Z" },
      { vocab_id: "review_new", state: 2, due: "2026-07-13T00:00:00Z" },
    ];
    expect(sortDueRows(rows).map((r) => r.vocab_id)).toEqual([
      "learning_early", // Learning, earliest due
      "learning_late", // Learning, later due
      "relearning", // Relearning
      "review_old", // Review, earliest due
      "review_new", // Review, later due
    ]);
  });

  it("does not mutate the input array", () => {
    const rows: DueRow[] = [
      { vocab_id: "a", state: 2, due: "2026-07-10T00:00:00Z" },
      { vocab_id: "b", state: 1, due: "2026-07-11T00:00:00Z" },
    ];
    const before = rows.map((r) => r.vocab_id);
    sortDueRows(rows);
    expect(rows.map((r) => r.vocab_id)).toEqual(before);
  });
});
