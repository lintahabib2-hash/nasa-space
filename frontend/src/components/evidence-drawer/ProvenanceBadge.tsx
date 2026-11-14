import type { ProvenanceKind } from "../../features/dashboard/types";

const LABELS: Record<string, { text: string; cls: string; help: string }> = {
  simulated: { text: "Simulated", cls: "prov--simulated", help: "Team-created demo data. Not NASA data and not a real astronaut." },
  nasa_measured: { text: "NASA measured", cls: "prov--nasa", help: "Measured by a NASA instrument or study." },
  environment_measured: { text: "NASA environment", cls: "prov--nasa", help: "Historical NASA environment telemetry. Not a person's health record." },
  analog_measured: { text: "Analog measured", cls: "prov--nasa", help: "Measured in a ground analog study (e.g. bed rest), not in spaceflight." },
  external_earth: { text: "External Earth data", cls: "prov--other", help: "Earth-based dataset, used for parser tests only." },
  manually_entered: { text: "Manually entered", cls: "prov--other", help: "Entered by hand in the daily check-in." },
  crew_self_report: { text: "Self-reported", cls: "prov--other", help: "Entered by the crew member in a local check-in." },
};

export function ProvenanceBadge({ kind }: { kind: ProvenanceKind }) {
  const p = LABELS[kind] ?? { text: kind || "unknown", cls: "prov--other", help: "Unrecognised provenance kind." };
  return (
    <span className={`prov ${p.cls}`} title={p.help} data-provenance={kind}>
      {p.text}
      <span className="sr-only">: {p.help}</span>
    </span>
  );
}
