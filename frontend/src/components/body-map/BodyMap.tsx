import { useId, useState } from "react";
import type { KeyboardEvent, ReactNode } from "react";
import type { Tier } from "../../features/dashboard/statusDisplay";
import { TIER_LABEL } from "../../features/dashboard/statusDisplay";
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

const PART_REGION: Record<string, string> = {
  skull: "brain",
  brain: "brain",
  spine: "musculoskeletal",
  ribs: "musculoskeletal",
  clavicle: "musculoskeletal",
  pelvis: "musculoskeletal",
  humerus: "musculoskeletal",
  forearm: "musculoskeletal",
  hand: "musculoskeletal",
  femur: "musculoskeletal",
  knee: "musculoskeletal",
  shin: "musculoskeletal",
  foot: "musculoskeletal",
  lungs: "cardiovascular",
  heart: "cardiovascular",
  trachea: "cardiovascular",
  liver: "metabolic",
  stomach: "metabolic",
  kidneys: "metabolic",
  colon: "metabolic",
  small: "metabolic",
};

const PART_LABEL: Record<string, string> = {
  skull: "Skull",
  brain: "Brain and behavior",
  spine: "Spine",
  ribs: "Ribs",
  clavicle: "Collarbone",
  pelvis: "Pelvis",
  humerus: "Upper arm bone",
  forearm: "Forearm bones",
  hand: "Hand bones",
  femur: "Thigh bone",
  knee: "Kneecap",
  shin: "Shin bones",
  foot: "Foot bones",
  lungs: "Lungs",
  heart: "Heart and blood vessels",
  trachea: "Windpipe",
  liver: "Liver",
  stomach: "Stomach",
  kidneys: "Kidneys",
  colon: "Large intestine",
  small: "Small intestine",
};

const BODY_REGION_IDS = ["brain", "cardiovascular", "metabolic", "musculoskeletal"];
const RIB_WIDTHS = [44, 52, 58, 62, 64, 64, 62, 58, 50, 42];

const LABELS = [
  { part: "brain", text: "BRAIN", x: 16, y: 40, side: "r", labelY: 40 },
  { part: "clavicle", text: "COLLARBONE", x: 70, y: 138, side: "r", labelY: 110 },
  { part: "ribs", text: "RIBS", x: 62, y: 184, side: "r", labelY: 160 },
  { part: "heart", text: "HEART", x: 36, y: 212, side: "r", labelY: 205 },
  { part: "humerus", text: "UPPER ARM BONE", x: 104, y: 236, side: "r", labelY: 235 },
  { part: "stomach", text: "STOMACH", x: 58, y: 282, side: "r", labelY: 270 },
  { part: "forearm", text: "FOREARM BONES", x: 112, y: 326, side: "r", labelY: 305 },
  { part: "colon", text: "LARGE INTESTINE", x: 46, y: 350, side: "r", labelY: 345 },
  { part: "hand", text: "HAND BONES", x: 118, y: 416, side: "r", labelY: 395 },
  { part: "foot", text: "FOOT BONES", x: 66, y: 728, side: "r", labelY: 725 },
  { part: "skull", text: "SKULL", x: -26, y: 60, side: "l", labelY: 50 },
  { part: "spine", text: "SPINE", x: 0, y: 122, side: "l", labelY: 100 },
  { part: "trachea", text: "WINDPIPE", x: 0, y: 144, side: "l", labelY: 140 },
  { part: "lungs", text: "LUNGS", x: -52, y: 196, side: "l", labelY: 190 },
  { part: "liver", text: "LIVER", x: -44, y: 278, side: "l", labelY: 255 },
  { part: "kidneys", text: "KIDNEYS", x: -38, y: 304, side: "l", labelY: 305 },
  { part: "small", text: "SMALL INTESTINE", x: -22, y: 350, side: "l", labelY: 360 },
  { part: "pelvis", text: "PELVIS", x: -64, y: 396, side: "l", labelY: 410 },
  { part: "femur", text: "THIGH BONE", x: -50, y: 480, side: "l", labelY: 470 },
  { part: "knee", text: "KNEECAP", x: -48, y: 566, side: "l", labelY: 560 },
  { part: "shin", text: "SHIN BONES", x: -46, y: 640, side: "l", labelY: 640 },
];

function activate(e: KeyboardEvent, fn: () => void) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fn();
  }
}

