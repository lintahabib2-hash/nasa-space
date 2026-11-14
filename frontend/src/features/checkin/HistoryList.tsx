import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import { localDay } from "./checkinSchema";
import type { LocalRecords } from "./checkinStore";

function summary(ind: LocalRecords["checkins"][number]["indicators"]): string {
  const parts: string[] = [];
  if (ind.sleep_duration) parts.push(`${ind.sleep_duration.value} h sleep`);
  if (ind.mood) parts.push(`mood ${ind.mood.value}/5`);
  if (ind.stress) parts.push(`stress ${ind.stress.value}/5`);
  if (ind.exercise_minutes) parts.push(`${ind.exercise_minutes.value} min exercise`);
  if (ind.systolic_bp && ind.diastolic_bp) parts.push(`BP ${ind.systolic_bp.value}/${ind.diastolic_bp.value} mmHg`);
  if (ind.blood_glucose) parts.push(`glucose ${ind.blood_glucose.value} mg/dL`);
  return parts.join(" · ");
}

function exportJson(records: LocalRecords) {
  const blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `crew-vitals-${localDay()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

/** The five most recent check-ins on this device, with JSON export. */
export function HistoryList({ records }: { records: LocalRecords }) {
  const latest = [...records.checkins].sort((a, b) => b.timestamp_utc.localeCompare(a.timestamp_utc)).slice(0, 5);
  const fmt = new Intl.DateTimeFormat(undefined, { weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  return (
    <section className="card ci-panel" aria-labelledby="history-title">
      <div className="ci-heading">
        <div>
          <span className="eyebrow">On this device</span>
          <h2 id="history-title">Recent check-ins</h2>
        </div>
        <button type="button" className="btn" onClick={() => exportJson(records)} disabled={records.checkins.length + records.reactionTests.length === 0}>
          Export JSON
        </button>
      </div>
      {latest.length === 0 ? (
        <p className="muted">No check-ins yet. Save one above and it will appear here.</p>
      ) : (
        <ul className="ci-history" data-testid="history">
          {latest.map((r) => (
            <li key={r.record_id}>
              <div className="ci-history__top">
                <strong>{fmt.format(new Date(r.timestamp_utc))}</strong>
                <ProvenanceBadge kind={r.provenance_kind} />
              </div>
              <div className="ci-history__values">{summary(r.indicators)}</div>
            </li>
          ))}
        </ul>
      )}
      {records.reactionTests.length > 0 && (
        <p className="small muted" style={{ marginTop: 10 }}>
          Reaction activities saved: {records.reactionTests.length}. Latest median{" "}
          <span className="num">{records.reactionTests[records.reactionTests.length - 1].score} ms</span> (not standardized).
        </p>
      )}
    </section>
  );
}
