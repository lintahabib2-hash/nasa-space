import { describe, expect, it } from "vitest";
import { statusDisplay, worstTier } from "../../src/features/dashboard/statusDisplay";

describe("statusDisplay", () => {
  it("never words the green tier as healthy", () => {
    const d = statusDisplay("no_persistent_flag");
    expect(d.tier).toBe("green");
    expect(`${d.label} ${d.description}`.toLowerCase()).not.toContain("healthy");
  });

  it("maps Member 2's safe fallback states to unknown, never green", () => {
    for (const s of ["unknown", "insufficient_history", "insufficient_scale", "insufficient_persistence_history", "no_observations"]) {
      expect(statusDisplay(s).tier).toBe("unknown");
    }
  });

  it("treats unrecognised or missing statuses as unknown", () => {
    expect(statusDisplay("something_new").tier).toBe("unknown");
    expect(statusDisplay(undefined).tier).toBe("unknown");
  });

  it("maps review to yellow", () => {
    expect(statusDisplay("review").tier).toBe("yellow");
  });
});

describe("worstTier", () => {
  it("returns unknown for an empty region instead of green", () => {
    expect(worstTier([])).toBe("unknown");
  });

  it("does not let one missing indicator hide behind green ones", () => {
    expect(worstTier(["no_persistent_flag", "unknown"])).toBe("unknown");
  });

  it("ranks review above unknown and green", () => {
    expect(worstTier(["no_persistent_flag", "insufficient_scale", "review"])).toBe("yellow");
  });
});
