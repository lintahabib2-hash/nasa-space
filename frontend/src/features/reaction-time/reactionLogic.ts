// Reaction-time activity logic (Member 5). Personal tracking only, not a validated cognitive test.
// Browser and device timing vary, so scores are not standardized (docs/reaction-time-limitations.md).
import { DEFAULT_SUBJECT_ID, newId } from "../checkin/checkinSchema";

export const ROUNDS = 5;
export const MIN_WAIT_MS = 900;
export const MAX_EXTRA_WAIT_MS = 1900;

export interface ReactionRecord {
  record_id: string;
  source_id: "crew-vitals-reaction-activity";
  provenance_kind: "manually_entered";
  subject_id: string;
  study_id: string;
  measurement: "visual_reaction_time_median";
  task: "five_round_visual_response";
  score: number;
  value: number;
  units: "milliseconds";
  rounds: number[];
  timestamp_utc: string;
  quality_state: "valid";
  reference_url: null;
  method: "browser_performance_api; click_or_touch";
}

/** Median of the rounds, rounded to whole milliseconds. */
export function median(values: number[]): number {
  if (values.length === 0) throw new Error("No readings");
  const s = [...values].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : Math.round((s[mid - 1] + s[mid]) / 2);
}

export function buildReactionRecord(rounds: number[], now: Date = new Date(), subjectId = DEFAULT_SUBJECT_ID): ReactionRecord {
  const score = median(rounds);
  return {
    record_id: newId("reaction"),
    source_id: "crew-vitals-reaction-activity",
    provenance_kind: "manually_entered",
    subject_id: subjectId,
    study_id: "local_checkin",
    measurement: "visual_reaction_time_median",
    task: "five_round_visual_response",
    score,
    value: score,
    units: "milliseconds",
    rounds: [...rounds],
    timestamp_utc: now.toISOString(),
    quality_state: "valid",
    reference_url: null,
    method: "browser_performance_api; click_or_touch",
  };
}

export function randomWait(rand: () => number = Math.random): number {
  return MIN_WAIT_MS + rand() * MAX_EXTRA_WAIT_MS;
}
