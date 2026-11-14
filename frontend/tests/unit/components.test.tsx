import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BodyMap } from "../../src/components/body-map/BodyMap";
import { TrendChart } from "../../src/components/charts/TrendChart";
import { CommsDelayBanner } from "../../src/components/environment-selector/CommsDelayBanner";
import { EvidenceDrawer } from "../../src/components/evidence-drawer/EvidenceDrawer";
import { StatusChip } from "../../src/components/status/StatusChip";
import { FIXTURE_BUNDLES, KNOWLEDGE } from "../../src/features/dashboard/dataSource";
import { DashboardPage } from "../../src/features/dashboard/DashboardPage";
import { EnvironmentContextCard } from "../../src/features/environment-context/EnvironmentContextCard";
import environmentSample from "../../src/features/environment-context/fixtures/environment.sample.json";

describe("StatusChip", () => {
  it("shows a text label and a tier-specific icon, not colour alone", () => {
    const { container } = render(<StatusChip status="review" />);
    expect(screen.getByText("Review")).toBeInTheDocument();
    expect(container.querySelector("svg[data-tier='yellow']")).not.toBeNull();
  });
});

describe("BodyMap", () => {
  const regions = [
    { id: "brain", label: "Brain and behavior", tier: "yellow" as const },
    { id: "cardiovascular", label: "Heart and blood vessels", tier: "green" as const },
    { id: "immune", label: "Immune system (whole body)", tier: "unknown" as const },
  ];

  it("regions are keyboard operable", async () => {
    const onSelect = vi.fn();
    render(<BodyMap regions={regions} selected="brain" onSelect={onSelect} />);
    const heart = screen.getByRole("button", { name: /Heart and blood vessels: No sustained change/ });
    heart.focus();
    await userEvent.keyboard("{Enter}");
    expect(onSelect).toHaveBeenCalledWith("cardiovascular");
    await userEvent.keyboard(" ");
    expect(onSelect).toHaveBeenCalledTimes(2);
  });

  it("marks the selected region as pressed and lists whole-body systems as buttons", () => {
    render(<BodyMap regions={regions} selected="brain" onSelect={() => {}} />);
    expect(screen.getByRole("button", { name: /Brain and behavior/ })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: /Immune system/ })).toHaveAttribute("aria-pressed", "false");
  });
});

describe("CommsDelayBanner", () => {
  it("adds flight-surgeon guidance only when an indicator needs action", () => {
    const env = KNOWLEDGE.environments.mars;
    const { rerender } = render(<CommsDelayBanner env={env} alert={false} />);
    expect(screen.queryByText(/If you need the flight surgeon/)).toBeNull();
    rerender(<CommsDelayBanner env={env} alert />);
    expect(screen.getByText(/If you need the flight surgeon/)).toBeInTheDocument();
  });
});

describe("TrendChart time axis", () => {
  const pt = (timestamp_utc: string, value: number | null) => ({ timestamp_utc, value, quality_state: value === null ? "missing" : "valid" });

  it("breaks the line across a long unrecorded gap and lists only real readings", () => {
    const series = [pt("2026-10-16T06:00:00Z", 7), pt("2026-10-17T06:00:00Z", 7.2), pt("2026-10-18T06:00:00Z", 6.9), pt("2026-11-10T06:00:00Z", 5.1), pt("2026-11-11T06:00:00Z", 5)];
    const { container } = render(<TrendChart label="Sleep" units="hours" series={series} baseline={7} />);
    expect(screen.getByText(/Line breaks where no readings were recorded/)).toBeInTheDocument();
    expect(container.querySelector("[role='img']")?.getAttribute("aria-label")).toMatch(/1 long gap with no readings/);
    expect(container.querySelectorAll("table tbody tr")).toHaveLength(5);
  });

  it("shows times, not just dates, for sub-daily instrument data", () => {
    const series = [pt("2014-09-20T03:59:00Z", 2641), pt("2014-09-20T04:04:00Z", 2646), pt("2014-09-20T04:09:00Z", 2650)];
    const { container } = render(<TrendChart label="CO2" units="ppm" series={series} baseline={null} />);
    expect(screen.getByRole("columnheader", { name: /Time \(UTC\)/ })).toBeInTheDocument();
    expect(container.querySelector("table tbody tr td")?.textContent).toBe("2014-09-20 03:59 UTC");
  });
});

describe("EnvironmentContextCard with the real chart (Member 4, NASA OSDR EDA RR-1)", () => {
  it("plots all 300 sample readings, shows limitations, and has no crew status", () => {
    render(<EnvironmentContextCard />);
    const card = screen.getByTestId("env-card");
    expect(card.querySelectorAll("table tbody tr")).toHaveLength(300);
    expect(card).toHaveTextContent(/Not personal exposure or effective dose/);
    expect(card).toHaveTextContent(/2646 ppm/);
    expect(card.querySelector(".chip")).toBeNull();
    expect(environmentSample.subject_id).toBeNull();
  });

  it("does not change when the crew member changes", async () => {
    render(<DashboardPage />);
    const before = screen.getByTestId("env-card").textContent;
    await userEvent.click(screen.getByLabelText(/Crew 03/));
    expect(screen.getByTestId("env-card").textContent).toBe(before);
  });
});

describe("EvidenceDrawer", () => {
  const drift = FIXTURE_BUNDLES[1];
  const sleep = drift.indicators.find((i) => i.measurement === "sleep_duration")!;

  it("shows provenance, reasons, sources and limitations, and closes on Escape", async () => {
    const onClose = vi.fn();
    render(<EvidenceDrawer indicator={sleep} knowledge={KNOWLEDGE} onClose={onClose} />);
    const dialog = screen.getByRole("dialog", { name: /Evidence: Sleep duration/ });
    expect(within(dialog).getAllByText(/Not NASA data/).length).toBeGreaterThan(0);
    expect(dialog.querySelector("[data-provenance='simulated']")).not.toBeNull();
    for (const reason of sleep.result.reasons) expect(within(dialog).getAllByText(reason).length).toBeGreaterThan(0);
    expect(within(dialog).getByRole("link", { name: /Risks of Human Spaceflight/ })).toHaveAttribute("href", "https://www.nasa.gov/hrp/risks/");
    expect(within(dialog).getByText(/No flag does not mean healthy/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Close/ })).toHaveFocus();
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalled();
  });
});

describe("DashboardPage (simulated fixtures)", () => {
  it("opens on the most urgent region and updates the comms banner when the environment changes", async () => {
    render(<DashboardPage />);
    // default subject is crew_01 (stable); switch to the drift scenario
    await userEvent.click(screen.getByLabelText(/Crew 02/));
    // Wording comes from Member 1's knowledge file; assert against it, not literal copy.
    const { mars, lunar } = KNOWLEDGE.environments;
    expect(screen.getByTestId("region-panel")).toHaveTextContent(KNOWLEDGE.regions.brain.label);
    expect(screen.getByTestId("comms-banner")).toHaveTextContent(mars.label);
    await userEvent.click(screen.getByLabelText(lunar.label));
    expect(screen.getByTestId("comms-banner")).toHaveTextContent(lunar.label);
    expect(screen.getByTestId("comms-banner")).toHaveTextContent(lunar.one_way_delay);
  });

  it("always shows that the scenario is simulated", () => {
    render(<DashboardPage />);
    expect(screen.getByTestId("data-notice")).toHaveTextContent(/SIMULATED demo data/);
  });
});
