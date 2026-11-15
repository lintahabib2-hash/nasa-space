import type { ReactNode } from "react";
import { DisclaimerBanner } from "./DisclaimerBanner";

/** Deep-space sky with a distant planet, orbital path and gold stars. */
function HeaderSky() {
  const sparkles: [number, number, number][] = [[90, 30, 3], [260, 98, 2.4], [420, 22, 2], [610, 80, 2.6], [760, 30, 2], [930, 104, 2.2]];
  return (
    <svg className="app-header__sky" viewBox="0 0 1200 140" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">
      <defs>
        <radialGradient id="earth" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0.86" stopColor="#68388d" />
          <stop offset="0.97" stopColor="#221545" />
          <stop offset="1" stopColor="#110515" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="1060" cy="600" r="500" fill="url(#earth)" />
      <circle cx="1060" cy="600" r="482" fill="none" stroke="#b26fcb" strokeWidth="2" opacity="0.9" />
      <path d="M560 150 C 760 40, 1040 10, 1220 40" fill="none" stroke="var(--orbit-blue)" strokeWidth="1" strokeDasharray="3 7" />
      {sparkles.map(([x, y, s]) => (
        <path key={`${x}-${y}`} d={`M${x} ${y - s * 2}L${x + s * 0.5} ${y - s * 0.5}L${x + s * 2} ${y}L${x + s * 0.5} ${y + s * 0.5}L${x} ${y + s * 2}L${x - s * 0.5} ${y + s * 0.5}L${x - s * 2} ${y}L${x - s * 0.5} ${y - s * 0.5}Z`} fill="#ffdf91" />
      ))}
    </svg>
  );
}

function MedicalTools() {
  return (
    <svg className="medical-tools" viewBox="0 0 220 140" aria-hidden="true">
      <g className="medical-tools__stethoscope" fill="none" stroke="#e6edf9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <path d="M27 21v25c0 19 12 33 31 33s31-14 31-33V21" />
        <path d="M58 79v16c0 12 8 20 18 20s18-8 18-20V87" />
        <path d="M21 21h12m50 0h12" stroke="#ffdf91" strokeWidth="4" />
        <circle cx="94" cy="87" r="8" fill="#68388d" />
        <circle cx="94" cy="87" r="3" fill="#ffdf91" stroke="none" />
      </g>
      <g className="medical-tools__syringe" fill="none" stroke="#c7d0de" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <rect x="150" y="21" width="17" height="48" rx="3" fill="#221545" />
        <path d="M145 27h27M158 13v8m0 48v20m-7-35h15m-15-12h15m-8 47v9" />
        <path d="M155 13h7" stroke="#ffdf91" strokeWidth="4" />
      </g>
      <g className="medical-tools__capsule" stroke="#e6edf9" strokeWidth="2">
        <rect x="119" y="84" width="46" height="19" rx="9.5" fill="#68388d" />
        <path d="M142 84v19" stroke="#ffdf91" />
      </g>
      <path className="medical-tools__cross" d="M193 25h10v10h10v10h-10v10h-10V45h-10V35h10Z" fill="#ffdf91" />
      <path className="medical-tools__ecg" d="M111 122h16l8-12 8 20 10-17 7 9h29" fill="none" stroke="#b26fcb" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function CosmicBackdrop() {
  return (
    <div className="cosmic-backdrop" aria-hidden="true">
      <svg className="cosmic-backdrop__stars" viewBox="0 0 1000 800" preserveAspectRatio="none">
        <path className="cosmic-star cosmic-star--gold cosmic-star--one" d="M0-22 6-6 22 0 6 6 0 22-6 6-22 0-6-6Z" transform="translate(155 145)" />
        <path className="cosmic-star cosmic-star--silver cosmic-star--two" d="M0-18 5-5 18 0 5 5 0 18-5 5-18 0-5-5Z" transform="translate(830 310)" />
        <path className="cosmic-star cosmic-star--gold cosmic-star--three" d="M0-20 5-5 20 0 5 5 0 20-5 5-20 0-5-5Z" transform="translate(735 690)" />
        <path className="cosmic-star cosmic-star--silver cosmic-star--four" d="M0-15 4-4 15 0 4 4 0 15-4 4-15 0-4-4Z" transform="translate(285 570)" />
      </svg>
      <svg className="cosmic-astronaut" viewBox="0 0 120 160">
        <g stroke="#e6edf9" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round">
          <path d="M40 77 25 86 18 108" fill="none" />
          <path d="M80 77 96 87 101 105" fill="none" />
          <path d="M48 119 42 143 53 145 60 124M72 119 79 142 68 146 61 124" fill="#221545" />
          <path d="m42 145-2 5h16l-2-5m25 0 2 5H65l2-5" fill="#855ab4" />
          <rect x="83" y="65" width="17" height="43" rx="7" fill="#68388d" />
          <path d="M39 64Q60 54 81 64L84 103 72 114 73 125H47L48 114 36 103Z" fill="#302044" />
          <circle cx="60" cy="38" r="24" fill="#221545" />
          <path d="M43 37Q45 18 65 17Q78 21 79 39Q65 49 48 43Z" fill="#855ab4" />
          <path d="M45 37Q60 31 76 37" fill="none" stroke="#e6edf9" opacity=".8" />
          <rect x="51" y="75" width="18" height="14" rx="3" fill="#68388d" />
          <path d="M55 81h10" fill="none" stroke="#ffdf91" />
          <circle cx="17" cy="110" r="6" fill="#c7d0de" />
          <circle cx="102" cy="107" r="6" fill="#c7d0de" />
        </g>
      </svg>
    </div>
  );
}

export function AppShell({ children, nav }: { children: ReactNode; nav?: ReactNode }) {
  return (
    <>
      <CosmicBackdrop />
      <a className="skip-link" href="#main">Skip to main content</a>
      <DisclaimerBanner />
      <header className="app-header">
        <HeaderSky />
        <MedicalTools />
        <div className="app-header__inner">
          <img
            className="brand__logo"
            src={`${import.meta.env.BASE_URL}images/nasa-space-health-monitoring-logo.png`}
            alt="NASA Space Health Monitoring logo"
          />
          <h1 className="brand__name">NASA Space Health Monitoring Agent</h1>
          {nav && <div className="app-header__nav">{nav}</div>}
        </div>
      </header>
      <main id="main" className="page" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
