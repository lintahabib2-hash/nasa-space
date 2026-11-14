import { useEffect, useRef, type KeyboardEvent } from "react";
import { fmtDateTime, fmtValue, humanize } from "../../features/dashboard/format";
import type { IndicatorData, Knowledge } from "../../features/dashboard/types";
import { StatusChip } from "../status/StatusChip";
import { ProvenanceBadge } from "./ProvenanceBadge";

interface Props {
  indicator: IndicatorData;
  knowledge: Knowledge;
  onClose: () => void;
}

const GLOBAL_LIMITATIONS = [
  "Thresholds are documented demo rules, not validated clinical limits.",
  "Not a diagnosis or prediction of any clinical condition.",
  "No flag does not mean healthy. It only means the demo rule found no sustained change.",
  "Crew, environment and analog data are different populations and are never joined on timestamp.",
];

/** Evidence drawer: sources, provenance, data quality, missing data and limitations for one indicator. */
export function EvidenceDrawer({ indicator, knowledge, onClose }: Props) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const r = indicator.result;
  const card = knowledge.indicators[indicator.measurement];
  const label = card?.label ?? humanize(indicator.measurement);
  const missingPoints = indicator.series.filter((p) => p.value === null || p.quality_state === "missing").length;
  const sourceIds = Array.from(new Set([...(card?.sources ?? []), indicator.source_id]));

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    return () => previous?.focus?.();
  }, []);

  function onKeyDown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      e.stopPropagation();
      onClose();
      return;
    }
    if (e.key !== "Tab" || !panelRef.current) return;
    const focusables = panelRef.current.querySelectorAll<HTMLElement>("a[href], button, [tabindex='0'], summary");
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} aria-hidden="true" />
      <div
        ref={panelRef}
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="evidence-title"
        onKeyDown={onKeyDown}
        data-testid="evidence-drawer"
      >
        <div className="drawer__head">
          <h2 id="evidence-title">Evidence: {label}</h2>
          <button ref={closeRef} type="button" className="btn" onClick={onClose}>
            Close <span className="sr-only">evidence drawer</span>
          </button>
        </div>

        <div className="drawer__body">
          <section aria-labelledby="ev-status">
            <h3 id="ev-status">Status and reasons</h3>
            <p style={{ margin: "0 0 6px" }}><StatusChip status={r.status} /></p>
            <ul className="reasons">{r.reasons.map((x) => <li key={x}>{x}</li>)}</ul>
            <p className="small muted" style={{ margin: 0 }}>
              Basis: {humanize(r.severity_basis)} ·{" "}
              {r.not_medical_diagnosis ? <span className="flag">Not a medical diagnosis</span> : null}
            </p>
          </section>

          <section aria-labelledby="ev-measured">
            <h3 id="ev-measured">Measured vs reference</h3>
            <dl className="kv">
              <dt>Latest</dt><dd>{fmtValue(r.current_value, indicator.units)} <span className="muted">({fmtDateTime(r.timestamp_utc)})</span></dd>
              <dt>Personal median</dt><dd>{fmtValue(r.baseline_value, indicator.units)}</dd>
              <dt>Robust z</dt><dd>{r.robust_z === null ? "— (not computed)" : r.robust_z.toFixed(2)}</dd>
              <dt>Reference band</dt><dd>{r.reference_band ? `${fmtValue(r.reference_band.low)}–${fmtValue(r.reference_band.high, indicator.units)}` : "— (not provided)"}</dd>
              <dt>Input period</dt>
              <dd>
                {r.reference_start_utc
                  ? `${r.reference_count ?? "?"} readings, ${fmtDateTime(r.reference_start_utc)} → ${fmtDateTime(r.reference_end_utc)}`
                  : "— (no reference period)"}
              </dd>
            </dl>
            {r.reference_band && <p className="small muted" style={{ margin: "6px 0 0" }}>Band: {r.reference_band.basis}</p>}
          </section>

          <section aria-labelledby="ev-quality">
            <h3 id="ev-quality">Data quality and missing data</h3>
            <dl className="kv">
              <dt>Quality state</dt><dd><span className={`flag${r.quality_state === "adequate_for_demo" ? "" : " flag--warn"}`}>{humanize(r.quality_state)}</span></dd>
              <dt>Earlier readings used</dt><dd>{r.history_count}</dd>
              <dt>Rejected readings</dt><dd>{r.rejected_history_count}</dd>
              <dt>Missing in chart</dt><dd>{missingPoints} of {indicator.series.length} days{missingPoints > 0 && <> <span className="flag flag--warn">missing data</span></>}</dd>
              {r.result_origin && (<><dt>Computed by</dt><dd>{r.result_origin}</dd></>)}
            </dl>
          </section>

          <section aria-labelledby="ev-prov">
            <h3 id="ev-prov">Provenance</h3>
            <p style={{ margin: "0 0 6px" }}><ProvenanceBadge kind={indicator.provenance_kind} /></p>
            {indicator.provenance_kind === "simulated" && (
              <p className="small" style={{ margin: "0 0 6px" }}><strong>Simulated demo data. Not NASA data</strong> and not a real astronaut record.</p>
            )}
            <dl className="kv">
              <dt>Source ID</dt><dd>{indicator.source_id}</dd>
              <dt>Study ID</dt><dd>{indicator.study_id}</dd>
              <dt>Subject</dt><dd>{r.subject_id}</dd>
            </dl>
          </section>

          <section aria-labelledby="ev-sources">
            <h3 id="ev-sources">Sources</h3>
            <ul className="source-list">
              {sourceIds.map((id) => {
                const s = knowledge.sources[id];
                if (!s) return <li key={id}>{id}: <span className="muted">not in source registry yet</span></li>;
                return (
                  <li key={id}>
                    <strong>{id}</strong>{" "}
                    {s.url ? <a href={s.url} target="_blank" rel="noreferrer noopener">{s.title}</a> : s.title}
                    <span className="muted"> · {s.publisher}</span>
                    {!s.url && s.url_note && <div className="small muted">{s.url_note}</div>}
                  </li>
                );
              })}
            </ul>
            {card && <p className="small muted" style={{ margin: "6px 0 0" }}>How measured: {card.how_measured} Why: {card.why}</p>}
          </section>

          <section aria-labelledby="ev-limits">
            <h3 id="ev-limits">Limitations</h3>
            <ul className="source-list">
              {(card?.limitations ?? []).map((l) => <li key={l}>{l}</li>)}
              {GLOBAL_LIMITATIONS.map((l) => <li key={l}>{l}</li>)}
            </ul>
            {knowledge.status.startsWith("draft") && (
              <p className="small muted" style={{ margin: "6px 0 0" }}>Guidance text is a draft pending science review (Member 1).</p>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
