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
import { fmtDate, fmtValue, unitLabel } from "../../features/dashboard/format";
import type { ReferenceBand, SeriesPoint } from "../../features/dashboard/types";

interface Props {
  label: string;
  units: string;
  series: SeriesPoint[];
  baseline: number | null;
  band?: ReferenceBand;
}

interface Row {
  ts: string;
  day: string;
  value: number | null;
  quality: string;
  isLatest: boolean;
}

function TooltipBody({ active, payload, units }: TooltipProps<number, string> & { units: string }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload as Row;
  return (
    <div className="trend-tooltip">
      <div>{fmtDate(row.ts)}</div>
      {row.value === null ? <div><b>Missing</b> (no reading)</div> : <div><b>{fmtValue(row.value, units)}</b></div>}
      {row.quality !== "valid" && row.value !== null && <div className="muted">quality: {row.quality}</div>}
    </div>
  );
}

/** One indicator over time, with the API-provided personal reference band shaded. */
export function TrendChart({ label, units, series, baseline, band }: Props) {
  const rows: Row[] = series.map((p, i) => ({
    ts: p.timestamp_utc,
    day: fmtDate(p.timestamp_utc),
    value: p.value,
    quality: p.quality_state,
    isLatest: i === series.length - 1,
  }));
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
    `${label}, ${rows.length} days. Latest ${latest?.value === null ? "missing" : fmtValue(latest?.value, units)}` +
    (band ? `; personal reference band ${fmtValue(band.low)} to ${fmtValue(band.high, units)}` : "; no reference band available") +
    (missing ? `; ${missing} missing days.` : ".");

  return (
    <div className="trend">
      <div className="trend__plot" role="img" aria-label={summary}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            {band && (
              <ReferenceArea y1={band.low} y2={band.high} fill="var(--band)" stroke="var(--band-edge)" strokeDasharray="2 3" ifOverflow="hidden" />
            )}
            {baseline !== null && (
              <ReferenceLine y={baseline} stroke="var(--text-muted)" strokeDasharray="5 4" strokeWidth={1.5} />
            )}
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickLine={false} axisLine={{ stroke: "var(--border)" }} minTickGap={24} />
            <YAxis domain={domain} tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} width={44} tickCount={4} />
            <Tooltip
              content={<TooltipBody units={units} />}
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
                if (cx === undefined || cy === undefined || !payload || payload.value === null) return <g key={`d${index}`} />;
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
        {missing > 0 && ` ${missing} of ${rows.length} days missing (gaps in line).`}
      </div>
      <details className="table-view">
        <summary>Show data table</summary>
        <div className="data-table-wrap" tabIndex={0}>
          <table className="data-table">
            <caption className="sr-only">{label} readings</caption>
            <thead>
              <tr><th scope="col">Date (UTC)</th><th scope="col">Value ({unitLabel(units)})</th><th scope="col">Quality</th></tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.ts}>
                  <td>{fmtDate(r.ts)}</td>
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
