import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Member 2's offline API (member2/offline_api.py) listens on 127.0.0.1:8766.
// In `api` data mode the dev server proxies /api there so requests stay same-origin.
const API_TARGET = process.env.CREW_VITALS_API ?? "http://127.0.0.1:8766";

export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { rollupOptions: { output: { manualChunks: { charts: ["recharts"] } } }, chunkSizeWarningLimit: 700 },
  server: {
    proxy: { "/api": { target: API_TARGET, changeOrigin: false } },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}"],
  },
});
