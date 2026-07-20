import "server-only";
import { fsrs, type FSRS } from "ts-fsrs";

// All FSRS scheduling runs server-side only — the client never computes or sends
// card dates/state. request_retention 0.9 per researcher-01. Fuzz spreads due dates
// in prod to avoid review pile-ups; disable it in tests for determinism.
export function getScheduler(opts?: { enableFuzz?: boolean }): FSRS {
  return fsrs({ request_retention: 0.9, enable_fuzz: opts?.enableFuzz ?? true });
}
