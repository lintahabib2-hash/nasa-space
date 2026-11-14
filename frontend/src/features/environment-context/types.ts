import type { ProvenanceKind, SeriesPoint } from "../dashboard/types";

/** One historical NASA environment series (Member 4's get_environment_series() shape). */
export interface EnvironmentSeries {
  source_id: string;
  registry_id?: string;
  source_url: string;
  citation: string;
  display_title: string;
  provenance_kind: ProvenanceKind;
  instrument: string;
  mission: string;
  location: string;
  population: string;
  subject_id: null;
  time_start_utc: string;
  time_end_utc: string;
  time_precision: string;
  row_count: number;
  series: { measurement: string; label: string; units: string; points: SeriesPoint[] }[];
  quality_summary: { missing_count: number; outlier_count: number; duplicate_timestamps_dropped?: number; notes: string };
  limitations: string[];
  is_fallback_not_ingested: boolean;
}
