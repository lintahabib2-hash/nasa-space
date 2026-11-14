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

type Shape = { paths: string[]; circle?: [number, number, number]; marker: [number, number] };

// Spacesuit regions. Whole-body systems (immune, radiation) cannot be placed on one
// spot, so they are listed as buttons under the figure.
const SHAPES: Record<string, Shape> = {
  // helmet shell
  brain: { paths: [], circle: [110, 50, 34], marker: [152, 22] },
  // hard upper torso
  cardiovascular: { paths: ["M66 98 Q110 86 154 98 L158 170 L62 170 Z"], marker: [110, 160] },
  // waist bearing and lower torso
  metabolic: { paths: ["M62 174 L158 174 L153 224 Q110 238 67 224 Z"], marker: [110, 204] },
  // arms and legs
  musculoskeletal: {
    paths: [
      "M64 102 L42 110 L28 196 L48 201 L62 142 Z",
      "M156 102 L178 110 L192 196 L172 201 L158 142 Z",
      "M70 230 L107 239 L103 356 L74 356 Z",
      "M150 230 L113 239 L117 356 L146 356 Z",
    ],
    marker: [24, 150],
  },
};

function activate(e: KeyboardEvent, fn: () => void) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fn();
  }
}

/** Decorative suit hardware drawn above the regions. Pointer events pass through. */
function SuitDetails() {
  return (
    <>
      {/* visor */}
      <path className="visor" d="M86 46 Q110 28 134 46 Q136 66 110 72 Q84 66 86 46 Z" fill="url(#visor)" stroke="#8e9bad" strokeWidth="1" />
      <path className="visor" d="M94 44 Q104 36 116 37" fill="none" stroke="#ffffff" strokeWidth="3" strokeLinecap="round" opacity="0.8" />
      {/* chest display and control module */}
      <rect className="suit-detail" x="92" y="112" width="36" height="24" rx="4" />
      <circle className="suit-detail" cx="101" cy="124" r="3.5" />
      <rect className="suit-detail" x="108" y="119" width="15" height="4" rx="1" />
      <rect className="suit-detail" x="108" y="126" width="11" height="4" rx="1" />
      {/* shoulder mission patch */}
      <circle className="patch" cx="146" cy="112" r="5" />
      {/* seams: waist ring, wrist, knee and boot rings */}
      <path className="seam" d="M64 174 Q110 184 156 174" />
      <path className="seam" d="M32 186 L49 190 M188 186 L171 190" />
      <path className="seam" d="M74 296 Q89 300 105 296 M115 296 Q131 300 146 296" />
    </>
  );
}

export function BodyMap({ regions, selected, onSelect }: Props) {
  const onFigure = regions.filter((r) => SHAPES[r.id]);
  const systemic = regions.filter((r) => !SHAPES[r.id]);

  return (
    <div className="bodymap">
      <svg viewBox="0 0 220 392" role="group" aria-label="Astronaut body map. Select a region to see its indicators.">
        <defs>
          <linearGradient id="visor" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#fde7b0" />
            <stop offset="0.55" stopColor="#f6c879" />
            <stop offset="1" stopColor="#b9d5f3" />
          </linearGradient>
        </defs>

        {/* life-support backpack, neck ring, gloves and boots: not interactive */}
        <rect className="suit-base" x="56" y="80" width="108" height="128" rx="16" />
        <rect className="suit-base" x="90" y="82" width="40" height="12" rx="5" />
        <circle className="suit-base" cx="37" cy="211" r="11" />
        <circle className="suit-base" cx="183" cy="211" r="11" />
        <rect className="suit-base" x="68" y="354" width="40" height="22" rx="8" />
        <rect className="suit-base" x="112" y="354" width="40" height="22" rx="8" />

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
              {s.paths.map((d) => <path className="shape" key={d} d={d} />)}
            </g>
          );
        })}

        <SuitDetails />

        {/* status markers sit on top so the suit hardware never hides them */}
        {onFigure.map((r) => {
          const [x, y] = SHAPES[r.id].marker;
          return (
            <g key={`m-${r.id}`} transform={`translate(${x - 11} ${y - 11})`} pointerEvents="none" aria-hidden="true">
              <circle cx="11" cy="11" r="12.5" fill="#ffffff" />
              <g transform="translate(1 1)"><StatusIcon tier={r.tier} size={20} /></g>
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
