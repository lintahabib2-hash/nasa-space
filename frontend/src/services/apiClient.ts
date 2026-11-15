// API client (online) with static-snapshot fallback (offline)
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// Every read tries the live API first (only if VITE_API_BASE is set) and otherwise, or when the
// API is unreachable, falls back to the static snapshot written by
// backend/scripts/export_static_snapshot.py. Callers learn which one answered via `origin`, so the
// UI can say "live" or "saved snapshot" and never pretend a cached answer is live.
import type { ApiBaselineResponse, EnvironmentSeries, Knowledge, SnapshotManifest } from "../types/contracts";

export type DataOrigin = "api" | "snapshot";
export interface Loaded<T> { data: T; origin: DataOrigin }

export class ApiClientError extends Error {
  constructor(message: string, readonly attempts: string[] = []) {
    super(attempts.length ? `${message} (${attempts.join("; ")})` : message);
    this.name = "ApiClientError";
  }
}

export interface RequestOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
  /** Override for tests; defaults to VITE_API_BASE. null/"" = snapshot only. */
  apiBase?: string | null;
  /** Override for tests; defaults to Vite's BASE_URL. */
  baseUrl?: string;
}

const SIMPLE_SNAPSHOTS: Record<string, string> = {
  "/api/environment": "environment.json",
  "/api/knowledge": "knowledge.json",
  "/api/sources": "sources.json",
};

export function configuredApiBase(): string | null {
  const v = import.meta.env.VITE_API_BASE;
  return typeof v === "string" && v.trim() ? v.trim().replace(/\/+$/, "") : null;
}

/** Which snapshot file stands in for an API path, or null if none does. */
export function snapshotUrl(path: string, baseUrl: string = import.meta.env.BASE_URL): string | null {
  const pathname = path.split("?")[0];
  const file = SIMPLE_SNAPSHOTS[pathname] ?? (pathname === "/api/baseline" || pathname === "/api/baseline/all" ? "baselines.json" : null);
  return file ? `${baseUrl}data/${file}` : null;
}

async function fetchJson(url: string, o: RequestOptions): Promise<unknown> {
  o.signal?.throwIfAborted(); // an already-aborted caller signal must stop us before any request
  const doFetch = o.fetchImpl ?? fetch;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new Error("timed out")), o.timeoutMs ?? 4000);
  const onAbort = () => ctrl.abort(o.signal?.reason);
  o.signal?.addEventListener("abort", onAbort, { once: true });
  try {
    const res = await doFetch(url, { signal: ctrl.signal, headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
    o.signal?.removeEventListener("abort", onAbort);
  }
}

function noObservations(subjectId: string, measurement: string): ApiBaselineResponse {
  return {
    subject_id: subjectId, measurement, status: "no_observations", quality_state: "missing",
    reasons: ["No readings stored for this indicator"], severity_basis: "unvalidated_demo_statistical_rule",
    not_medical_diagnosis: true, current_value: null, baseline_value: null, robust_z: null,
    history_count: 0, rejected_history_count: 0,
  };
}

/** Pick the API's answer out of a snapshot file. */
function fromSnapshot(path: string, raw: unknown): unknown {
  const url = new URL(path, "http://snapshot.invalid");
  if (url.pathname === "/api/baseline" || url.pathname === "/api/baseline/all") {
    const subject = url.searchParams.get("subject_id") ?? "";
    const list = ((raw as Record<string, ApiBaselineResponse[]>)[subject] ?? []);
    if (url.pathname === "/api/baseline/all") return list;
    const measurement = url.searchParams.get("measurement") ?? "";
    return list.find((b) => b.measurement === measurement) ?? noObservations(subject, measurement);
  }
  return raw;
}

export async function apiGet<T>(path: string, options: RequestOptions = {}): Promise<Loaded<T>> {
  const attempts: string[] = [];
  const base = options.apiBase === undefined ? configuredApiBase() : options.apiBase;
  if (base) {
    try {
      return { data: (await fetchJson(`${base}${path}`, options)) as T, origin: "api" };
    } catch (e) {
      if (options.signal?.aborted) throw e;
      attempts.push(`live API: ${(e as Error).message}`);
    }
  }
  const snap = snapshotUrl(path, options.baseUrl);
  if (!snap) throw new ApiClientError(`No offline snapshot exists for ${path}`, attempts);
  try {
    return { data: fromSnapshot(path, await fetchJson(snap, options)) as T, origin: "snapshot" };
  } catch (e) {
    if (options.signal?.aborted) throw e;
    attempts.push(`snapshot: ${(e as Error).message}`);
    throw new ApiClientError(`Could not load ${path}`, attempts);
  }
}

export const getEnvironment = (o?: RequestOptions) => apiGet<EnvironmentSeries>("/api/environment", o);
export const getKnowledge = (o?: RequestOptions) => apiGet<Knowledge>("/api/knowledge", o);
export const getSources = (o?: RequestOptions) => apiGet<Record<string, unknown>>("/api/sources", o);
export const getBaselines = (subjectId: string, o?: RequestOptions) =>
  apiGet<ApiBaselineResponse[]>(`/api/baseline/all?subject_id=${encodeURIComponent(subjectId)}`, o);
export const getBaseline = (subjectId: string, measurement: string, o?: RequestOptions) =>
  apiGet<ApiBaselineResponse>(`/api/baseline?subject_id=${encodeURIComponent(subjectId)}&measurement=${encodeURIComponent(measurement)}`, o);

/** The snapshot manifest (static deploy only). Tells the UI what data is available offline. */
export async function getSnapshotManifest(o: RequestOptions = {}): Promise<SnapshotManifest> {
  const url = `${o.baseUrl ?? import.meta.env.BASE_URL}data/manifest.json`;
  return (await fetchJson(url, o)) as SnapshotManifest;
}
