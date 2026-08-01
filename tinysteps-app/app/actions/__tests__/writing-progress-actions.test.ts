import { beforeEach, describe, expect, it, vi } from "vitest";
import { revalidatePath } from "next/cache";
import type { WritingExercise } from "@/lib/types/content-types";
import { startWriting, submitWritingAnswers } from "../writing-progress-actions";

vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));

const mocks = vi.hoisted(() => {
  const maybeSingle = vi.fn();
  const insert = vi.fn();
  return {
    getUser: vi.fn(),
    rpc: vi.fn(),
    maybeSingle,
    insert,
    getWritingExercise: vi.fn(),
    canOpenWriting: vi.fn(),
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

const exercise: WritingExercise = {
  id: "starters_writing_001",
  level: "starters",
  order: 1,
  title: "Test",
  scenario: "Test",
  estimated_minutes: 4,
  grammar_ids: ["starters_grammar_003"],
  instruction: "Complete.",
  passage: "{{b1}} {{b2}} {{b3}} {{b4}} {{b5}}",
  blanks: ["is", "am", "are", "is", "are"].map((answer, index) => ({
    id: `b${index + 1}`,
    cue: "be",
    accepted_answers: [answer],
  })),
};

vi.mock("@/lib/content/writing-loader", () => ({ getWritingExercise: mocks.getWritingExercise }));

vi.mock("@/lib/access/paid-access", () => ({ canOpenWriting: mocks.canOpenWriting }));

const answers = exercise.blanks.map((blank) => ({ blankId: blank.id, value: blank.accepted_answers[0] }));

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getUser.mockResolvedValue({ data: { user: { id: "user-1" } } });
  mocks.getWritingExercise.mockReturnValue(exercise);
  mocks.canOpenWriting.mockResolvedValue(true);
  mocks.rpc.mockResolvedValue({ error: null });
  mocks.maybeSingle.mockResolvedValue({ data: null, error: null });
  mocks.insert.mockResolvedValue({ error: null });
});

describe("submitWritingAnswers", () => {
  it("scores on the server, records the attempt and revalidates writing pages", async () => {
    const result = await submitWritingAnswers(exercise.id, answers);
    expect(result).toMatchObject({ score: 100, correctCount: 5, completed: true });
    expect(mocks.rpc).toHaveBeenCalledWith("record_writing_attempt", {
      p_writing_id: exercise.id,
      p_score: 100,
    });
    expect(revalidatePath).toHaveBeenCalledWith("/writing");
    expect(revalidatePath).toHaveBeenCalledWith("/writing/starters");
  });

  it("rejects unauthenticated, missing, locked and malformed submissions", async () => {
    mocks.getUser.mockResolvedValueOnce({ data: { user: null } });
    await expect(submitWritingAnswers(exercise.id, answers)).rejects.toThrow("Not authenticated");

    mocks.getWritingExercise.mockReturnValueOnce(undefined);
    await expect(submitWritingAnswers("missing", answers)).rejects.toThrow("not found");

    mocks.canOpenWriting.mockResolvedValueOnce(false);
    await expect(submitWritingAnswers(exercise.id, answers)).rejects.toThrow("locked");

    await expect(submitWritingAnswers(exercise.id, answers.slice(1))).rejects.toThrow("Invalid writing answers");
    expect(mocks.rpc).not.toHaveBeenCalled();
  });

  it("does not report success when the progress RPC fails", async () => {
    mocks.rpc.mockResolvedValue({ error: { message: "database unavailable" } });
    await expect(submitWritingAnswers(exercise.id, answers)).rejects.toThrow("Failed to save writing progress");
  });
});

describe("startWriting", () => {
  it("creates in-progress state only when no row exists", async () => {
    await startWriting(exercise.id);
    expect(mocks.insert).toHaveBeenCalledWith(expect.objectContaining({
      user_id: "user-1",
      writing_id: exercise.id,
      status: "in_progress",
    }));

    vi.clearAllMocks();
    mocks.getWritingExercise.mockReturnValue(exercise);
    mocks.canOpenWriting.mockResolvedValue(true);
    mocks.getUser.mockResolvedValue({ data: { user: { id: "user-1" } } });
    mocks.maybeSingle.mockResolvedValue({ data: { status: "completed" }, error: null });
    await startWriting(exercise.id);
    expect(mocks.insert).not.toHaveBeenCalled();
  });

  it("fails closed when the progress read fails", async () => {
    mocks.maybeSingle.mockResolvedValue({ data: null, error: { message: "network error" } });
    await startWriting(exercise.id);
    expect(mocks.insert).not.toHaveBeenCalled();
  });
});