export function BodyMap({ regions, selected, onSelect }: Props) {
  const [activePart, setActivePart] = useState<string | null>(null);
  const generatedId = useId().replace(/:/g, "");
  const id = (name: string) => `${generatedId}-${name}`;
  const regionById = new Map(regions.map((region) => [region.id, region]));
  const systemic = regions.filter((region) => !BODY_REGION_IDS.includes(region.id));

  const renderPart = (partId: string, children: ReactNode) => {
    const regionId = PART_REGION[partId];
    const region = regionById.get(regionId);
    const hot = activePart === partId;
    const ariaLabel = region && (partId === "brain" || partId === "heart")
      ? `${region.label}: ${TIER_LABEL[region.tier]}`
      : `${PART_LABEL[partId]}: ${region ? TIER_LABEL[region.tier] : "Health region unavailable"}`;

    return (
      <g
        key={partId}
        className={`part${hot ? " hot" : ""}`}
        data-p={partId}
        role="button"
        tabIndex={region ? 0 : -1}
        aria-disabled={!region}
        aria-pressed={selected === regionId}
        aria-label={ariaLabel}
        onPointerEnter={() => setActivePart(partId)}
        onPointerLeave={() => setActivePart(null)}
        onFocus={() => setActivePart(partId)}
        onBlur={() => setActivePart(null)}
        onClick={() => region && onSelect(regionId)}
        onKeyDown={(e) => region && activate(e, () => onSelect(regionId))}
      >
        {children}
      </g>
    );
  };

  return (
    <div className="bodymap">
      <svg viewBox="0 0 600 760" role="group" aria-label="Labeled human body map. Select an organ or bone to see its health indicators.">
        <defs>
          <radialGradient id={id("backdrop")} cx=".5" cy=".4" r=".72">
            <stop offset="0" stopColor="#0b1a33" />
            <stop offset="1" stopColor="#050b1a" />
          </radialGradient>
          <path id={id("arm")} d="M96 152 C108 156 116 172 114 196 C112 224 112 246 117 268 C119 300 116 330 112 352 L110 374 C120 392 124 414 122 432 C122 446 118 454 113 454 C108 454 104 444 103 432 C102 414 100 396 98 374 C96 346 96 300 94 272 C90 250 88 224 86 204 Z" />
          <path id={id("leg")} d="M84 392 C92 440 84 500 72 556 C68 570 68 584 70 600 C74 626 72 664 62 698 C66 712 72 728 72 738 C70 746 56 748 44 746 C36 746 32 740 34 730 C36 716 40 706 42 698 C38 664 34 630 34 604 C32 584 30 570 32 556 C26 500 14 460 6 432 Z" />
          <g id={id("humerus")}>
            <path d="M94 166 C100 200 102 236 104 268" />
            <circle cx="92" cy="164" r="9" />
          </g>
          <g id={id("forearm")}>
            <path d="M108 278 C114 312 114 340 110 370" />
            <path d="M100 278 C102 312 102 340 102 372" />
          </g>
          <g id={id("hand")}>
            <circle cx="105" cy="380" r="6" />
            <path d="M106 386 L118 440 M105 386 L112 448 M104 386 L106 448 M103 386 L99 434 M108 382 L122 408" />
          </g>
          <g id={id("femur")}>
            <path d="M52 414 C62 462 56 512 48 554" />
            <circle cx="46" cy="408" r="9" />
            <path d="M54 410 L70 420" />
          </g>
          <ellipse id={id("knee")} cx="48" cy="566" rx="9" ry="11" />
          <g id={id("shin")}>
            <path d="M46 580 C46 620 46 660 46 696" />
            <path d="M62 586 C62 626 60 660 60 692" />
          </g>
          <path id={id("foot")} d="M52 704 L68 738 M52 704 L60 742 M52 704 L52 744 M52 704 L44 742 M52 704 L38 738" />
          <path id={id("clavicle")} d="M8 134 C30 128 62 132 90 148" />
          <ellipse id={id("kidney")} cx="38" cy="302" rx="9" ry="16" transform="rotate(-10 38 302)" />
        </defs>

        <rect className="hologram__backdrop" width="600" height="760" rx="14" fill={`url(#${id("backdrop")})`} />
        <g transform="translate(300 0)">
          <g className="shell">
            <path d="M0 22 C24 22 36 42 35 66 C34 88 22 108 0 112 C-22 108 -34 88 -35 66 C-36 42 -24 22 0 22Z" />
            <ellipse cx="36" cy="70" rx="5" ry="10" />
            <ellipse cx="-36" cy="70" rx="5" ry="10" />
            <path d="M-14 98 L14 98 L15 128 C40 134 78 138 96 154 C100 170 98 190 90 205 C80 235 66 262 62 292 C60 330 80 352 82 392 C76 410 50 430 0 438 C-50 430 -76 410 -82 392 C-80 352 -60 330 -62 292 C-66 262 -80 235 -90 205 C-98 190 -100 170 -96 154 C-78 138 -40 134 -15 128Z" />
            <use href={`#${id("arm")}`} />
            <use href={`#${id("arm")}`} transform="scale(-1 1)" />
            <use href={`#${id("leg")}`} />
            <use href={`#${id("leg")}`} transform="scale(-1 1)" />
          </g>

          <g id={id("skeleton")}>
            {renderPart("skull", <>
              <path d="M0 26 C24 26 32 46 30 64 C29 74 24 82 18 86 L18 94 L-18 94 L-18 86 C-24 82 -29 74 -30 64 C-32 46 -24 26 0 26Z" />
              <path className="bone" strokeWidth="2" d="M-20 92 C-20 108 -10 112 0 112 C10 112 20 108 20 92" />
              <circle className="deco" cx="-11" cy="66" r="6" />
              <circle className="deco" cx="11" cy="66" r="6" />
              <path className="deco" d="M0 72 L-3 82 L3 82Z M-14 97 L14 97" />
            </>)}

            {renderPart("spine", <>
              {Array.from({ length: 24 }, (_, index) => {
                const width = 12 + index * 0.5;
                const y = 114 + index * 10.3;
                return <rect key={index} x={-width / 2} y={y} width={width} height="7.5" rx="3" />;
              })}
              <path className="bone" d="M-14 368 L14 368 L6 402 L-6 402Z" />
            </>)}

            {renderPart("ribs", <>
              <rect className="bone" x="-6" y="146" width="12" height="72" rx="5" />
              {RIB_WIDTHS.map((width, index) => {
                const y = 150 + index * 12.5;
                return [1, -1].map((side) => (
                  <path
                    className="bone"
                    key={`${index}-${side}`}
                    d={`M${side * 8} ${y} C${side * (8 + width * 0.5)} ${y - 8} ${side * width} ${y + 2} ${side * width} ${y + 26}`}
                  />
                ));
              })}
            </>)}

            {renderPart("clavicle", <>
              <use href={`#${id("clavicle")}`} className="bone" />
              <use href={`#${id("clavicle")}`} className="bone" transform="scale(-1 1)" />
            </>)}

            {renderPart("pelvis", <path d="M12 366 C46 348 76 362 78 390 C78 408 64 424 48 424 C38 424 32 414 30 406 L10 420 L0 430 L-10 420 L-30 406 C-32 414 -38 424 -48 424 C-64 424 -78 408 -78 390 C-76 362 -46 348 -12 366Z" />)}

            {renderPart("humerus", <>
              <use href={`#${id("humerus")}`} className="bone" />
              <use href={`#${id("humerus")}`} className="bone" transform="scale(-1 1)" />
            </>)}
            {renderPart("forearm", <>
              <use href={`#${id("forearm")}`} className="bone" />
              <use href={`#${id("forearm")}`} className="bone" transform="scale(-1 1)" />
            </>)}
            {renderPart("hand", <>
              <use href={`#${id("hand")}`} className="bone" />
              <use href={`#${id("hand")}`} className="bone" transform="scale(-1 1)" />
            </>)}
            {renderPart("femur", <>
              <use href={`#${id("femur")}`} className="bone" />
              <use href={`#${id("femur")}`} className="bone" transform="scale(-1 1)" />
            </>)}
            {renderPart("knee", <>
              <use href={`#${id("knee")}`} />
              <use href={`#${id("knee")}`} transform="scale(-1 1)" />
            </>)}
            {renderPart("shin", <>
              <use href={`#${id("shin")}`} className="bone" />
              <use href={`#${id("shin")}`} className="bone" transform="scale(-1 1)" />
            </>)}
            {renderPart("foot", <>
              <use href={`#${id("foot")}`} className="bone" />
              <use href={`#${id("foot")}`} className="bone" transform="scale(-1 1)" />
            </>)}
          </g>

          <g id={id("organs")}>
            <path className="deco" d="M-66 232 C-40 252 40 252 66 232" />
            {renderPart("kidneys", <>
              <use href={`#${id("kidney")}`} className="organ" />
              <use href={`#${id("kidney")}`} className="organ" transform="scale(-1 1)" />
            </>)}
            {renderPart("liver", <path className="organ" d="M-6 252 C-40 244 -66 250 -72 270 C-70 296 -40 304 -18 296 C0 292 20 280 28 268 C20 258 8 254 -6 252Z" />)}
            {renderPart("stomach", <path className="organ" d="M22 258 C50 250 66 268 56 292 C50 310 28 312 20 300 C14 290 22 284 28 278 C34 270 20 266 22 258Z" />)}
            {renderPart("colon", <path className="bone" strokeWidth="8" strokeOpacity=".45" d="M-46 376 L-46 318 C-46 310 -40 306 -34 306 L34 306 C42 306 46 310 46 318 L46 372 C46 392 30 398 20 392 C12 388 8 394 0 400" />)}
            {renderPart("small", <path className="bone" strokeWidth="5" strokeOpacity=".6" d="M-30 330 C-10 322 10 326 30 332 C34 342 12 346 -4 342 C-22 340 -34 350 -26 358 C-14 366 10 360 28 366 C34 376 14 380 -6 376 C-24 374 -30 382 -16 386 C0 390 18 388 28 384" />)}
            {renderPart("lungs", <>
              <path className="organ" d="M-10 156 C-44 148 -66 176 -64 216 C-62 238 -44 246 -22 242 C-12 240 -8 230 -8 220Z" />
              <path className="organ" d="M10 156 C44 148 66 176 64 216 C62 238 44 246 24 242 C14 238 10 226 10 222 C22 216 28 202 12 190 C8 178 8 166 10 156Z" />
            </>)}
            {renderPart("trachea", <path className="bone" strokeWidth="6" d="M0 108 L0 156 M0 156 L-18 178 M0 156 L18 178" />)}
            {renderPart("heart", <path className="organ" d="M10 190 C24 176 46 186 40 208 C36 224 22 236 10 246 C-2 236 -16 224 -18 208 C-22 186 -4 176 10 190Z" />)}
            {renderPart("brain", <>
              <ellipse className="organ" cx="0" cy="46" rx="24" ry="17" />
              <path className="deco" d="M0 30 L0 62 M-12 38 C-18 46 -14 54 -8 58 M12 38 C18 46 14 54 8 58 M-20 48 C-14 44 -8 48 M20 48 C14 44 8 48" />
            </>)}
          </g>

          <g id={id("labels")}>
            {LABELS.map((label) => {
              const parentId = PART_REGION[label.part];
              const region = regionById.get(parentId);
              const right = label.side === "r";
              const textX = right ? 285 : -285;
              const elbow = right ? 150 : -150;
              const hot = activePart === label.part;
              return (
                <g
                  key={label.part}
                  className={`label${hot ? " hot" : ""}`}
                  data-p={label.part}
                  onPointerEnter={() => setActivePart(label.part)}
                  onPointerLeave={() => setActivePart(null)}
                >
                  <path d={`M${label.x} ${label.y} L${elbow} ${label.labelY} L${textX} ${label.labelY}`} />
                  <text x={textX} y={label.labelY - 4} textAnchor={right ? "end" : "start"}>{label.text}</text>
                  {!region && <title>{label.text}: health region unavailable</title>}
                </g>
              );
            })}
          </g>
        </g>
      </svg>

      <div className="systemic" aria-label="Whole-body systems">
        {systemic.map((region) => (
          <button
            key={region.id}
            type="button"
            aria-pressed={selected === region.id}
            data-region={region.id}
            onClick={() => onSelect(region.id)}
          >
            <span>{region.label}</span>
            <TierChip tier={region.tier} />
          </button>
        ))}
      </div>

      <div className="legend" aria-label="Status legend">
        {(["green", "yellow", "red", "unknown"] as Tier[]).map((tier) => (
          <TierChip key={tier} tier={tier} />
        ))}
      </div>
    </div>
  );
}
