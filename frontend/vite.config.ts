import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { transformWithEsbuild, type Plugin } from "vite";

// Member 6: compiles src/sw/service-worker.ts into dist/sw.js after the build, injecting the list
// of every shipped file to precache and a content hash used as the cache name. Because the hash
// covers every file, the cache is invalidated automatically on every release.
function crewVitalsServiceWorker(): Plugin {
  let root = process.cwd();
  let outDir = "dist";
  const walk = (dir: string): string[] =>
    readdirSync(dir).flatMap((name) => {
      const full = path.join(dir, name);
      return statSync(full).isDirectory() ? walk(full) : [full];
    });
  return {
    name: "crew-vitals-service-worker",
    apply: "build",
    configResolved(config) {
      root = config.root;
      outDir = path.resolve(config.root, config.build.outDir);
    },
    async closeBundle() {
      const files = walk(outDir)
        .map((f) => path.relative(outDir, f).split(path.sep).join("/"))
        .filter((f) => f !== "sw.js" && !f.endsWith(".map") && !f.endsWith(".gitkeep"))
        .sort();
      const hash = createHash("sha256");
      for (const f of files) hash.update(f).update(readFileSync(path.join(outDir, f)));
      const version = hash.digest("hex").slice(0, 12);
      const precache = ["./", ...files.map((f) => `./${f}`)];
      const source = readFileSync(path.resolve(root, "src/sw/service-worker.ts"), "utf8");
      const out = await transformWithEsbuild(source, "service-worker.ts", {
        loader: "ts",
        format: "iife", // a classic worker script: no import/export statements allowed
        target: "es2020",
        minify: true,
        define: { __PRECACHE__: JSON.stringify(precache), __CACHE_VERSION__: JSON.stringify(version) },
      });
      writeFileSync(path.join(outDir, "sw.js"), out.code);
    },
  };
}

// Member 2's offline API (prototypes/offline_research/offline_api.py) listens on 127.0.0.1:8766.
// In `api` data mode the dev server proxies /api there so requests stay same-origin.
const API_TARGET = process.env.CREW_VITALS_API ?? "http://127.0.0.1:8766";

export default defineConfig({
  plugins: [react(), crewVitalsServiceWorker()],
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
