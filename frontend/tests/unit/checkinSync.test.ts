import { describe, expect, it, vi } from "vitest";
import { OUTBOX_KEY, syncCheckin } from "../../src/services/checkinSync";

class MemoryStorage implements Storage {
  private m = new Map<string, string>();
  get length() { return this.m.size; }
  clear() { this.m.clear(); }
  getItem(k: string) { return this.m.has(k) ? this.m.get(k)! : null; }
  key(i: number) { return [...this.m.keys()][i] ?? null; }
  removeItem(k: string) { this.m.delete(k); }
  setItem(k: string, v: string) { this.m.set(k, String(v)); }
}

const record = (id: string) => ({ record_id: id, subject_id: "crew_01", indicators: {} });
const ok = () => vi.fn(async () => new Response("{}", { status: 201 }));

describe("check-in sync to the crew API (Member 6)", () => {
  it("does nothing when no API is configured", async () => {
    const storage = new MemoryStorage();
    const fetchImpl = ok();
    expect(await syncCheckin(record("a"), { apiBase: null, storage, fetchImpl })).toEqual({ kind: "local_only" });
    expect(fetchImpl).not.toHaveBeenCalled();
    expect(storage.getItem(OUTBOX_KEY)).toBeNull();
  });

  it("POSTs the Member 5 record to /api/checkins and leaves nothing queued", async () => {
    const storage = new MemoryStorage();
    const fetchImpl = ok();
    const result = await syncCheckin(record("a"), { apiBase: "http://api.test", storage, fetchImpl });
    expect(result).toEqual({ kind: "sent", sent: 1 });
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/checkins");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body)).record_id).toBe("a");
    expect(storage.getItem(OUTBOX_KEY)).toBeNull();
  });

  it("queues while the API is unreachable and sends the backlog once it is back", async () => {
    const storage = new MemoryStorage();
    const down = vi.fn(async () => { throw new TypeError("Failed to fetch"); });
    const first = await syncCheckin(record("a"), { apiBase: "http://api.test", storage, fetchImpl: down as unknown as typeof fetch });
    expect(first).toMatchObject({ kind: "queued", pending: 1 });
    await syncCheckin(record("b"), { apiBase: "http://api.test", storage, fetchImpl: down as unknown as typeof fetch });
    expect(JSON.parse(storage.getItem(OUTBOX_KEY)!)).toHaveLength(2);

    const up = ok();
    expect(await syncCheckin(null, { apiBase: "http://api.test", storage, fetchImpl: up })).toEqual({ kind: "sent", sent: 2 });
    expect(storage.getItem(OUTBOX_KEY)).toBeNull();
  });

  it("does not queue the same record twice, and drops records the API rejects as invalid", async () => {
    const storage = new MemoryStorage();
    const down = vi.fn(async () => new Response("", { status: 503 }));
    await syncCheckin(record("a"), { apiBase: "http://api.test", storage, fetchImpl: down });
    await syncCheckin(record("a"), { apiBase: "http://api.test", storage, fetchImpl: down });
    expect(JSON.parse(storage.getItem(OUTBOX_KEY)!)).toHaveLength(1);

    const rejects = vi.fn(async () => new Response("", { status: 422 }));
    expect(await syncCheckin(null, { apiBase: "http://api.test", storage, fetchImpl: rejects })).toEqual({ kind: "sent", sent: 0 });
    expect(storage.getItem(OUTBOX_KEY)).toBeNull();
  });
});
