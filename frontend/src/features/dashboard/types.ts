// Types the Member 3 UI consumes.
// `BaselineResult` mirrors Member 2's get_baseline_result() output (member2/analytics.py).
// Fields marked "requested" are extra fields the UI can use but does not require.
// When Member 6 publishes shared/schemas, move these to src/types/contracts.ts.

export type ProvenanceKind =
  | "nasa_measured"
  | "analog_measured"
  | "external_earth"
  | "simulated"
  | "manually_entered"
  | "crew_self_report"
  | "environment_measured"
  | (string & {});

export type QualityState = "valid" | "missing" | "outlier" | "unknown" | (string & {});

export interface ReferenceBand {
  low: number;
  high: number;
  basis: string;
}

export interface BaselineResult {
  subject_id: string;
  measurement: string;
  current_value: number | null;
  units: string;
  source_id: string;
  study_id: string;
  provenance_kind: ProvenanceKind;
  history_count: number;
  rejected_history_count: number;
  baseline_value: number | null;
  robust_z: number | null;
  status: string;
  quality_state: string;
  reasons: string[];
  severity_basis: string;
  not_medical_diagnosis: true;
  reference_count?: number;
  reference_start_utc?: string;
  reference_end_utc?: string;
  timestamp_utc?: string;
  analysis_context?: string;
  /** requested from Member 2: shaded band for the trend chart */
  reference_band?: ReferenceBand;
  /** fixtures only: which code produced this result */
  result_origin?: string;
}

export interface SeriesPoint {
  timestamp_utc: string;
  value: number | null;
  quality_state: QualityState;
}

export interface IndicatorData {
  measurement: string;
  units: string;
  source_id: string;
  provenance_kind: ProvenanceKind;
  study_id: string;
  result: BaselineResult;
  series: SeriesPoint[];
}

export interface CrewBundle {
  schema: string;
  subject_id: string;
  display_name: string;
  scenario: string;
  scenario_label: string;
  source_id: string;
  provenance_kind: ProvenanceKind;
  study_id: string;
  as_of_utc: string;
  generated_by: string;
  notice?: string;
  indicators: IndicatorData[];
}

export interface SourceRef {
  title: string;
  url: string | null;
  publisher: string;
  url_note?: string;
}

export interface RegionCard {
  label: string;
  function: string;
  spaceflight_effects: string;
  hazards: string[];
  indicators: string[];
  sources: string[];
}

export interface IndicatorCard {
  label: string;
  region: string;
  how_measured: string;
  why: string;
  self_care: string[];
  contact_when: string[];
  sources: string[];
  limitations: string[];
}

export interface EnvironmentCard {
  label: string;
  setting: string;
  one_way_delay: string;
  reply_expectation: string;
  guidance: string;
}

export interface Knowledge {
  schema: string;
  status: string;
  notice: string;
  sources: Record<string, SourceRef>;
  hazards: Record<string, string>;
  regions: Record<string, RegionCard>;
  indicators: Record<string, IndicatorCard>;
  environments: Record<string, EnvironmentCard>;
  environment_sources: string[];
  environment_note: string;
}

export type DataMode = "fixtures" | "api";
