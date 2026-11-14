import { useCallback, useState } from "react";
import { ProvenanceBadge } from "../../components/evidence-drawer/ProvenanceBadge";
import { StreakCard } from "../gamification/Streaks";
import { ReactionTimeTask } from "../reaction-time/ReactionTimeTask";
import { PROMPTS, Reminders } from "../reminders/Reminders";
import { CheckInForm } from "./CheckInForm";
import { DEFAULT_SUBJECT_ID } from "./checkinSchema";
import { appendCheckin, appendReaction, emptyRecords, readRecords, type LocalRecords } from "./checkinStore";
import { HistoryList } from "./HistoryList";
import "./checkin.css";

function initialRecords(): { records: LocalRecords; error: string } {
  try {
    return { records: readRecords(), error: "" };
  } catch (e) {
    return { records: emptyRecords(), error: (e as Error).message };
  }
}

/** Daily check-in page (Member 5): check-in, reaction activity, history, routine and streak. */
export function CheckInPage() {
  const [{ records, error }, setState] = useState(initialRecords);
  const [prompt, setPrompt] = useState(() => PROMPTS[Math.floor(Math.random() * PROMPTS.length)]);
  const onPrompt = useCallback((text: string) => setPrompt(text), []);

  return (
    <div className="ci-page">
      <section className="ci-intro">
        <div>
          <span className="eyebrow">Daily crew routine</span>
          <h2 className="ci-title">A quick check-in, on your terms.</h2>
          <p className="muted">
            Record how you feel today. Entries stay in this browser, saved as <span className="num">{DEFAULT_SUBJECT_ID}</span>.
            They are not a diagnosis or medical assessment.
          </p>
        </div>
        <StreakCard days={records.checkins.map((c) => c.local_day)} />
      </section>

      {error && <div className="banner banner--error" role="alert">{error}</div>}

      <div className="ci-layout">
        <div className="ci-main">
          <CheckInForm
            onSave={(record) => {
              setState({ records: appendCheckin(record), error: "" });
              setPrompt("Thanks for checking in. Take a moment for yourself.");
            }}
          />
          <ReactionTimeTask onSave={(record) => setState({ records: appendReaction(record), error: "" })} />
          <HistoryList records={records} />
        </div>
        <aside className="ci-side">
          <Reminders prompt={prompt} onPrompt={onPrompt} />
          <section className="card ci-panel ci-notice">
            <strong>Not medical advice</strong>
            <p className="small">
              This tool records what you enter. It does not interpret readings, diagnose conditions, or replace advice from
              a qualified health professional or flight surgeon.
            </p>
          </section>
          <section className="card ci-panel">
            <span className="eyebrow">Data &amp; privacy</span>
            <h3>Local by design</h3>
            <p className="muted small">
              Check-ins and activity results are stored in this browser&apos;s local storage. Export a copy any time. Clearing
              browser data removes these records.
            </p>
            <ProvenanceBadge kind="manually_entered" />
          </section>
        </aside>
      </div>
    </div>
  );
}
