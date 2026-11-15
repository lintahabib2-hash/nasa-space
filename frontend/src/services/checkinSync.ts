// Check-in sync to the crew API (Member 6).
// Check-ins are always saved on this device first (Member 5's checkinStore). When an API is configured
// (VITE_API_BASE), each record is also POSTed to /api/checkins. Records that cannot be sent (offline,
// API down) wait in a small outbox and are retried when the browser comes back online. The backend
// upserts by record_id, so a retry never creates a duplicate. With no API configured this is a no-op.
import { configuredApiBase } from "./apiClient";

export const OUTBOX_KEY = "crew-vitals.outbox.v1";

export type SyncResult =
  | { kind: "local_only" }                    // no API configured: nothing to send
  | { kind: "sent"; sent: number }            // everything in the outbox reached the API
  | { kind: "queued"; pending: number; reason: string }; // kept for a later retry

export interface SyncOptions {
  apiBase?: string | null;
  fetchImpl?: typeof fetch;
  storage?: Storage;
  timeoutMs?: number;
}

type OutboxRecord = { record_id: string } & Record<string, unknown>;

function readOutbox(storage: Storage): OutboxRecord[] {
  try {
    const parsed = JSON.parse(storage.getItem(OUTBOX_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter((r) => r && typeof r.record_id === "string") : [];
  } catch {
    return [];
  }
}

function writeOutbox(storage: Storage, records: OutboxRecord[]): void {
  try {
    if (records.length) storage.setItem(OUTBOX_KEY, JSON.stringify(records));
    else storage.removeItem(OUTBOX_KEY);
  } catch {
    /* storage full or blocked: the record is still in the main check-in store */
  }
}

async function post(base: string, record: OutboxRecord, o: SyncOptions): Promise<void> {
  const doFetch = o.fetchImpl ?? fetch;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), o.timeoutMs ?? 5000);
  try {
    const res = await doFetch(`${base}/api/checkins`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(record),
      signal: ctrl.signal,
    });
    if (res.status === 422 || res.status === 400) {
      // The API rejected the record itself; retrying will not help. Drop it from the outbox
      // (it remains in the local check-in history) rather than retrying forever.
      throw Object.assign(new Error(`rejected by API (HTTP ${res.status})`), { permanent: true });
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } finally {
    clearTimeout(timer);
  }
}

/** Queue a new check-in (if an API is configured) and try to send everything waiting. */
export async function syncCheckin(record: OutboxRecord | null, o: SyncOptions = {}): Promise<SyncResult> {
  const base = o.apiBase === undefined ? configuredApiBase() : o.apiBase;
  if (!base) return { kind: "local_only" };
  const storage = o.storage ?? localStorage;
  const outbox = readOutbox(storage).filter((r) => !record || r.record_id !== record.record_id);
  if (record) outbox.push(record);
  writeOutbox(storage, outbox);

  const remaining: OutboxRecord[] = [];
  let sent = 0;
  let reason = "";
  for (const r of outbox) {
    try {
      await post(base, r, o);
      sent += 1;
    } catch (e) {
      if ((e as { permanent?: boolean }).permanent) {
        reason = (e as Error).message;
        continue;
      }
      reason = (e as Error).message || "API unreachable";
      remaining.push(r);
    }
  }
  writeOutbox(storage, remaining);
  return remaining.length ? { kind: "queued", pending: remaining.length, reason } : { kind: "sent", sent };
}

/** Retry the outbox whenever the browser reports it is back online. Returns a stop function. */
export function startOutboxRetry(o: SyncOptions = {}): () => void {
  if (typeof window === "undefined") return () => {};
  const retry = () => void syncCheckin(null, o);
  window.addEventListener("online", retry);
  retry();
  return () => window.removeEventListener("online", retry);
}
