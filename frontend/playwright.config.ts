// Browser tests (Member 6). Run `npm run build` first; the tests run against the production build,
// served by `vite preview`, because that is what gets deployed (and the only thing with a service worker).
//
//   npm run build && npm run test:e2e
//   PLAYWRIGHT_BASE_URL=https://<user>.github.io/<repo>/ npm run test:e2e   # test the LIVE site
import { defineConfig, devices } from "@playwright/test";

const live = process.env.PLAYWRIGHT_BASE_URL;
const baseURL = live ? (live.endsWith("/") ? live : `${live}/`) : "http://127.0.0.1:4173/";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: { baseURL, serviceWorkers: "allow", trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: live
    ? undefined
    : {
        command: "npm run preview -- --host 127.0.0.1 --port 4173 --strictPort",
        url: "http://127.0.0.1:4173/",
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
