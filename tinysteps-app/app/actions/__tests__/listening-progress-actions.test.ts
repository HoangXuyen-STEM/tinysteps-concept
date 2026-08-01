import { beforeEach, describe, expect, it, vi } from "vitest";
import { revalidatePath } from "next/cache";
import type { ListeningExercise } from "@/lib/types/content-types";
import { startListening, submitListeningAnswers } from "../listening-progress-actions";

vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));

const mocks = vi.hoisted(() => {
  const maybeSingle = vi.fn();
  const insert = vi.fn();
  return {
    getUser: vi.fn(),
    rpc: vi.fn(),
    maybeSingle,
    insert,
    getListeningExercise: vi.fn(),
    canOpenListening: vi.fn(),
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          eq: vi.fn(() => ({ maybeSingle })),
        })),
      })),
      insert,
    })),
  };
});

vi.mock("@/utils/supabase/server", () => ({
  createClient: vi.fn(() => ({
    auth: { getUser: mocks.getUser },
    rpc: mocks.rpc,
    from: mocks.from,
  })),
}));

const exercise: ListeningExercise = {
  id: "starters_listening_001",
  level: "starters",
  order: 1,
  title: "Test",
  scenario: "Test",
  estimated_minutes: 4,
  grammar_ids: ["starters_grammar_003"],
  instruction: "Listen and complete.",
  audio_text: "seven grey 12 three",
  passage: "{{b1}} {{b2}} {{b3}} {{b4}}",
  transcript: "seven grey 12 three",
  blanks: [
    { id: "b1", cue: "age", category: "age", accepted_answers: ["seven", "7"] },
    { id: "b2", cue: "colour", category: "color", accepted_answers: ["grey", "gray"] },
    { id: "b3", cue: "house number", category: "address", accepted_answers: ["12"] },
    { id: "b4", cue: "number of books", category: "number", accepted_answers: ["three", "3"] },
  ],
};

vi.mock("@/lib/content/listening-loader", () => ({ getListeningExercise: mocks.getListeningExercise }));

vi.mock("@/lib/access/paid-access", () => ({ canOpenListening: mocks.canOpenListening }));

const answers = exercise.blanks.map((blank) => ({ blankId: blank.id, value: blank.accepted_answers[0] }));

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getUser.mockResolvedValue({ data: { user: { id: "user-1" } } });
  mocks.getListeningExercise.mockReturnValue(exercise);
  mocks.canOpenListening.mockResolvedValue(true);
  mocks.rpc.mockResolvedValue({ error: null });
  mocks.maybeSingle.mockResolvedValue({ data: null, error: null });
  mocks.insert.mockResolvedValue({ error: null });
});

describe("submitListeningAnswers", () => {
  it("scores on the server, records the attempt, revalidates pages and returns the transcript", async () => {
    const result = await submitListeningAnswers(exercise.id, answers);
    expect(result).toMatchObject({ score: 100, correctCount: 4, completed: true, transcript: exercise.transcript });
    expect(mocks.rpc).toHaveBeenCalledWith("record_listening_attempt", {
      p_listening_id: exercise.id,
      p_score: 100,
    });
    expect(revalidatePath).toHaveBeenCalledWith("/listening");
    expect(revalidatePath).toHaveBeenCalledWith("/listening/starters");
  });

  it("rejects unauthenticated, missing, locked and malformed submissions", async () => {
    mocks.getUser.mockResolvedValueOnce({ data: { user: null } });
    await expect(submitListeningAnswers(exercise.id, answers)).rejects.toThrow("Not authenticated");

    mocks.getListeningExercise.mockReturnValueOnce(undefined);
    await expect(submitListeningAnswers("missing", answers)).rejects.toThrow("not found");

    mocks.canOpenListening.mockResolvedValueOnce(false);
    await expect(submitListeningAnswers(exercise.id, answers)).rejects.toThrow("locked");

    await expect(submitListeningAnswers(exercise.id, answers.slice(1))).rejects.toThrow("Invalid listening answers");
    expect(mocks.rpc).not.toHaveBeenCalled();
  });

  it("does not report success when the progress RPC fails", async () => {
    mocks.rpc.mockResolvedValue({ error: { message: "database unavailable" } });
    await expect(submitListeningAnswers(exercise.id, answers)).rejects.toThrow("Failed to save listening progress");
  });
});

describe("startListening", () => {
  it("creates in-progress state only when no row exists", async () => {
    await startListening(exercise.id);
    expect(mocks.insert).toHaveBeenCalledWith(expect.objectContaining({
      user_id: "user-1",
      listening_id: exercise.id,
      status: "in_progress",
    }));

    vi.clearAllMocks();
    mocks.getListeningExercise.mockReturnValue(exercise);
    mocks.canOpenListening.mockResolvedValue(true);
    mocks.getUser.mockResolvedValue({ data: { user: { id: "user-1" } } });
    mocks.maybeSingle.mockResolvedValue({ data: { status: "completed" }, error: null });
    await startListening(exercise.id);
    expect(mocks.insert).not.toHaveBeenCalled();
  });

  it("fails closed when the progress read fails", async () => {
    mocks.maybeSingle.mockResolvedValue({ data: null, error: { message: "network error" } });
    await startListening(exercise.id);
    expect(mocks.insert).not.toHaveBeenCalled();
  });
});
