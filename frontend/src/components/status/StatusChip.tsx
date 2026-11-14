import { statusDisplay, TIER_LABEL, type Tier } from "../../features/dashboard/statusDisplay";
import { StatusIcon } from "./StatusIcon";

/** Status chip for one API status string: colour + shape + text, never colour alone. */
export function StatusChip({ status }: { status: string }) {
  const d = statusDisplay(status);
  return (
    <span className={`chip chip--${d.tier}`} title={d.description} data-tier={d.tier}>
      <StatusIcon tier={d.tier} />
      {d.label}
    </span>
  );
}

/** Chip for an aggregated tier (e.g. a body region). */
export function TierChip({ tier, label }: { tier: Tier; label?: string }) {
  return (
    <span className={`chip chip--${tier}`} data-tier={tier}>
      <StatusIcon tier={tier} />
      {label ?? TIER_LABEL[tier]}
    </span>
  );
}
