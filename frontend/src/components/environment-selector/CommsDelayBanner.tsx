import type { EnvironmentCard } from "../../features/dashboard/types";

interface Props {
  env: EnvironmentCard;
  /** true when any indicator needs review, so the escalation guidance is emphasised */
  alert: boolean;
  note?: string;
}

/** Comms-delay banner. Announced politely to screen readers whenever the environment changes. */
export function CommsDelayBanner({ env, alert, note }: Props) {
  return (
    <div className={`banner banner--comms${alert ? " is-alert" : ""}`} role="status" aria-live="polite" data-testid="comms-banner">
      <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" style={{ flex: "none", marginTop: 2 }}>
        <path d="M4 18a10 10 0 0 1 16 0M7.5 15a6 6 0 0 1 9 0" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <circle cx="12" cy="18" r="1.8" fill="currentColor" />
      </svg>
      <div>
        <div className="banner__title">
          {env.label} · {env.setting}
        </div>
        <div>
          One-way signal delay: <strong>{env.one_way_delay}</strong>. {env.reply_expectation}
        </div>
        {alert && (
          <div style={{ marginTop: 4 }}>
            <strong>If you need the flight surgeon:</strong> {env.guidance}
          </div>
        )}
        {note && <div className="small muted" style={{ marginTop: 4 }}>{note}</div>}
      </div>
    </div>
  );
}
