import type { ReactNode } from "react";
import { DisclaimerBanner } from "./DisclaimerBanner";

/** Team-made mission patch: Earth arc, orbit and a pulse line. Not an agency logo. */
function MissionPatch() {
  return (
    <svg width="56" height="56" viewBox="0 0 56 56" aria-hidden="true" style={{ flex: "none" }}>
      <defs>
        <clipPath id="patch-clip"><circle cx="28" cy="28" r="22" /></clipPath>
      </defs>
      <circle cx="28" cy="28" r="26" fill="#ffffff" stroke="#0e1a2b" strokeWidth="2" />
      <circle cx="28" cy="28" r="22" fill="#dcebfa" />
      <g clipPath="url(#patch-clip)">
        <circle cx="28" cy="70" r="30" fill="#8fbdeb" />
        <circle cx="28" cy="70" r="30" fill="none" stroke="#ffffff" strokeWidth="1.5" />
      </g>
      <ellipse cx="28" cy="27" rx="21" ry="8" fill="none" stroke="#e8601c" strokeWidth="1.8" transform="rotate(-18 28 27)" />
      <path d="M11 28h7l3-7 4 13 3-9 2 3h15" fill="none" stroke="#0e1a2b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="44" cy="20" r="2.6" fill="#e8601c" />
    </svg>
  );
}

/** Pale orbital-daylight sky with Earth's limb along the right edge. */
function HeaderSky() {
  const sparkles: [number, number, number][] = [[90, 30, 3], [260, 98, 2.4], [420, 22, 2], [610, 80, 2.6], [760, 30, 2], [930, 104, 2.2]];
  return (
    <svg className="app-header__sky" viewBox="0 0 1200 140" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">
      <defs>
        <radialGradient id="earth" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0.86" stopColor="#a9cdf0" />
          <stop offset="0.97" stopColor="#cfe4f8" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="1060" cy="600" r="500" fill="url(#earth)" />
      <circle cx="1060" cy="600" r="482" fill="none" stroke="#ffffff" strokeWidth="2" opacity="0.9" />
      <path d="M560 150 C 760 40, 1040 10, 1220 40" fill="none" stroke="#9bbbe0" strokeWidth="1" strokeDasharray="3 7" />
      {sparkles.map(([x, y, s]) => (
        <path key={`${x}-${y}`} d={`M${x} ${y - s * 2}L${x + s * 0.5} ${y - s * 0.5}L${x + s * 2} ${y}L${x + s * 0.5} ${y + s * 0.5}L${x} ${y + s * 2}L${x - s * 0.5} ${y + s * 0.5}L${x - s * 2} ${y}L${x - s * 0.5} ${y - s * 0.5}Z`} fill="#9bb8da" />
      ))}
    </svg>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <a className="skip-link" href="#main">Skip to main content</a>
      <DisclaimerBanner />
      <header className="app-header">
        <HeaderSky />
        <div className="app-header__inner">
          <MissionPatch />
          <div>
            <h1 className="brand__name">Crew Vitals</h1>
            <p className="brand__tag">Daily crew readiness, compared with each astronaut&apos;s own baseline</p>
          </div>
          <span className="brand__event">NASA Space Apps Challenge 2026</span>
        </div>
      </header>
      <main id="main" className="page" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
