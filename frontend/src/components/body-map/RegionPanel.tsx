import { fmtValue, humanize } from "../../features/dashboard/format";
import { statusDisplay, worstTier } from "../../features/dashboard/statusDisplay";
import type { EnvironmentCard, IndicatorData, Knowledge } from "../../features/dashboard/types";
import { TrendChart } from "../charts/TrendChart";
import { ProvenanceBadge } from "../evidence-drawer/ProvenanceBadge";
import { StatusChip, TierChip } from "../status/StatusChip";

interface Props {
  regionId: string;
  indicators: IndicatorData[];
  knowledge: Knowledge;
  env: EnvironmentCard;
  onOpenEvidence: (measurement: string) => void;
}

/** Selected body region: what it does, spaceflight effects, and each indicator with status and guidance. */
export function RegionPanel({ regionId, indicators, knowledge, env, onOpenEvidence }: Props) {
  const region = knowledge.regions[regionId];
  if (!region) return null;
  const tier = worstTier(indicators.map((i) => i.result.status));
  const headingId = `region-${regionId}-title`;

  return (
    <section className="card" aria-labelledby={headingId} data-testid="region-panel">
      <div className="region-panel__head">
        <h2 id={headingId}>{region.label}</h2>
        <TierChip tier={tier} />
      </div>

      <dl className="facts">
        <div><dt>Function</dt><dd>{region.function}</dd></div>
        <div><dt>Spaceflight effects</dt><dd>{region.spaceflight_effects}</dd></div>
        <div>
          <dt>Hazards</dt>
          <dd className="tags">{region.hazards.map((h) => <span className="tag" key={h}>{knowledge.hazards[h] ?? h}</span>)}</dd>
        </div>
      </dl>

      {indicators.length === 0 && (
        <p className="muted">No readings for this region from the current data source.</p>
      )}

      {indicators.map((ind) => {
        const card = knowledge.indicators[ind.measurement];
        const r = ind.result;
        const d = statusDisplay(r.status);
        const label = card?.label ?? humanize(ind.measurement);
        const needsAction = d.tier === "yellow" || d.tier === "red";
        return (
          <article className="indicator" key={ind.measurement} data-measurement={ind.measurement}>
            <div className="indicator__head">
              <h3 className="indicator__title">{label}</h3>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <ProvenanceBadge kind={ind.provenance_kind} />
                <StatusChip status={r.status} />
              </div>
            </div>

            <div className="indicator__values">
              <span>Latest <b>{fmtValue(r.current_value, ind.units)}</b></span>
              <span>Personal median <b>{fmtValue(r.baseline_value, ind.units)}</b></span>
              <span>Robust z <b>{r.robust_z === null ? "—" : r.robust_z.toFixed(1)}</b></span>
            </div>

            <ul className="reasons" aria-label="Reasons from the analytics engine">
              {r.reasons.map((reason) => <li key={reason}>{reason}</li>)}
            </ul>

            {needsAction && card && (
              <div className="guidance guidance--selfcare" role="region" aria-label={`Self-care for ${label}`}>
                <strong>{d.tier === "red" ? "Interim steps now" : "Self-care now, recheck within 24 hours"}</strong>
                <ul>{card.self_care.map((s) => <li key={s}>{s}</li>)}</ul>
              </div>
            )}

            {card && (
              <details className="escalation" open={d.tier === "red"}>
                <summary>When to contact the flight surgeon</summary>
                <ul>{card.contact_when.map((s) => <li key={s}>{s}</li>)}</ul>
                <div className="delay">
                  <strong>{env.label}:</strong> one-way delay {env.one_way_delay}. {env.guidance}
                </div>
              </details>
            )}

            <TrendChart label={label} units={ind.units} series={ind.series} baseline={r.baseline_value} band={r.reference_band} />

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
              {card && <span className="small muted">How: {card.how_measured} Why: {card.why}</span>}
              <button type="button" className="btn" onClick={() => onOpenEvidence(ind.measurement)} aria-haspopup="dialog">
                Evidence &amp; sources
              </button>
            </div>
          </article>
        );
      })}
    </section>
  );
}
