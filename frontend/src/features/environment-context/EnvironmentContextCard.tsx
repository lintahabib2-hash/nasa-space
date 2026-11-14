import { TrendChart } from "../../components/charts/TrendChart";
import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import environmentSample from "./fixtures/environment.sample.json";

const co2Series = environmentSample.series[0];

export function EnvironmentContextCard() {
  return (
    <section className="card env-context-card" aria-labelledby="env-context-card-title">
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

      <TrendChart
        label={co2Series.label}
        units={co2Series.units}
        series={co2Series.points}
        baseline={null}
      />

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
