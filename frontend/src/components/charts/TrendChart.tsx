import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipProps,
} from "recharts";
import { fmtDate, fmtDateTime, fmtValue, unitLabel } from "../../features/dashboard/format";
import type { ReferenceBand, SeriesPoint } from "../../features/dashboard/types";

interface Props {
  label: string;
  units: string;
  series: SeriesPoint[];
  baseline: number | null;
  band?: ReferenceBand;
}

interface Row {
  t: number;
  ts: string;
  value: number | null;
  quality: string;
  isLatest: boolean;
  /** Synthetic break inserted into a long time gap. Plotted as a line break only, never listed. */
  gap?: boolean;
}

const DAY_MS = 86_400_000;
/** A gap this many times longer than the typical spacing breaks the line. */
const GAP_FACTOR = 3;
const TICKS = 5;

function medianOf(xs: number[]): number {
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

/** Up to TICKS ticks spread evenly in time, each snapped to a real reading. */
function timeTicks(ts: number[]): number[] {
  if (ts.length <= TICKS) return ts;
  const lo = ts[0];
  const span = ts[ts.length - 1] - lo;
  const picked = new Set<number>();
  for (let k = 0; k < TICKS; k++) {
    const target = lo + (span * k) / (TICKS - 1);
    picked.add(ts.reduce((best, x) => (Math.abs(x - target) < Math.abs(best - target) ? x : best), ts[0]));
  }
  return [...picked].sort((a, b) => a - b);
}

function TooltipBody({ active, payload, units, fmt }: TooltipProps<number, string> & { units: string; fmt: (iso: string) => string }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload as Row;
  if (row.gap) return null;
  return (
    <div className="trend-tooltip">
      <div>{fmt(row.ts)}</div>
      {row.value === null ? <div><b>Missing</b> (no reading)</div> : <div><b>{fmtValue(row.value, units)}</b></div>}
      {row.quality !== "valid" && row.value !== null && <div className="muted">quality: {row.quality}</div>}
    </div>
  );
}

/** One indicator over time, with the API-provided personal reference band shaded. */
export function TrendChart({ label, units, series, baseline, band }: Props) {
  // Readings are placed on a real time axis, so uneven spacing (e.g. 18 Oct then 10 Nov) shows as it is.
  const rows: Row[] = series
    .map((p) => ({ t: Date.parse(p.timestamp_utc), ts: p.timestamp_utc, value: p.value, quality: p.quality_state, isLatest: false }))
    .filter((r) => Number.isFinite(r.t))
    .sort((a, b) => a.t - b.t);
  if (rows.length) rows[rows.length - 1].isLatest = true;

  const times = rows.map((r) => r.t);
  const steps = times.slice(1).map((t, i) => t - times[i]).filter((d) => d > 0);
  const typicalStep = steps.length ? medianOf(steps) : DAY_MS;
  // Daily data shows dates; anything finer (e.g. 5-minute instrument data) also shows the time.
  const subDaily = typicalStep < DAY_MS * 0.9;
  const fmtPoint = subDaily ? fmtDateTime : fmtDate;
  const unitWord = subDaily ? "readings" : "days";

  // Break the line across long unrecorded periods instead of drawing a straight bridge.
  const plotRows: Row[] = [];
  let breaks = 0;
  rows.forEach((r, i) => {
    if (i > 0 && r.t - rows[i - 1].t > typicalStep * GAP_FACTOR) {
      const mid = (r.t + rows[i - 1].t) / 2;
      plotRows.push({ t: mid, ts: new Date(mid).toISOString(), value: null, quality: "gap", isLatest: false, gap: true });
      breaks += 1;
    }
    plotRows.push(r);
  });

  const values = rows.flatMap((r) => (r.value === null ? [] : [r.value]));
  const missing = rows.filter((r) => r.value === null).length;

  // Presentation only: fit the y-axis to the readings and median. The band is clipped
  // to that range, so a wide band on a coarse scale (e.g. 1–5) cannot squash the data.
  const extent = [...values, ...(baseline !== null ? [baseline] : [])];
  const lo = extent.length ? Math.min(...extent) : 0;
  const hi = extent.length ? Math.max(...extent) : 1;
  const pad = (hi - lo || Math.abs(hi) || 1) * 0.15;
  const domain: [number, number] = [Math.floor((lo - pad) * 10) / 10, Math.ceil((hi + pad) * 10) / 10];

  const latest = rows[rows.length - 1];
  const summary =
    `${label}, ${rows.length} ${unitWord}` +
    (rows.length ? ` from ${fmtPoint(rows[0].ts)} to ${fmtPoint(latest.ts)}` : "") +
    `. Latest ${latest?.value === null ? "missing" : fmtValue(latest?.value, units)}` +
    (band ? `; personal reference band ${fmtValue(band.low)} to ${fmtValue(band.high, units)}` : "; no reference band available") +
    (missing ? `; ${missing} missing ${unitWord}` : "") +
    (breaks ? `; ${breaks} long ${breaks === 1 ? "gap" : "gaps"} with no readings.` : ".");

  return (
    <div className="trend">
      <div className="trend__plot" role="img" aria-label={summary}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={plotRows} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            {band && (
              <ReferenceArea y1={band.low} y2={band.high} fill="var(--band)" stroke="var(--band-edge)" strokeDasharray="2 3" ifOverflow="hidden" />
            )}
            {baseline !== null && (
              <ReferenceLine y={baseline} stroke="var(--text-muted)" strokeDasharray="5 4" strokeWidth={1.5} />
            )}
            <XAxis
              dataKey="t"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              ticks={timeTicks(times)}
              tickFormatter={(t: number) => {
                const iso = new Date(t).toISOString();
                return subDaily && times[times.length - 1] - times[0] < 2 * DAY_MS ? `${iso.slice(11, 16)}` : fmtDate(iso);
              }}
              tick={{ fontSize: 11, fill: "var(--text-muted)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border)" }}
              minTickGap={24}
            />
            <YAxis domain={domain} tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} width={44} tickCount={4} />
            <Tooltip
              content={<TooltipBody units={units} fmt={fmtPoint} />}
              cursor={{ stroke: "var(--text-muted)", strokeWidth: 1, strokeDasharray: "3 3" }}
              isAnimationActive={false}
            />
            <Line
              type="linear"
              dataKey="value"
              stroke="var(--series)"
              strokeWidth={2}
              connectNulls={false}
              isAnimationActive={false}
              dot={(props: { cx?: number; cy?: number; index?: number; payload?: Row }) => {
                const { cx, cy, payload, index } = props;
                if (cx === undefined || cy === undefined || !payload || payload.value === null || (!payload.isLatest && plotRows.length > 120)) {
                  return <g key={`d${index}`} />; // dense series (e.g. 300 instrument points): line only, latest still marked
                }
                return payload.isLatest ? (
                  <circle key={`d${index}`} cx={cx} cy={cy} r={6} fill="var(--series)" stroke="var(--surface)" strokeWidth={2.5} />
                ) : (
                  <circle key={`d${index}`} cx={cx} cy={cy} r={3.5} fill="var(--series)" stroke="var(--surface)" strokeWidth={1.5} />
                );
              }}
              activeDot={{ r: 6, stroke: "var(--surface)", strokeWidth: 2 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="trend__caption">
        {band ? "Shaded: personal reference band from the analytics API. " : "No reference band available. "}
        {baseline !== null && "Dashed: personal median. "}
        {latest?.value === null ? "Latest reading is missing." : "Large dot: latest reading."}
        {missing > 0 && ` ${missing} of ${rows.length} ${unitWord} missing (gaps in line).`}
        {breaks > 0 && ` Line breaks where no readings were recorded for a long period.`}
      </div>
      <details className="table-view">
        <summary>Show data table</summary>
        <div className="data-table-wrap" tabIndex={0}>
          <table className="data-table">
            <caption className="sr-only">{label} readings</caption>
            <thead>
              <tr><th scope="col">{subDaily ? "Time (UTC)" : "Date (UTC)"}</th><th scope="col">Value ({unitLabel(units)})</th><th scope="col">Quality</th></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={`${r.ts}-${i}`}>
                  <td>{fmtPoint(r.ts)}</td>
                  <td>{r.value === null ? "—" : fmtValue(r.value)}</td>
                  <td>{r.quality}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
