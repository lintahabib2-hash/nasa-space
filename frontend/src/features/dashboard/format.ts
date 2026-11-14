const UNIT_LABEL: Record<string, string> = {
  hours: "h",
  score_1_5: "/ 5",
  bpm: "bpm",
  mmHg: "mmHg",
  "mg/dL": "mg/dL",
  degC: "°C",
  "uSv/day": "µSv/day",
  minutes: "min",
};

export function unitLabel(units: string): string {
  return UNIT_LABEL[units] ?? units;
}

export function fmtValue(value: number | null | undefined, units?: string): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const rounded = Math.abs(value) >= 100 ? Math.round(value).toString() : String(Math.round(value * 10) / 10);
  return units ? `${rounded} ${unitLabel(units)}` : rounded;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", timeZone: "UTC" });
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return `${d.toISOString().slice(0, 16).replace("T", " ")} UTC`;
}

export function humanize(token: string): string {
  return token.replace(/_/g, " ");
}
