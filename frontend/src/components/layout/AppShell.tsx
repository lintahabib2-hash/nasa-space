import type { ReactNode } from "react";
import { DisclaimerBanner } from "./DisclaimerBanner";
import { Cosmos, HeaderScene } from "./SpaceScene";

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

export function AppShell({ children, nav }: { children: ReactNode; nav?: ReactNode }) {
  return (
    <>
      <Cosmos />
      <a className="skip-link" href="#main">Skip to main content</a>
      <DisclaimerBanner />
      <header className="app-header">
        <HeaderScene />
        <div className="app-header__inner">
          <MissionPatch />
          <div>
            <h1 className="brand__name">Crew Vitals</h1>
            <p className="brand__tag">Daily crew readiness, compared with each astronaut&apos;s own baseline</p>
          </div>
          <span className="brand__event">NASA Space Apps Challenge 2026</span>
          {nav && <div className="app-header__nav">{nav}</div>}
        </div>
      </header>
      <main id="main" className="page" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
