import { describe, it, expect, vi, beforeEach } from "vitest";
import { submitLessonAnswers, startLesson } from "../lesson-progress-actions";
import * as checkAnswer from "@/lib/exercises/check-answer";
import * as lessonLoader from "@/lib/content/lesson-loader";

// Mock next/cache
vi.mock("next/cache", () => ({
  revalidatePath: vi.fn(),
}));

// Mock supabase server client
const mockRpc = vi.fn();
const mockGetUser = vi.fn();
const mockMaybeSingle = vi.fn();
const mockUpsert = vi.fn();
// Hoisted: vi.mock factories run before top-level consts are initialized.
const { mockCanOpenLesson } = vi.hoisted(() => ({ mockCanOpenLesson: vi.fn() }));

vi.mock("@/lib/access/paid-access", () => ({ canOpenLesson: mockCanOpenLesson }));

// Chainable query builder: .from().select().eq().eq().maybeSingle() and .from().upsert()
const mockFrom = vi.fn(() => ({
  select: vi.fn(() => ({
    eq: vi.fn(() => ({
      eq: vi.fn(() => ({ maybeSingle: mockMaybeSingle })),
    })),
  })),
  upsert: mockUpsert,
}));

vi.mock("@/utils/supabase/server", () => ({
  createClient: vi.fn(() => ({
    auth: { getUser: mockGetUser },
    rpc: mockRpc,
    from: mockFrom,
  })),
}));

// Mock content loader
vi.mock("@/lib/content/lesson-loader", () => ({
  getLesson: vi.fn(),
}));

describe("submitLessonAnswers", () => {
  beforeEach(() => {
    mockCanOpenLesson.mockResolvedValue(true);
  });

  it("computes score server-side and calls complete_lesson_rpc", async () => {
    // Setup mocks
    mockGetUser.mockResolvedValue({ data: { user: { id: "user-123" } } });

    // @ts-expect-error Mocked return value
    lessonLoader.getLesson.mockReturnValue({
      id: "lesson-1",
      exercises: [], // mocked, checkAnswer will handle it
    });

    vi.spyOn(checkAnswer, "computeScore").mockReturnValue({
      score: 85,
      correctCount: 17,
      totalItems: 20,
    });

    mockRpc.mockResolvedValue({ error: null });

    const result = await submitLessonAnswers("lesson-1", []);

    expect(result).toEqual({ score: 85, correctCount: 17, totalItems: 20 });
    expect(mockRpc).toHaveBeenCalledWith("complete_lesson_rpc", {
      p_lesson_id: "lesson-1",
      p_score: 85,
    });
  });

  it("refuses to score a lesson the learner has not unlocked", async () => {
    mockGetUser.mockResolvedValue({ data: { user: { id: "user-123" } } });
    mockRpc.mockClear();
    mockCanOpenLesson.mockResolvedValue(false);

    await expect(submitLessonAnswers("lesson-1", [])).rejects.toThrow("locked");
    expect(mockRpc).not.toHaveBeenCalled();
  });
});

describe("startLesson", () => {
  beforeEach(() => {
    mockGetUser.mockReset();
    mockMaybeSingle.mockReset();
    mockUpsert.mockReset();
    mockGetUser.mockResolvedValue({ data: { user: { id: "user-123" } } });
    mockUpsert.mockResolvedValue({ error: null });
    mockCanOpenLesson.mockResolvedValue(true);
  });

  it("does not record progress for a lesson the learner has not unlocked", async () => {
    mockCanOpenLesson.mockResolvedValue(false);
    mockMaybeSingle.mockResolvedValue({ data: null, error: null });

    await startLesson("lesson-1");

    expect(mockUpsert).not.toHaveBeenCalled();
  });

  it("does not write when the progress read fails (fail closed, not silently ignored)", async () => {
    mockMaybeSingle.mockResolvedValue({
      data: null,
      error: { message: "network error" },
    });

    await startLesson("lesson-1");

    expect(mockUpsert).not.toHaveBeenCalled();
  });

  it("never downgrades a completed lesson back to in_progress", async () => {
    mockMaybeSingle.mockResolvedValue({
      data: { status: "completed" },
      error: null,
    });

    await startLesson("lesson-1");

    expect(mockUpsert).not.toHaveBeenCalled();
  });

  it("does not re-upsert an already in_progress lesson", async () => {
    mockMaybeSingle.mockResolvedValue({
      data: { status: "in_progress" },
      error: null,
    });

    await startLesson("lesson-1");

    expect(mockUpsert).not.toHaveBeenCalled();
  });

  it("upserts in_progress when there is no existing row", async () => {
    mockMaybeSingle.mockResolvedValue({ data: null, error: null });

    await startLesson("lesson-1");

    expect(mockUpsert).toHaveBeenCalledWith(
      expect.objectContaining({
        user_id: "user-123",
        lesson_id: "lesson-1",
        status: "in_progress",
      }),
      { onConflict: "user_id, lesson_id" },
    );
  });

  it("upserts in_progress when the existing row is not_started", async () => {
    mockMaybeSingle.mockResolvedValue({
      data: { status: "not_started" },
      error: null,
    });

    await startLesson("lesson-1");

    expect(mockUpsert).toHaveBeenCalledTimes(1);
  });
});
