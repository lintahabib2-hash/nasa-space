import type { EnvironmentCard } from "../../features/dashboard/types";

interface Props {
  env: EnvironmentCard;
  /** environment id, used only to place the crew marker on the (not to scale) signal path */
  envId?: string;
  /** true when any indicator needs review, so the escalation guidance is emphasised */
  alert: boolean;
  note?: string;
}

// Symbolic distance along the path and pulse speed. Not to scale.
const PATH: Record<string, { at: number; dur: number }> = {
  station: { at: 0.14, dur: 1.2 },
  spacecraft: { at: 0.36, dur: 1.8 },
  lunar: { at: 0.46, dur: 2 },
  mars: { at: 0.95, dur: 4.5 },
};

function SignalPath({ envId, label }: { envId?: string; label: string }) {
  const { at, dur } = PATH[envId ?? ""] ?? { at: 0.5, dur: 2 };
  const style = { "--at": at, "--dur": `${dur}s` } as React.CSSProperties;
  return (
    <div className="signal__path" style={style} aria-hidden="true">
      <span className="signal__scale">not to scale</span>
      <span className="signal__track">
        <span className="signal__pulse" />
      </span>
      <span className="signal__node signal__node--earth">
        <svg width="34" height="34" viewBox="0 0 34 34">
          <defs>
            <radialGradient id="sig-earth" cx="0.35" cy="0.35" r="0.75">
              <stop offset="0" stopColor="#bfe0ff" />
              <stop offset="1" stopColor="#2a78d6" />
            </radialGradient>
          </defs>
          <circle cx="17" cy="17" r="15" fill="url(#sig-earth)" />
          <path d="M8 12q5-4 9 0t8 2M11 23q4 3 10 0" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" opacity="0.85" />
        </svg>
        <span className="signal__label">Earth</span>
      </span>
      <span className="signal__node signal__node--crew">
        <svg width="28" height="28" viewBox="0 0 28 28">
          <circle cx="14" cy="14" r="12" fill="#fff" stroke="#0e1a2b" strokeWidth="1.6" />
          <path d="M7 13q7-8 14 0q0 7-7 8q-7-1-7-8z" fill="#f6c879" stroke="#0e1a2b" strokeWidth="1" />
        </svg>
        <span className="signal__label">{label}</span>
      </span>
    </div>
  );
}

/** Earth-to-crew signal path and comms-delay guidance. Announced politely when the environment changes. */
export function CommsDelayBanner({ env, envId, alert, note }: Props) {
  return (
    <div className={`card signal${alert ? " is-alert" : ""}`} role="status" aria-live="polite" data-testid="comms-banner">
      <SignalPath envId={envId} label={env.label} />
      <div className="banner__title">
        {env.label} · {env.setting}
      </div>
      <div>
        One-way signal delay: <span className="signal__delay">{env.one_way_delay}</span>. {env.reply_expectation}
      </div>
      {alert && (
        <div style={{ marginTop: 6 }}>
          <strong>If you need the flight surgeon:</strong> {env.guidance}
        </div>
      )}
      {note && <div className="small muted" style={{ marginTop: 6 }}>{note}</div>}
    </div>
  );
}
