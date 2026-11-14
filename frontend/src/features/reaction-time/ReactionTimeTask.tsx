import { useEffect, useRef, useState } from "react";
import { buildReactionRecord, randomWait, ROUNDS, type ReactionRecord } from "./reactionLogic";

type Phase = "idle" | "waiting" | "ready" | "between" | "done";

interface Props {
  /** Persist the result. Throw to report a save error. */
  onSave: (record: ReactionRecord) => void;
}

/**
 * Optional five-round visual reaction activity (Member 5, ported from app.js).
 * Fix vs. the original: the target stays clickable while waiting, so an early tap is
 * detected as "Too soon" instead of being silently ignored by a disabled button.
 */
export function ReactionTimeTask({ onSave }: Props) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [instruction, setInstruction] = useState("Ready when you are. Complete five rounds.");
  const [status, setStatus] = useState("Results are saved only if you complete the activity.");
  const [error, setError] = useState("");
  const [startLabel, setStartLabel] = useState("Start activity");
  const rounds = useRef<number[]>([]);
  const startedAt = useRef(0);
  const timer = useRef<number | undefined>(undefined);

  const clear = () => window.clearTimeout(timer.current);
  useEffect(() => clear, []);

  function beginRound() {
    setPhase("waiting");
    setInstruction(`Wait for the target… Round ${rounds.current.length + 1} of ${ROUNDS}`);
    timer.current = window.setTimeout(() => {
      startedAt.current = performance.now();
      setPhase("ready");
      setInstruction("Tap or click the target!");
    }, randomWait());
  }

  function start() {
    clear();
    rounds.current = [];
    setError("");
    setStatus("Optional activity in progress.");
    setStartLabel("Restart activity");
    beginRound();
  }

  function finish() {
    const record = buildReactionRecord(rounds.current);
    setPhase("done");
    try {
      onSave(record);
      setInstruction(`Activity complete. Median response: ${record.score} ms.`);
      setStatus("Saved on this device. This is not a standardized score.");
    } catch (e) {
      setError((e as Error).message);
      setInstruction("Activity complete, but the result could not be saved.");
    }
    setStartLabel("Try again");
  }

  function onTarget() {
    if (phase === "waiting") {
      clear();
      rounds.current = [];
      setPhase("idle");
      setInstruction("Too soon. Start again when you are ready.");
      setStatus("No result was saved.");
      setStartLabel("Start activity");
      return;
    }
    if (phase !== "ready") return;
    rounds.current.push(Math.round(performance.now() - startedAt.current));
    if (rounds.current.length >= ROUNDS) {
      setPhase("between");
      timer.current = window.setTimeout(finish, 300);
      return;
    }
    setPhase("between");
    setInstruction("Got it. Get ready for the next round.");
    timer.current = window.setTimeout(beginRound, 500);
  }

  const active = phase === "waiting" || phase === "ready";
  return (
    <section className="card ci-panel" aria-labelledby="reaction-title">
      <div className="ci-heading">
        <div>
          <span className="eyebrow">Optional · about 30 seconds</span>
          <h2 id="reaction-title">Reaction-time activity</h2>
        </div>
      </div>
      <p className="muted">
        Tap or click when the target turns orange. This brief activity is for personal tracking only. It is not a validated
        cognitive test and makes no health or performance judgement.
      </p>
      <div className={`reaction-box is-${phase}`}>
        <p className="reaction-instruction" aria-live="assertive">{instruction}</p>
        <button
          type="button"
          className="reaction-target"
          disabled={!active}
          onClick={onTarget}
          aria-label={phase === "ready" ? "Target: tap now" : "Target: wait"}
          data-phase={phase}
        >
          {phase === "ready" ? "GO" : phase === "between" ? "✓" : "WAIT"}
        </button>
      </div>
      <div className="ci-actions">
        <button type="button" className="btn" onClick={start}>{startLabel}</button>
        <span className="small muted" aria-live="polite">{status}</span>
      </div>
      <p className="small muted ci-note">
        Timing uses this device&apos;s browser clock. Screen refresh, touch input, browser load and hardware can affect results.
        Do not compare results across devices as if they were standardized.
      </p>
      {error && <p className="ci-error" role="alert">{error}</p>}
    </section>
  );
}
