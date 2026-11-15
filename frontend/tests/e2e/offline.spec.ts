// E2E: app works with network disabled
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// 1. Load online once; wait until the service worker reports "Offline ready".
// 2. Switch the browser offline and reload. The app must still open.
// 3. With the network off: two contrasting scenarios + missing data, a saved check-in,
//    validation errors, and recovery of records if localStorage is cleared.
import { expect, test, type Page } from "@playwright/test";

const open = (crew: string) => `./?crew=${crew}&env=mars`;
const badge = (page: Page) => page.getByTestId("offline-badge");

async function mirrored(page: Page): Promise<boolean> {
  return page.evaluate(
    () =>
      new Promise<boolean>((resolve) => {
        const req = indexedDB.open("crew-vitals-mirror");
        req.onerror = () => resolve(false);
        req.onsuccess = () => {
          const db = req.result;
          if (!db.objectStoreNames.contains("kv")) { db.close(); resolve(false); return; }
          const get = db.transaction("kv").objectStore("kv").get("crew-vitals.checkins.v1");
          get.onsuccess = () => { db.close(); resolve(typeof get.result === "string"); };
          get.onerror = () => { db.close(); resolve(false); };
        };
      }),
  );
}

test("the deployed app works fully offline after the first load", async ({ page, context, baseURL }) => {
  const external: string[] = [];
  const pageErrors: string[] = [];
  const origin = new URL(baseURL!).origin;
  page.on("request", (r) => { if (!r.url().startsWith(origin) && !r.url().startsWith("data:") && !r.url().startsWith("blob:")) external.push(r.url()); });
  page.on("pageerror", (e) => pageErrors.push(String(e)));

  await test.step("online first load registers the service worker and caches the app", async () => {
    await page.goto("./");
    await expect(badge(page)).toHaveAttribute("data-sw-state", "ready");
    await expect(badge(page)).toContainText("Offline ready");
    await page.reload(); // from now on the page is controlled by the worker
    await page.waitForFunction(() => !!navigator.serviceWorker.controller);
    const cached = await page.evaluate(async () => {
      const names = (await caches.keys()).filter((k) => k.startsWith("crew-vitals-"));
      const entries = names.length ? (await (await caches.open(names[0])).keys()).length : 0;
      return { names: names.length, entries };
    });
    expect(cached.names).toBe(1);
    expect(cached.entries).toBeGreaterThanOrEqual(20);
  });

  await context.setOffline(true);

  await test.step("network off: reload still shows the dashboard", async () => {
    await page.reload();
    await expect(badge(page)).toHaveAttribute("data-online", "false");
    await expect(badge(page)).toContainText("Offline: using saved data");
    await expect(page.getByRole("heading", { name: "Today's readings" })).toBeVisible();
  });

  await test.step("network off: two contrasting scenarios + missing data", async () => {
    await page.goto(open("crew_01"));
    await expect(page.getByRole("heading", { name: "Today's readings" })).toBeVisible();
    await expect(page.locator(".overview .chip--yellow, .overview .chip--red")).toHaveCount(0);

    await page.goto(open("crew_02"));
    await expect(page.locator(".overview .chip--yellow", { hasText: "Review" }).first()).toBeVisible();

    await page.goto(open("crew_03"));
    await expect(page.locator(".overview .chip--unknown").first()).toBeVisible();
    expect(await page.locator(".overview").innerText()).not.toMatch(/NaN|undefined|null/);
    await expect(page.getByTestId("env-card")).toContainText(/historical instrument data/i);
  });

  await test.step("network off: a check-in is validated, saved and survives reload", async () => {
    await page.goto("./#/checkin");
    await page.locator("#ci-sleep_duration").fill("99");
    await page.locator("#ci-mood").selectOption("3");
    await page.locator("#ci-stress").selectOption("2");
    await page.locator("#ci-exercise_minutes").fill("30");
    await page.getByRole("button", { name: /Save today's check-in/ }).click();
    await expect(page.getByRole("alert").filter({ hasText: /sleep/i })).toBeVisible();
    await expect(page.getByTestId("history")).toHaveCount(0);

    await page.locator("#ci-sleep_duration").fill("7.5");
    await page.getByRole("button", { name: /Save today's check-in/ }).click();
    await expect(page.getByText("Check-in saved on this device.")).toBeVisible();
    await expect(page.getByTestId("history")).toContainText("7.5 h sleep");

    await page.reload();
    await expect(page.getByTestId("history")).toContainText("7.5 h sleep");
  });

  await test.step("records are restored from the IndexedDB mirror if localStorage is wiped", async () => {
    await expect.poll(() => mirrored(page), { timeout: 15_000 }).toBe(true);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(page.getByTestId("history")).toContainText("7.5 h sleep");
  });

  await test.step("nothing was requested from outside the app, and no script errors occurred", async () => {
    expect(external).toEqual([]);
    expect(pageErrors).toEqual([]);
  });

  await context.setOffline(false);
});
