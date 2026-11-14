import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BodyMap } from "../../src/components/body-map/BodyMap";
import { CommsDelayBanner } from "../../src/components/environment-selector/CommsDelayBanner";
import { EvidenceDrawer } from "../../src/components/evidence-drawer/EvidenceDrawer";
import { StatusChip } from "../../src/components/status/StatusChip";
import { FIXTURE_BUNDLES, KNOWLEDGE } from "../../src/features/dashboard/dataSource";
import { DashboardPage } from "../../src/features/dashboard/DashboardPage";

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
    expect(screen.getByTestId("region-panel")).toHaveTextContent("Brain and behavior");
    expect(screen.getByTestId("comms-banner")).toHaveTextContent("Mars transit");
    await userEvent.click(screen.getByLabelText("Lunar base"));
    expect(screen.getByTestId("comms-banner")).toHaveTextContent("1.3 seconds");
  });

  it("always shows that the scenario is simulated", () => {
    render(<DashboardPage />);
    expect(screen.getByTestId("data-notice")).toHaveTextContent(/SIMULATED demo data/);
  });
});
