// API client: live API first, snapshot fallback, honest about which one answered.
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it, vi } from "vitest";
import { ApiClientError, apiGet, getBaseline, getBaselines, getEnvironment, snapshotUrl } from "../../src/services/apiClient";
import { isApiBaselineResponse } from "../../src/types/contracts";

const DATA = path.resolve(__dirname, "../../public/data");
const file = (name: string) => JSON.parse(readFileSync(path.join(DATA, name), "utf8"));

/** fetch double that serves the real snapshot files from public/data (like the deployed site would). */
function snapshotFetch(): typeof fetch {
  return (async (url: string) => {
    const m = /\/data\/([\w.-]+\.json)$/.exec(String(url));
    if (!m) return new Response("nope", { status: 404 });
    return new Response(JSON.stringify(file(m[1])), { status: 200 });
  }) as unknown as typeof fetch;
}
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

describe("snapshotUrl", () => {
  it("maps API paths to snapshot files under the base URL", () => {
    expect(snapshotUrl("/api/environment", "./")).toBe("./data/environment.json");
    expect(snapshotUrl("/api/knowledge", "/nasa-space/")).toBe("/nasa-space/data/knowledge.json");
    expect(snapshotUrl("/api/baseline/all?subject_id=X01_stable", "./")).toBe("./data/baselines.json");
    expect(snapshotUrl("/api/baseline?subject_id=a&measurement=b", "./")).toBe("./data/baselines.json");
  });
  it("returns null for paths with no snapshot (writes are never faked offline)", () => {
    expect(snapshotUrl("/api/checkins", "./")).toBeNull();
    expect(snapshotUrl("/api/observations", "./")).toBeNull();
  });
});

describe("apiGet", () => {
  it("uses the snapshot only when no API is configured", async () => {
    const fetchImpl = vi.fn(snapshotFetch());
    const r = await apiGet("/api/environment", { apiBase: null, baseUrl: "./", fetchImpl });
    expect(r.origin).toBe("snapshot");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(String(fetchImpl.mock.calls[0][0])).toBe("./data/environment.json");
  });

  it("prefers the live API and reports origin 'api'", async () => {
    const fetchImpl = vi.fn(async () => json({ hello: "live" })) as unknown as typeof fetch;
    const r = await apiGet<{ hello: string }>("/api/environment", { apiBase: "http://x:8000", fetchImpl });
    expect(r).toEqual({ data: { hello: "live" }, origin: "api" });
  });

  it("falls back to the snapshot when the API is down, and says so", async () => {
    const calls: string[] = [];
    const fetchImpl = (async (url: string) => {
      calls.push(String(url));
      if (String(url).startsWith("http://x:8000")) throw new TypeError("Failed to fetch");
      return snapshotFetch()(url);
    }) as unknown as typeof fetch;
    const r = await getEnvironment({ apiBase: "http://x:8000", baseUrl: "./", fetchImpl });
    expect(r.origin).toBe("snapshot");
    expect(calls).toEqual(["http://x:8000/api/environment", "./data/environment.json"]);
    expect(r.data.provenance_kind).toBe("nasa_measured");
  });

  it("falls back on an HTTP error from the API", async () => {
    const fetchImpl = (async (url: string) =>
      String(url).startsWith("http://x") ? json({ error: "boom" }, 500) : snapshotFetch()(url)) as unknown as typeof fetch;
    expect((await getEnvironment({ apiBase: "http://x:8000", baseUrl: "./", fetchImpl })).origin).toBe("snapshot");
  });

  it("falls back when the API hangs (timeout)", async () => {
    const fetchImpl = ((url: string, init?: RequestInit) =>
      String(url).startsWith("http://x")
        ? new Promise((_, reject) => init?.signal?.addEventListener("abort", () => reject(new Error("aborted"))))
        : snapshotFetch()(url)) as unknown as typeof fetch;
    const r = await getEnvironment({ apiBase: "http://x:8000", baseUrl: "./", fetchImpl, timeoutMs: 20 });
    expect(r.origin).toBe("snapshot");
  });

  it("throws a descriptive error when both the API and the snapshot fail", async () => {
    const fetchImpl = (async () => new Response("nope", { status: 404 })) as unknown as typeof fetch;
    const err = await apiGet("/api/environment", { apiBase: "http://x:8000", baseUrl: "./", fetchImpl }).catch((e) => e);
    expect(err).toBeInstanceOf(ApiClientError);
    expect(err.attempts).toHaveLength(2);
    expect(err.message).toMatch(/live API.*snapshot/);
  });

  it("refuses paths that have no snapshot instead of inventing data", async () => {
    await expect(apiGet("/api/checkins", { apiBase: null, baseUrl: "./", fetchImpl: snapshotFetch() })).rejects.toBeInstanceOf(ApiClientError);
  });

  it("does not swallow a caller's abort", async () => {
    const ctrl = new AbortController();
    ctrl.abort(new Error("user left"));
    const fetchImpl = (async (_: string, init?: RequestInit) => { init?.signal?.throwIfAborted(); return json({}); }) as unknown as typeof fetch;
    await expect(apiGet("/api/environment", { apiBase: null, baseUrl: "./", fetchImpl, signal: ctrl.signal })).rejects.toThrow();
  });
});

describe("snapshot content (the real files the deployed site serves)", () => {
  it("baselines resolve per subject and per measurement, with a safe 'no_observations' for unknowns", async () => {
    const opts = { apiBase: null, baseUrl: "./", fetchImpl: snapshotFetch() };
    const drift = await getBaseline("X01_downward_drift", "sleep_duration", opts);
    expect(drift.origin).toBe("snapshot");
    expect(drift.data.status).toBe("review");
    const stable = await getBaselines("X01_stable", opts);
    expect(stable.data.map((b) => b.measurement)).toEqual(["sleep_duration"]);
    const ghost = await getBaseline("ghost", "sleep_duration", opts);
    expect(ghost.data.status).toBe("no_observations");
    expect(isApiBaselineResponse(ghost.data)).toBe(true);
  });

  it("every snapshot baseline satisfies the shared response contract and is non-diagnostic", () => {
    for (const results of Object.values(file("baselines.json")) as unknown[][]) {
      for (const r of results) expect(isApiBaselineResponse(r), JSON.stringify(r)).toBe(true);
    }
  });

  it("environment snapshot keeps its citation and never carries a crew subject", () => {
    const env = file("environment.json");
    expect(env.subject_id).toBeNull();
    expect(env.citation).toBeTruthy();
    expect(env.provenance_kind).toBe("nasa_measured");
  });

  it("manifest says the snapshot contains no real astronaut data and lists every data file", () => {
    const m = file("manifest.json");
    expect(m.contains_real_astronaut_data).toBe(false);
    expect(Object.keys(m.files).sort()).toEqual(["baselines.json", "environment.json", "knowledge.json", "sources.json"]);
  });
});

describe("isApiBaselineResponse", () => {
  it("rejects unknown statuses, missing reasons and a false non-diagnostic flag", () => {
    const ok = file("baselines.json").X01_stable[0];
    expect(isApiBaselineResponse(ok)).toBe(true);
    expect(isApiBaselineResponse({ ...ok, status: "healthy" })).toBe(false);
    expect(isApiBaselineResponse({ ...ok, reasons: [] })).toBe(false);
    expect(isApiBaselineResponse({ ...ok, not_medical_diagnosis: false })).toBe(false);
    expect(isApiBaselineResponse(null)).toBe(false);
  });
});
