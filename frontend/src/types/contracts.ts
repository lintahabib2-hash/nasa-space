// TS types mirroring shared/schemas
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// Source of truth: shared/schemas/*.schema.json (mirrored by backend/app/contracts/*.py).
// Types the dashboard already uses are re-exported from there so there is one import path.

export type {
  BaselineResult, CrewBundle, IndicatorData, Knowledge, SeriesPoint, ProvenanceKind, QualityState,
} from "../features/dashboard/types";

/** shared/schemas/envelope.schema.json: one measurement for one subject at one UTC instant. */
export interface Observation {
  source_id: string;
  provenance_kind: string;
  subject_id: string;
  study_id: string;
  measurement: string;
  /** null = missing reading (never NaN, never imputed) */
  value: number | null;
  units: string;
  timestamp_utc: string;
  quality_state: "valid" | "missing" | "outlier" | "unknown";
  reference_url?: string | null;
}

export const BASELINE_STATUSES = [
  "no_persistent_flag", "review", "insufficient_history", "insufficient_scale",
  "insufficient_persistence_history", "unknown", "no_observations",
] as const;
export type BaselineStatus = (typeof BASELINE_STATUSES)[number];

/** shared/schemas/api-response.schema.json: what /api/baseline returns (extra analytics fields allowed). */
export interface ApiBaselineResponse {
  subject_id: string;
  measurement: string;
  source_id?: string | null;
  study_id?: string | null;
  provenance_kind?: string | null;
  units?: string | null;
  status: BaselineStatus;
  quality_state: string;
  reasons: string[];
  severity_basis: string;
  not_medical_diagnosis: true;
  current_value: number | null;
  baseline_value: number | null;
  robust_z: number | null;
  history_count: number;
  rejected_history_count: number;
  [extra: string]: unknown;
}

/** shared/schemas/environment-series.schema.json: historical instrument data, never a crew record. */
export interface EnvironmentSeries {
  source_id: string;
  registry_id?: string;
  source_url?: string | null;
  citation: string;
  display_title?: string;
  provenance_kind: string;
  instrument: string;
  subject_id: null;
  limitations: string[];
  is_fallback_not_ingested?: boolean;
  quality_summary?: Record<string, unknown>;
  series: { measurement: string; label?: string; units: string; points: { timestamp_utc: string; value: number | null; quality_state: string }[] }[];
}

/** shared/schemas/snapshot-manifest.schema.json: frontend/public/data/manifest.json */
export interface SnapshotManifest {
  schema: "crew-vitals/snapshot@1";
  generated_by: string;
  contains_real_astronaut_data: false;
  files: Record<string, { sha256: string; bytes: number; api_path: string }>;
}

export function isApiBaselineResponse(x: unknown): x is ApiBaselineResponse {
  if (typeof x !== "object" || x === null) return false;
  const r = x as Record<string, unknown>;
  return (
    typeof r.subject_id === "string" && typeof r.measurement === "string" &&
    (BASELINE_STATUSES as readonly string[]).includes(r.status as string) &&
    Array.isArray(r.reasons) && r.reasons.length > 0 && r.not_medical_diagnosis === true
  );
}
