// Due-card ordering for the review queue: Learning → Relearning → Review → (New).
// Pure + exported so it can be unit-tested independently of Supabase. State ints match
// ts-fsrs: 0 New, 1 Learning, 2 Review, 3 Relearning (researcher-01 §4).
export function dueStatePriority(state: number): number {
  switch (state) {
    case 1: // Learning
      return 1;
    case 3: // Relearning
      return 2;
    case 2: // Review
      return 3;
    default: // New / anything else
      return 4;
  }
}

export type DueRow = { vocab_id: string; state: number; due: string };

/** Sort due existing cards by state priority, then earliest due first. */
export function sortDueRows(rows: DueRow[]): DueRow[] {
  return [...rows].sort((a, b) => {
    const pa = dueStatePriority(a.state);
    const pb = dueStatePriority(b.state);
    if (pa !== pb) return pa - pb;
    return new Date(a.due).getTime() - new Date(b.due).getTime();
  });
}
