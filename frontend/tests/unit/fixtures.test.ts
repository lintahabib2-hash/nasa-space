import { describe, expect, it } from "vitest";
import { FIXTURE_BUNDLES, KNOWLEDGE } from "../../src/features/dashboard/dataSource";

describe("simulated UI fixtures", () => {
  it("are all labelled simulated (X01) and never as NASA data", () => {
    for (const b of FIXTURE_BUNDLES) {
      expect(b.provenance_kind).toBe("simulated");
      expect(b.source_id).toBe("X01");
      for (const i of b.indicators) {
        expect(i.provenance_kind).toBe("simulated");
        expect(i.result.provenance_kind).toBe("simulated");
        expect(i.result.not_medical_diagnosis).toBe(true);
      }
    }
  });

  it("cover stable, drift and missing-data scenarios", () => {
    expect(FIXTURE_BUNDLES.map((b) => b.scenario)).toEqual(["stable", "gradual_drift", "missing_data"]);
  });

  it("drift scenario triggers review; stable scenario's single noisy point does not", () => {
    const [stable, drift] = FIXTURE_BUNDLES;
    expect(drift.indicators.some((i) => i.result.status === "review")).toBe(true);
    const hr = stable.indicators.find((i) => i.measurement === "resting_heart_rate")!;
    expect(Math.abs(hr.result.robust_z ?? 0)).toBeGreaterThanOrEqual(3);
    expect(hr.result.status).toBe("no_persistent_flag");
  });

  it("missing latest reading yields unknown, never a green status", () => {
    const missing = FIXTURE_BUNDLES[2];
    const sleep = missing.indicators.find((i) => i.measurement === "sleep_duration")!;
    expect(sleep.series.at(-1)?.value).toBeNull();
    expect(sleep.result.status).toBe("unknown");
  });

  it("every indicator has a knowledge card and a region", () => {
    for (const i of FIXTURE_BUNDLES[0].indicators) {
      const card = KNOWLEDGE.indicators[i.measurement];
      expect(card, i.measurement).toBeDefined();
      expect(KNOWLEDGE.regions[card.region], card.region).toBeDefined();
    }
  });

  it("contain no NaN or infinite numbers", () => {
    const text = JSON.stringify(FIXTURE_BUNDLES);
    expect(text).not.toMatch(/NaN|Infinity/);
  });
});
