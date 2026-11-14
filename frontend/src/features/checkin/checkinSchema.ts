// Daily check-in contract and validation (Member 5).
// Ported from Linta's nasa-space-upload app (app.js). Input bounds and messages are
// kept as written. These are input-format bounds, not health or safety thresholds.
// Measurement names match Member 2's analytics and the dashboard
// (e.g. sleep_duration, resting_heart_rate, systolic_bp). JSON Schema: shared/schemas/checkin.schema.json

export const CHECKIN_SCHEMA = "crew-vitals/checkin@1";
export const SOURCE_ID = "crew-vitals-daily-check-in";
export const STUDY_ID = "local_checkin";
export const PROVENANCE = "manually_entered" as const;
export const DEFAULT_SUBJECT_ID = import.meta.env.VITE_SUBJECT_ID || "crew_01";

export type CollectionMethod = "self_reported" | "device_measured";

export interface Observation {
  source_id: string;
  provenance_kind: typeof PROVENANCE;
  subject_id: string;
  study_id: string;
  measurement: string;
  value: number;
  units: string;
  timestamp_utc: string;
  quality_state: "valid";
  reference_url: null;
}

export interface CheckinRecord {
  schema: typeof CHECKIN_SCHEMA;
  record_id: string;
  subject_id: string;
  timestamp_utc: string;
  local_day: string;
  method: CollectionMethod;
  provenance_kind: typeof PROVENANCE;
  source_id: string;
  indicators: Record<string, Observation>;
}

export interface FieldDef {
  measurement: string;
  label: string;
  units: string;
  unitLabel: string;
  min: number;
  max: number;
  step: number;
  integer: boolean;
  required: boolean;
  hint: string;
  group: "core" | "vitals";
  /** when set, render as a select with these labelled options */
  options?: { value: number; label: string }[];
}

export const FIELDS: FieldDef[] = [
  { measurement: "sleep_duration", label: "Sleep", units: "hours", unitLabel: "hours", min: 0, max: 24, step: 0.25, integer: false, required: true, group: "core", hint: "0–24 hours" },
  {
    measurement: "mood", label: "Mood", units: "score_1_5", unitLabel: "1–5", min: 1, max: 5, step: 1, integer: true, required: true, group: "core",
    hint: "Your own rating, no right answer",
    options: [
      { value: 1, label: "1 — Very low" }, { value: 2, label: "2 — Low" }, { value: 3, label: "3 — Okay" },
      { value: 4, label: "4 — Good" }, { value: 5, label: "5 — Very good" },
    ],
  },
  {
    measurement: "stress", label: "Stress", units: "score_1_5", unitLabel: "1–5", min: 1, max: 5, step: 1, integer: true, required: true, group: "core",
    hint: "1 = none, 5 = highest for you",
    options: [
      { value: 1, label: "1 — None" }, { value: 2, label: "2 — Low" }, { value: 3, label: "3 — Moderate" },
      { value: 4, label: "4 — High" }, { value: 5, label: "5 — Very high" },
    ],
  },
  { measurement: "exercise_minutes", label: "Exercise", units: "minutes", unitLabel: "minutes", min: 0, max: 1440, step: 1, integer: true, required: true, group: "core", hint: "0–1,440 minutes today" },
  { measurement: "resting_heart_rate", label: "Resting heart rate", units: "bpm", unitLabel: "bpm", min: 20, max: 250, step: 1, integer: true, required: false, group: "vitals", hint: "20–250 bpm" },
  { measurement: "body_temperature", label: "Body temperature", units: "degC", unitLabel: "°C", min: 25, max: 45, step: 0.1, integer: false, required: false, group: "vitals", hint: "25–45 °C" },
  { measurement: "oxygen_saturation", label: "Oxygen saturation", units: "percent", unitLabel: "%", min: 50, max: 100, step: 1, integer: true, required: false, group: "vitals", hint: "50–100%" },
  { measurement: "systolic_bp", label: "Blood pressure — systolic", units: "mmHg", unitLabel: "mmHg", min: 40, max: 300, step: 1, integer: true, required: false, group: "vitals", hint: "40–300 mmHg; enter with diastolic" },
  { measurement: "diastolic_bp", label: "Blood pressure — diastolic", units: "mmHg", unitLabel: "mmHg", min: 20, max: 200, step: 1, integer: true, required: false, group: "vitals", hint: "20–200 mmHg; enter with systolic" },
  { measurement: "blood_glucose", label: "Blood glucose", units: "mg/dL", unitLabel: "mg/dL", min: 10, max: 1000, step: 1, integer: true, required: false, group: "vitals", hint: "10–1,000 mg/dL" },
  { measurement: "radiation_badge_daily_dose", label: "Dosimeter badge reading", units: "uSv/day", unitLabel: "µSv/day", min: 0, max: 100000, step: 0.1, integer: false, required: false, group: "vitals", hint: "Copy today's badge reading" },
];

export type BuildResult =
  | { ok: true; record: CheckinRecord }
  | { ok: false; message: string; field?: string };

export function localDay(date: Date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function newId(prefix: string): string {
  const c = globalThis.crypto as Crypto | undefined;
  return c?.randomUUID ? c.randomUUID() : `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function observation(measurement: string, value: number, units: string, timestamp: string, subjectId: string): Observation {
  return {
    source_id: SOURCE_ID, provenance_kind: PROVENANCE, subject_id: subjectId, study_id: STUDY_ID,
    measurement, value, units, timestamp_utc: timestamp, quality_state: "valid", reference_url: null,
  };
}

/** Validates raw form strings and builds one check-in record. Only complete, valid check-ins are returned. */
export function buildCheckin(
  raw: Record<string, string | undefined>,
  opts: { now?: Date; method?: CollectionMethod; subjectId?: string } = {},
): BuildResult {
  const now = opts.now ?? new Date();
  const timestamp = now.toISOString();
  const subjectId = opts.subjectId ?? DEFAULT_SUBJECT_ID;
  const indicators: Record<string, Observation> = {};

  for (const f of FIELDS) {
    const text = (raw[f.measurement] ?? "").trim();
    if (text === "") {
      if (f.required) return { ok: false, field: f.measurement, message: `${f.label} is required.` };
      continue;
    }
    const value = Number(text);
    const bad = !Number.isFinite(value) || value < f.min || value > f.max || (f.integer && !Number.isInteger(value));
    if (bad) {
      const kind = f.integer ? "a whole number" : "a number";
      return { ok: false, field: f.measurement, message: `${f.label} must be ${kind} from ${f.min} to ${f.max} ${f.unitLabel}.` };
    }
    indicators[f.measurement] = observation(f.measurement, value, f.units, timestamp, subjectId);
  }

  const sys = indicators.systolic_bp;
  const dia = indicators.diastolic_bp;
  if (!!sys !== !!dia) {
    return { ok: false, field: sys ? "diastolic_bp" : "systolic_bp", message: "Enter both systolic and diastolic blood pressure, or leave both blank." };
  }
  if (sys && dia && sys.value <= dia.value) {
    return { ok: false, field: "systolic_bp", message: "Systolic blood pressure must be greater than diastolic." };
  }

  return {
    ok: true,
    record: {
      schema: CHECKIN_SCHEMA,
      record_id: newId("checkin"),
      subject_id: subjectId,
      timestamp_utc: timestamp,
      local_day: localDay(now),
      method: opts.method ?? "self_reported",
      provenance_kind: PROVENANCE,
      source_id: SOURCE_ID,
      indicators,
    },
  };
}
