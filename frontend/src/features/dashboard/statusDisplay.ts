// Presentation mapping only: API status string -> display tier, label and symbol.
// It contains no medical thresholds. Every decision comes from the API's `status`.
// "No sustained change" is deliberately NOT worded as "healthy". Without a demo flag
// we have no evidence either way (Member 2 handoff).

export type Tier = "green" | "yellow" | "red" | "unknown";

export interface StatusDisplay {
  tier: Tier;
  label: string;
  description: string;
}

const MAP: Record<string, StatusDisplay> = {
  no_persistent_flag: {
    tier: "green",
    label: "No sustained change",
    description: "No sustained deviation from this person's statistical reference under the demo rule. Keep your routine.",
  },
  review: {
    tier: "yellow",
    label: "Review",
    description: "Several consecutive readings are away from this person's reference. Do the self-care steps now and recheck within 24 hours.",
  },
  // Reserved for when the API emits an escalation tier (requested from Member 2).
  escalate: {
    tier: "red",
    label: "Contact flight surgeon",
    description: "Far outside the reference, persistent, or with symptoms. Follow the interim steps while you wait for a reply.",
  },
  insufficient_history: {
    tier: "unknown",
    label: "Not enough history",
    description: "Too few earlier readings to build a personal reference.",
  },
  insufficient_scale: {
    tier: "unknown",
    label: "Not enough spread",
    description: "Earlier readings barely vary (zero MAD), so no robust z-score can be computed.",
  },
  insufficient_persistence_history: {
    tier: "unknown",
    label: "Building history",
    description: "There is a reference, but too few recent readings to judge persistence.",
  },
  no_observations: {
    tier: "unknown",
    label: "No data",
    description: "No readings stored for this indicator.",
  },
  unknown: {
    tier: "unknown",
    label: "Unknown",
    description: "Status cannot be determined, for example because the latest reading is missing.",
  },
};

export function statusDisplay(status: string | null | undefined): StatusDisplay {
  if (status && MAP[status]) return MAP[status];
  return { ...MAP.unknown, description: `Unrecognised status "${status ?? "none"}". Treated as unknown.` };
}

const ORDER: Record<Tier, number> = { green: 0, unknown: 1, yellow: 2, red: 3 };

/** The worst tier among several statuses. With no statuses, the result is "unknown", never green. */
export function worstTier(statuses: string[]): Tier {
  if (statuses.length === 0) return "unknown";
  return statuses
    .map((s) => statusDisplay(s).tier)
    .reduce((a, b) => (ORDER[b] > ORDER[a] ? b : a), "green" as Tier);
}

export const TIER_LABEL: Record<Tier, string> = {
  green: "No sustained change",
  yellow: "Review",
  red: "Contact flight surgeon",
  unknown: "Not enough data",
};
