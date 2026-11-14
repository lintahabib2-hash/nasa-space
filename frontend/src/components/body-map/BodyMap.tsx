import type { KeyboardEvent } from "react";
import type { Tier } from "../../features/dashboard/statusDisplay";
import { TIER_LABEL } from "../../features/dashboard/statusDisplay";
import { StatusIcon } from "../status/StatusIcon";
import { TierChip } from "../status/StatusChip";

export interface RegionStatus {
  id: string;
  label: string;
  tier: Tier;
}

interface Props {
  regions: RegionStatus[];
  selected: string;
  onSelect: (id: string) => void;
}

// Anatomical regions drawn on the figure. Whole-body systems (immune, radiation)
// cannot be placed on one spot, so they are listed as buttons under the figure.
const SHAPES: Record<string, { paths?: string[]; circle?: [number, number, number]; marker: [number, number] }> = {
  brain: { circle: [100, 40, 26], marker: [138, 24] },
  cardiovascular: { paths: ["M70 80 Q100 72 130 80 L134 150 L66 150 Z"], marker: [100, 114] },
  metabolic: { paths: ["M66 153 L134 153 L130 208 Q100 220 70 208 Z"], marker: [100, 182] },
  musculoskeletal: {
    paths: [
      "M66 84 L52 90 L34 190 L47 194 L64 122 Z",
      "M134 84 L148 90 L166 190 L153 194 L136 122 Z",
      "M72 214 L98 222 L95 362 L77 362 Z",
      "M128 214 L102 222 L105 362 L123 362 Z",
    ],
    marker: [40, 150],
  },
};

function activate(e: KeyboardEvent, fn: () => void) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fn();
  }
}

export function BodyMap({ regions, selected, onSelect }: Props) {
  const onFigure = regions.filter((r) => SHAPES[r.id]);
  const systemic = regions.filter((r) => !SHAPES[r.id]);

  return (
    <div className="bodymap">
      <svg viewBox="0 0 200 380" role="group" aria-label="Body map. Select a region to see its indicators.">
        {/* neutral silhouette: neck, hands and feet are not interactive */}
        <rect className="silhouette" x="92" y="64" width="16" height="16" rx="4" />
        <circle className="silhouette" cx="40" cy="200" r="7" />
        <circle className="silhouette" cx="160" cy="200" r="7" />
        <ellipse className="silhouette" cx="86" cy="368" rx="12" ry="6" />
        <ellipse className="silhouette" cx="114" cy="368" rx="12" ry="6" />

        {onFigure.map((r) => {
          const s = SHAPES[r.id];
          const pressed = selected === r.id;
          return (
            <g
              key={r.id}
              className={`region region--${r.tier}`}
              role="button"
              tabIndex={0}
              aria-pressed={pressed}
              aria-label={`${r.label}: ${TIER_LABEL[r.tier]}`}
              data-region={r.id}
              onClick={() => onSelect(r.id)}
              onKeyDown={(e) => activate(e, () => onSelect(r.id))}
            >
              <title>{`${r.label}: ${TIER_LABEL[r.tier]}`}</title>
              {s.circle && <circle className="shape" cx={s.circle[0]} cy={s.circle[1]} r={s.circle[2]} />}
              {s.paths?.map((d) => <path key={d} d={d} />)}
              <g transform={`translate(${s.marker[0] - 10} ${s.marker[1] - 10})`}>
                <StatusIcon tier={r.tier} size={20} />
              </g>
            </g>
          );
        })}
      </svg>

      <div className="systemic" aria-label="Whole-body systems">
        {systemic.map((r) => (
          <button
            key={r.id}
            type="button"
            aria-pressed={selected === r.id}
            data-region={r.id}
            onClick={() => onSelect(r.id)}
          >
            <span>{r.label}</span>
            <TierChip tier={r.tier} />
          </button>
        ))}
      </div>

      <div className="legend" aria-label="Status legend">
        {(["green", "yellow", "red", "unknown"] as Tier[]).map((t) => (
          <TierChip key={t} tier={t} />
        ))}
      </div>
    </div>
  );
}
