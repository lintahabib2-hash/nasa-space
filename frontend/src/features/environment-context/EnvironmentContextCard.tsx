// Separate historical NASA environment card (Member 4 data, D01 NASA OSDR EDA RR-1).
// Context only: no status chips, no personal reference band, never driven by the crew selector,
// never on the same time axis as crew charts.
import { TrendChart } from "../../components/charts/TrendChart";
import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import { fmtDate } from "../dashboard/format";
import type { EnvironmentSeries } from "./types";

export function EnvironmentContextCard({ data }: { data: EnvironmentSeries }) {
  const series = data.series[0];
  const shown = series?.points.length ?? 0;
  return (
    <section className="card env-card" aria-labelledby="env-context-title" data-testid="env-card">
      <div className="env-card__head">
        <div>
          <span className="eyebrow">Separate from crew data</span>
          <h2 id="env-context-title">Historical NASA environment context</h2>
        </div>
        <ProvenanceBadge kind={data.provenance_kind} />
      </div>

      <p className="env-card__lede">
        <strong>{data.display_title}.</strong> Historical instrument data from {data.location}, {fmtDate(data.time_start_utc)} to{" "}
        {fmtDate(data.time_end_utc)} {data.time_start_utc.slice(0, 4)}. Not this crew member&apos;s exposure or dose, and never
        compared with crew readings.
      </p>

      {data.is_fallback_not_ingested && (
        <p className="env-card__fallback">Static reference image, not ingested data.</p>
      )}

      {series && (
        <>
          <h3 className="env-card__series">{series.label}</h3>
          <TrendChart label={`${series.label} (historical, ${data.mission})`} units={series.units} series={series.points} baseline={null} />
        </>
      )}

      <dl className="env-card__facts">
        <div><dt>Mission</dt><dd>{data.mission}</dd></div>
        <div><dt>Instrument</dt><dd>{data.instrument}</dd></div>
        <div><dt>Population</dt><dd>{data.population}</dd></div>
        <div>
          <dt>Readings</dt>
          <dd>
            <span className="num">{shown}</span> shown of <span className="num">{data.row_count.toLocaleString()}</span>
            {data.time_precision === "minute" && " (minute precision, UTC)"}
          </dd>
        </div>
      </dl>

      <details className="env-card__more">
        <summary>Data quality and limitations</summary>
        <p className="small">{data.quality_summary.notes}</p>
        <p className="small muted">
          Missing readings: <span className="num">{data.quality_summary.missing_count}</span> · Quarantined outliers:{" "}
          <span className="num">{data.quality_summary.outlier_count}</span>
        </p>
        <ul className="small">
          {data.limitations.map((l) => <li key={l}>{l}</li>)}
        </ul>
      </details>

      <p className="env-card__cite small">
        Source: <a href={data.source_url} target="_blank" rel="noreferrer">NASA OSDR Environmental Data Application</a>
        {data.registry_id && <> ({data.registry_id})</>}. {data.citation}
      </p>
    </section>
  );
}
