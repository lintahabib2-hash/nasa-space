import { useMemo, useState } from "react";
import { BodyMap, type RegionStatus } from "../../components/body-map/BodyMap";
import { RegionPanel } from "../../components/body-map/RegionPanel";
import { CommsDelayBanner } from "../../components/environment-selector/CommsDelayBanner";
import { EnvironmentSelector } from "../../components/environment-selector/EnvironmentSelector";
import { EvidenceDrawer } from "../../components/evidence-drawer/EvidenceDrawer";
import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import { StatusChip } from "../../components/status/StatusChip";
import { EnvironmentContextCard } from "../environment-context/EnvironmentContextCard";
import { configuredMode, FIXTURE_BUNDLES, KNOWLEDGE } from "./dataSource";
import { fmtValue, humanize } from "./format";
import { statusDisplay, worstTier, type Tier } from "./statusDisplay";
import type { CrewBundle, DataMode, IndicatorData, Knowledge } from "./types";
import { useCrewData } from "./useCrewData";

const TIER_ORDER: Record<Tier, number> = { green: 0, unknown: 1, yellow: 2, red: 3 };

function regionIndicators(bundle: CrewBundle, knowledge: Knowledge, regionId: string): IndicatorData[] {
  return bundle.indicators.filter((i) => knowledge.indicators[i.measurement]?.region === regionId);
}

function regionStatuses(bundle: CrewBundle, knowledge: Knowledge): RegionStatus[] {
  return Object.entries(knowledge.regions).map(([id, region]) => ({
    id,
    label: region.label,
    tier: worstTier(regionIndicators(bundle, knowledge, id).map((i) => i.result.status)),
  }));
}

function mostUrgentRegion(regions: RegionStatus[]): string {
  return regions.reduce((a, b) => (TIER_ORDER[b.tier] > TIER_ORDER[a.tier] ? b : a), regions[0]).id;
}

export function DashboardPage({ knowledge = KNOWLEDGE }: { knowledge?: Knowledge }) {
  const [mode, setMode] = useState<DataMode>(configuredMode());
  const subjectForApi = import.meta.env.VITE_SUBJECT_ID || "crew_01";
  const state = useCrewData(mode, subjectForApi);

  // Deep links for demos and recordings: ?crew=crew_02&env=lunar
  const params = new URLSearchParams(typeof window === "undefined" ? "" : window.location.search);
  const [subjectIdx, setSubjectIdx] = useState(() =>
    Math.max(0, FIXTURE_BUNDLES.findIndex((b) => b.subject_id === params.get("crew"))),
  );
  const [envId, setEnvId] = useState(() => {
    const e = params.get("env");
    return e && knowledge.environments[e] ? e : "mars";
  });
  const [regionChoice, setRegionChoice] = useState<string | null>(null);
  const [evidenceFor, setEvidenceFor] = useState<string | null>(null);

  const bundles = state.kind === "ready" ? state.bundles : [];
  const bundle = bundles[Math.min(subjectIdx, bundles.length - 1)];
  const regions = useMemo(() => (bundle ? regionStatuses(bundle, knowledge) : []), [bundle, knowledge]);
  const regionId = regionChoice ?? (regions.length ? mostUrgentRegion(regions) : "brain");
  const env = knowledge.environments[envId];
  const anyAction = !!bundle?.indicators.some((i) => ["yellow", "red"].includes(statusDisplay(i.result.status).tier));
  const evidenceIndicator = bundle?.indicators.find((i) => i.measurement === evidenceFor);

  function chooseSubject(i: number) {
    setSubjectIdx(i);
    setRegionChoice(null); // jump to the most urgent region for the new crew member
    setEvidenceFor(null);
  }

  return (
    <>
      <div className="card controls">
        {bundles.length > 1 && (
          <fieldset className="control-group">
            <legend>Crew member</legend>
            <div className="segmented">
              {bundles.map((b, i) => (
                <label key={b.subject_id}>
                  <input type="radio" name="crew" checked={i === subjectIdx} onChange={() => chooseSubject(i)} />
                  <span>{b.display_name} · {humanize(b.scenario)}</span>
                </label>
              ))}
            </div>
          </fieldset>
        )}
        <EnvironmentSelector environments={knowledge.environments} value={envId} onChange={setEnvId} />
      </div>

      {env && <CommsDelayBanner env={env} envId={envId} alert={anyAction} note={knowledge.environment_note} />}

      {state.kind === "loading" && <div className="card" role="status">Loading data from the local API…</div>}

      {state.kind === "error" && (
        <div className="banner banner--error" role="alert">
          <div>
            <div className="banner__title">Local API unavailable</div>
            <div className="small">{state.message}. Start prototypes/offline_research/offline_api.py, or view the simulated scenarios.</div>
            <button type="button" className="btn" style={{ marginTop: 8 }} onClick={() => setMode("fixtures")}>
              Show simulated scenarios
            </button>
          </div>
        </div>
      )}

      {bundle && (
        <>
          <div className="banner banner--sim" data-testid="data-notice">
            <ProvenanceBadge kind={bundle.provenance_kind} />
            <div className="small">
              <strong>{bundle.display_name}: {bundle.scenario_label}.</strong>{" "}
              {bundle.notice ?? `Source ${bundle.source_id}.`} As of {bundle.as_of_utc.slice(0, 10)}.
            </div>
          </div>

          <section className="card" aria-labelledby="overview-title">
            <span className="eyebrow">Latest check-in vs. personal baseline</span>
            <h2 id="overview-title">Today&apos;s readings</h2>
            <div className="overview">
              {bundle.indicators.map((i) => {
                const card = knowledge.indicators[i.measurement];
                const region = card?.region;
                return (
                  <button
                    key={i.measurement}
                    type="button"
                    aria-current={region === regionId}
                    onClick={() => region && setRegionChoice(region)}
                  >
                    <span className="overview__top">
                      <span className="overview__name">{card?.label ?? humanize(i.measurement)}</span>
                      <span className="overview__value">{fmtValue(i.result.current_value, i.units)}</span>
                    </span>
                    <StatusChip status={i.result.status} />
                  </button>
                );
              })}
            </div>
          </section>

          <div className="main-grid">
            <section className="card" aria-labelledby="bodymap-title">
              <span className="eyebrow">Select a region</span>
              <h2 id="bodymap-title">Body map</h2>
              <BodyMap regions={regions} selected={regionId} onSelect={setRegionChoice} />
            </section>
            {env && (
              <RegionPanel
                regionId={regionId}
                indicators={regionIndicators(bundle, knowledge, regionId)}
                knowledge={knowledge}
                env={env}
                onOpenEvidence={setEvidenceFor}
              />
            )}
          </div>
        </>
      )}

      <EnvironmentContextCard />

      {evidenceIndicator && (
        <EvidenceDrawer indicator={evidenceIndicator} knowledge={knowledge} onClose={() => setEvidenceFor(null)} />
      )}
    </>
  );
}
