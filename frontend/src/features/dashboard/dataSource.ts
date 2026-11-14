
// Loads dashboard data in one of two modes:
//   fixtures: bundled SIMULATED scenarios. Works offline and on a static host.
//   api:      Member 2's localhost API (prototypes/offline_research/offline_api.py), via the Vite /api proxy.
// Member 6 can swap this for src/services/apiClient.ts once it exists.

import stable from "./fixtures/crew_01_stable.json";
import drift from "./fixtures/crew_02_gradual_drift.json";
import missing from "./fixtures/crew_03_missing_data.json";
import reviewedKnowledge from "../../../../shared/knowledge/knowledge.json";
import type { BaselineResult, CrewBundle, DataMode, Knowledge, SeriesPoint } from "./types";

export const FIXTURE_BUNDLES: CrewBundle[] = [stable, drift, missing] as CrewBundle[];

// Member 1's reviewed science knowledge file.
export const KNOWLEDGE: Knowledge = reviewedKnowledge as Knowledge;

export function configuredMode(): DataMode {
  return import.meta.env.VITE_DATA_MODE === "api" ? "api" : "fixtures";
}

interface CheckinRecord {
  subject_id: string;
  study_id: string;
  source_id: string;
  provenance_kind: string;
  measurement: string;
  value: number;
  units: string;
  timestamp_utc: string;
}

async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { signal, headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`${url} returned HTTP ${res.status}`);
  return (await res.json()) as T;
}

/** Builds a one-indicator bundle (sleep) from Member 2's live API. */
export async function loadApiBundle(subjectId: string, signal?: AbortSignal): Promise<CrewBundle> {
  const q = `subject_id=${encodeURIComponent(subjectId)}`;
  const [{ records }, latest] = await Promise.all([
    getJson<{ records: CheckinRecord[] }>(`/api/checkins?${q}`, signal),
    getJson<Partial<BaselineResult> & { status: string; reasons: string[] }>(`/api/analytics/latest?${q}`, signal),
  ]);
  const sleep = records.filter((r) => r.measurement === "sleep_duration");
  const latestRecord = sleep[sleep.length - 1];
  const series: SeriesPoint[] = sleep.map((r) => ({
    timestamp_utc: r.timestamp_utc,
    value: r.value,
    quality_state: "valid",
  }));
  const result: BaselineResult = {
    subject_id: subjectId,
    measurement: "sleep_duration",
    current_value: latestRecord?.value ?? null,
    units: "hours",
    source_id: latestRecord?.source_id ?? "local_checkin",
    study_id: latestRecord?.study_id ?? "unknown",
    provenance_kind: latestRecord?.provenance_kind ?? "unknown",
    history_count: Math.max(sleep.length - 1, 0),
    rejected_history_count: 0,
    baseline_value: null,
    robust_z: null,
    quality_state: "unknown",
    severity_basis: "unvalidated_demo_statistical_rule",
    not_medical_diagnosis: true,
    ...latest,
  };
  return {
    schema: "crew-vitals/ui-bundle@0.1",
    subject_id: subjectId,
    display_name: subjectId,
    scenario: "local_api",
    scenario_label: "Local API (Member 2): self-reported sleep only",
    source_id: result.source_id,
    provenance_kind: result.provenance_kind,
    study_id: result.study_id,
    as_of_utc: new Date().toISOString(),
    generated_by: "prototypes/offline_research/offline_api.py",
    indicators: [
      {
        measurement: "sleep_duration",
        units: "hours",
        source_id: result.source_id,
        provenance_kind: result.provenance_kind,
        study_id: result.study_id,
        result,
        series,
      },
    ],
  };
}
