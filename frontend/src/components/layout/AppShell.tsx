import type { ReactNode } from "react";
import { DisclaimerBanner } from "./DisclaimerBanner";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <a className="skip-link" href="#main">Skip to main content</a>
      <DisclaimerBanner />
      <header className="app-header">
        <div className="app-header__inner">
          <div className="brand">
            <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
              <circle cx="13" cy="13" r="12" fill="none" stroke="var(--accent)" strokeWidth="2" />
              <path d="M4 14h4l2-5 3 9 2.5-6 1.5 2H22" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Crew Vitals
            <span className="brand__tag">Crew readiness &amp; context monitor</span>
          </div>
        </div>
      </header>
      <main id="main" className="page" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
