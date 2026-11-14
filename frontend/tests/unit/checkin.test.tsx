import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CheckInPage } from "../../src/features/checkin/CheckInPage";
import { buildCheckin, FIELDS, localDay } from "../../src/features/checkin/checkinSchema";
import { readRecords, STORAGE_KEY } from "../../src/features/checkin/checkinStore";
import { calculateStreak } from "../../src/features/gamification/streakLogic";
import { buildReactionRecord, median } from "../../src/features/reaction-time/reactionLogic";
import { ReactionTimeTask } from "../../src/features/reaction-time/ReactionTimeTask";

const base = { sleep_duration: "7.5", mood: "4", stress: "2", exercise_minutes: "30" };
const ENVELOPE = ["source_id", "provenance_kind", "subject_id", "study_id", "measurement", "value", "units", "timestamp_utc", "quality_state", "reference_url"];

describe("buildCheckin (ported from Member 5's app.js)", () => {
  it("builds a record with full observation envelopes, manually_entered provenance and a subject_id", () => {
    const r = buildCheckin(base, { now: new Date("2026-11-14T10:00:00Z") });
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    const sleep = r.record.indicators.sleep_duration;
    for (const k of ENVELOPE) expect(sleep).toHaveProperty(k);
    expect(sleep).toMatchObject({ measurement: "sleep_duration", units: "hours", value: 7.5, provenance_kind: "manually_entered", quality_state: "valid" });
    expect(sleep.subject_id).toBeTruthy();
    expect(r.record.timestamp_utc).toBe("2026-11-14T10:00:00.000Z");
  });

  it.each([
    ["sleep above 24 h", { sleep_duration: "25" }],
    ["negative sleep", { sleep_duration: "-1" }],
    ["mood out of range", { mood: "6" }],
    ["fractional exercise", { exercise_minutes: "10.5" }],
    ["heart rate 300", { resting_heart_rate: "300" }],
    ["non-numeric value", { body_temperature: "abc" }],
    ["missing required sleep", { sleep_duration: "" }],
  ])("rejects %s", (_name, override) => {
    expect(buildCheckin({ ...base, ...override }).ok).toBe(false);
  });

  it("requires both blood-pressure values together", () => {
    const r = buildCheckin({ ...base, systolic_bp: "120" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.message).toMatch(/both systolic and diastolic/);
  });

  it("requires systolic greater than diastolic", () => {
    const r = buildCheckin({ ...base, systolic_bp: "80", diastolic_bp: "90" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.message).toMatch(/greater than diastolic/);
  });

  it("stores optional vitals only when entered", () => {
    const r = buildCheckin({ ...base, body_temperature: "36.8", blood_glucose: "95" });
    expect(r.ok && Object.keys(r.record.indicators).sort()).toEqual(
      ["blood_glucose", "body_temperature", "exercise_minutes", "mood", "sleep_duration", "stress"],
    );
  });

  it("uses measurement names the dashboard knows about", async () => {
    const { KNOWLEDGE } = await import("../../src/features/dashboard/dataSource");
    const known = FIELDS.filter((f) => KNOWLEDGE.indicators[f.measurement]).map((f) => f.measurement);
    expect(known).toEqual(expect.arrayContaining(["sleep_duration", "mood", "stress", "exercise_minutes", "resting_heart_rate", "systolic_bp", "diastolic_bp", "blood_glucose", "body_temperature"]));
  });
});

describe("reaction logic", () => {
  it("computes the median of five rounds", () => {
    expect(median([300, 250, 400, 280, 260])).toBe(280);
    expect(median([200, 300])).toBe(250);
  });

  it("builds a record with task, score, method, timestamp and provenance", () => {
    const r = buildReactionRecord([300, 250, 400, 280, 260], new Date("2026-11-14T10:00:00Z"));
    expect(r).toMatchObject({ task: "five_round_visual_response", score: 280, units: "milliseconds", provenance_kind: "manually_entered", timestamp_utc: "2026-11-14T10:00:00.000Z" });
    expect(r.method).toMatch(/browser_performance_api/);
  });
});

describe("streaks", () => {
  const today = new Date(2026, 10, 14, 12);
  const day = (offset: number) => localDay(new Date(2026, 10, 14 + offset, 12));
  it("counts consecutive days including today", () => {
    expect(calculateStreak([day(0), day(-1), day(-2), day(-4)], today)).toBe(3);
  });
  it("does not break mid-day before today's check-in", () => {
    expect(calculateStreak([day(-1), day(-2)], today)).toBe(2);
  });
  it("is zero with a gap before yesterday", () => {
    expect(calculateStreak([day(-3)], today)).toBe(0);
  });
});

describe("ReactionTimeTask", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("detects an early tap as 'Too soon' and saves nothing (bug fixed from original)", () => {
    const onSave = vi.fn();
    render(<ReactionTimeTask onSave={onSave} />);
    fireEvent.click(screen.getByRole("button", { name: /Start activity/ }));
    const target = screen.getByRole("button", { name: /Target: wait/ });
    expect(target).toBeEnabled();
    fireEvent.click(target);
    expect(screen.getByText(/Too soon/)).toBeInTheDocument();
    expect(onSave).not.toHaveBeenCalled();
  });

  it("completes five rounds and saves the median", () => {
    const onSave = vi.fn();
    render(<ReactionTimeTask onSave={onSave} />);
    fireEvent.click(screen.getByRole("button", { name: /Start activity/ }));
    for (let i = 0; i < 5; i++) {
      act(() => { vi.advanceTimersByTime(3000); }); // target appears
      fireEvent.click(screen.getByRole("button", { name: /Target: tap now/ }));
      act(() => { vi.advanceTimersByTime(600); }); // next round / finish
    }
    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onSave.mock.calls[0][0].rounds).toHaveLength(5);
    expect(screen.getByText(/Median response/)).toBeInTheDocument();
  });
});

describe("CheckInPage", () => {
  beforeEach(() => localStorage.clear());

  it("saves a check-in locally, shows it in history and starts a streak", async () => {
    render(<CheckInPage />);
    await userEvent.type(screen.getByLabelText(/^Sleep/), "7.5");
    await userEvent.selectOptions(screen.getByLabelText(/^Mood/), "4");
    await userEvent.selectOptions(screen.getByLabelText(/^Stress/), "2");
    await userEvent.type(screen.getByLabelText(/^Exercise/), "30");
    await userEvent.click(screen.getByRole("button", { name: /Save today/ }));

    expect(screen.getByText("Check-in saved on this device.")).toBeInTheDocument();
    expect(readRecords().checkins).toHaveLength(1);
    expect(screen.getByTestId("history")).toHaveTextContent("7.5 h sleep");
    expect(screen.getByTestId("streak")).toHaveTextContent("1 day streak");
  });

  it("shows a clear error and saves nothing for invalid input", async () => {
    render(<CheckInPage />);
    await userEvent.type(screen.getByLabelText(/^Sleep/), "30");
    await userEvent.click(screen.getByRole("button", { name: /Save today/ }));
    expect(screen.getByRole("alert")).toHaveTextContent(/Sleep must be a number from 0 to 24/);
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it("explains why each core measurement is taken", async () => {
    // Text comes from Member 1's knowledge file, so read it from there rather than hard-coding it.
    const { KNOWLEDGE } = await import("../../src/features/dashboard/dataSource");
    const why = KNOWLEDGE.indicators.sleep_duration.why;
    expect(why).toBeTruthy();
    render(<CheckInPage />);
    expect(screen.getByText(`Why: ${why}`, { exact: false })).toBeInTheDocument();
  });
});
