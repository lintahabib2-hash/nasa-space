import type { Tier } from "../../features/dashboard/statusDisplay";

// Each tier has its own shape and symbol, so status reads without colour:
//   green ✓ circle · yellow ! triangle · red ! octagon · unknown ? dashed circle
export function StatusIcon({ tier, size = 18 }: { tier: Tier; size?: number }) {
  const common = { width: size, height: size, viewBox: "0 0 20 20", "aria-hidden": true, className: "status-icon" } as const;
  switch (tier) {
    case "green":
      return (
        <svg {...common} data-tier="green">
          <circle cx="10" cy="10" r="9" fill="var(--good)" />
          <path d="M5.5 10.5l3 3 6-6.5" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "yellow":
      return (
        <svg {...common} data-tier="yellow">
          <path d="M10 1.8l8.6 15.4H1.4z" fill="var(--warning)" stroke="#6b4a00" strokeWidth="1" strokeLinejoin="round" />
          <path d="M10 7v5" stroke="#1a1300" strokeWidth="2.2" strokeLinecap="round" />
          <circle cx="10" cy="14.8" r="1.2" fill="#1a1300" />
        </svg>
      );
    case "red":
      return (
        <svg {...common} data-tier="red">
          <path d="M6.3 1h7.4L19 6.3v7.4L13.7 19H6.3L1 13.7V6.3z" fill="var(--critical)" />
          <path d="M10 5v6" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
          <circle cx="10" cy="14.5" r="1.3" fill="#fff" />
        </svg>
      );
    default:
      return (
        <svg {...common} data-tier="unknown">
          <circle cx="10" cy="10" r="8.5" fill="var(--surface)" stroke="var(--unknown)" strokeWidth="1.6" strokeDasharray="3 2" />
          <path d="M7.6 7.6a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5v.4" fill="none" stroke="var(--text-2)" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="10" cy="14.6" r="1.1" fill="var(--text-2)" />
        </svg>
      );
  }
}
