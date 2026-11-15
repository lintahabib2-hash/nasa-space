// E2E: two contrasting scenarios + missing data
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// Runs against the production build. The same checks run again with the network switched off in
// offline.spec.ts. Relative URLs ("./?crew=...") keep this working on a sub-path host.
import { expect, test } from "@playwright/test";

const open = (crew: string, env = "mars") => `./?crew=${crew}&env=${env}`;

test.describe("simulated crew scenarios", () => {
  test("crew_01 stable: no reading is flagged for review", async ({ page }) => {
    await page.goto(open("crew_01"));
    await expect(page.getByRole("heading", { name: "Today's readings" })).toBeVisible();
    await expect(page.locator(".overview .chip--yellow, .overview .chip--red")).toHaveCount(0);
    await expect(page.locator(".overview .chip--green").first()).toBeVisible();
  });

  test("crew_02 gradual drift: sustained drift is shown as Review with a reason", async ({ page }) => {
    await page.goto(open("crew_02"));
    const review = page.locator(".overview .chip--yellow", { hasText: "Review" });
    await expect(review.first()).toBeVisible();
    expect(await review.count()).toBeGreaterThanOrEqual(2);
  });

  test("crew_03 missing data: gaps are Unknown / Not enough history, never 'healthy'", async ({ page }) => {
    await page.goto(open("crew_03"));
    await expect(page.locator(".overview .chip--unknown").first()).toBeVisible();
    const text = await page.locator(".overview").innerText();
    expect(text).toMatch(/Unknown|Not enough/);
    expect(text).not.toMatch(/NaN|undefined|null/);
  });

  test("every scenario is labelled simulated and the NASA environment card stays separate", async ({ page }) => {
    for (const crew of ["crew_01", "crew_02", "crew_03"]) {
      await page.goto(open(crew));
      await expect(page.getByTestId("data-notice")).toContainText(/simulated/i);
      const card = page.getByTestId("env-card");
      await expect(card).toContainText(/historical instrument data/i);
      await expect(card).not.toContainText(/review|no sustained change/i);
    }
  });

  test("changing the environment updates the comms-delay banner", async ({ page }) => {
    await page.goto(open("crew_02", "station"));
    const delay = page.locator(".signal__delay").first();
    await expect(delay).toBeVisible();
    const station = await delay.innerText();
    await page.goto(open("crew_02", "mars"));
    await expect(page.locator(".signal__delay").first()).toBeVisible();
    expect(await page.locator(".signal__delay").first().innerText()).not.toEqual(station);
  });
});
