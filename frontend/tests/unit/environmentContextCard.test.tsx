import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvironmentContextCard } from "../../src/features/environment-context/EnvironmentContextCard";
import { DashboardPage } from "../../src/features/dashboard/DashboardPage";

vi.mock("../../src/components/charts/TrendChart", () => ({
  TrendChart: ({
    baseline,
    band,
  }: {
    baseline: number | null;
    band?: unknown;
  }) => (
    <div
      data-testid="environment-trend"
      data-baseline={baseline === null ? "null" : String(baseline)}
      data-has-band={String(band !== undefined)}
    />
  ),
}));

const CITATION =
  "Data and visualizations are courtesy of the Environmental Data Application (EDA) " +
  "(https://visualization.osdr.nasa.gov/eda/). Version: not displayed on the site (accessed 14 Nov 2026).";

describe("EnvironmentContextCard", () => {
  it("shows measured provenance, cited source, null baseline, and non-diagnostic wording", () => {
    const { container } = render(<EnvironmentContextCard />);

    expect(container.querySelector("[data-provenance='nasa_measured']")).not.toBeNull();
    expect(screen.getByText(CITATION)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "NASA EDA (RR-1)" })).toHaveAttribute(
      "href",
      "https://visualization.osdr.nasa.gov/eda/",
    );
    expect(
      screen.getByText("historical instrument data, not this crew member's exposure or dose"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("environment-trend")).toHaveAttribute("data-baseline", "null");
    expect(screen.getByTestId("environment-trend")).toHaveAttribute("data-has-band", "false");
    expect(container.querySelector("[data-tier]")).toBeNull();
  });

  it("is mounted as a separate card in DashboardPage", () => {
    render(<DashboardPage />);

    expect(
      screen.getByRole("region", {
        name: "NASA RR-1 EDA: historical experimental environment",
      }),
    ).toBeInTheDocument();
  });
});
