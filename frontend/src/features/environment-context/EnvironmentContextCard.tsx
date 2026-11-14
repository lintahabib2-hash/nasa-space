// Separate historical NASA environment card (Member 4, D01 NASA OSDR EDA RR-1).
// Context only: no status chips, no personal reference band, never driven by the crew selector,
// never on the same time axis as crew charts.
import { TrendChart } from "../../components/charts/TrendChart";
import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import environmentSample from "./fixtures/environment.sample.json";

const co2Series = environmentSample.series[0];

export function EnvironmentContextCard() {
  const summary = environmentSample.quality_summary;
  return (
    <section className="card env-context-card" aria-labelledby="env-context-card-title" data-testid="env-card">
      <div className="env-context-card__heading">
        <div>
          <span className="eyebrow">Separate from crew data</span>
          <h2 id="env-context-card-title">{environmentSample.display_title}</h2>
        </div>
        <ProvenanceBadge kind={environmentSample.provenance_kind} />
      </div>

      <p className="small muted">
        historical instrument data, not this crew member&apos;s exposure or dose
      </p>

      {environmentSample.is_fallback_not_ingested && (
        <p className="env-context-card__fallback">Static reference image, not ingested data.</p>
      )}

      <TrendChart
        label={co2Series.label}
        units={co2Series.units}
        series={co2Series.points}
        baseline={null}
      />

      <dl className="env-context-card__facts">
        <div><dt>Mission</dt><dd>{environmentSample.mission}, {environmentSample.location}</dd></div>
        <div><dt>Instrument</dt><dd>{environmentSample.instrument}</dd></div>
        <div><dt>Population</dt><dd>{environmentSample.population}</dd></div>
        <div>
          <dt>Readings</dt>
          <dd>
            <span className="num">{co2Series.points.length}</span> shown of{" "}
            <span className="num">{environmentSample.row_count.toLocaleString()}</span> (UTC, {environmentSample.time_precision} precision)
          </dd>
        </div>
      </dl>

      <details className="env-context-card__more">
        <summary>Data quality and limitations</summary>
        <p className="small">{summary.notes}</p>
        <p className="small muted">
          Missing readings: <span className="num">{summary.missing_count}</span> · Quarantined outliers:{" "}
          <span className="num">{summary.outlier_count}</span>
        </p>
        <ul className="small">
          {environmentSample.limitations.map((l) => <li key={l}>{l}</li>)}
        </ul>
      </details>

      <p className="small">
        <strong>Citation:</strong> {environmentSample.citation}
      </p>
      <p className="small">
        <strong>Source:</strong>{" "}
        <a href={environmentSample.source_url} target="_blank" rel="noreferrer">
          NASA EDA (RR-1)
        </a>
      </p>
    </section>
  );
}
