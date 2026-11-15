// Durability layer: IndexedDB mirror + restore for check-in records.
import { IDBFactory } from "fake-indexeddb";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { STORAGE_KEY } from "../../src/features/checkin/checkinStore";
import { mirrorNow, requestPersistence, restoreBeforeRender, restoreIfMissing, startDurability } from "../../src/services/storage";

const RECORDS = JSON.stringify({ checkins: [{ record_id: "c1" }], reactionTests: [] });

let idb: IDBFactory;
beforeEach(() => { idb = new IDBFactory(); localStorage.clear(); });
afterEach(() => vi.useRealTimers());

describe("mirrorNow / restoreIfMissing", () => {
  it("does nothing when there are no records yet", async () => {
    expect(await mirrorNow(localStorage, idb)).toBe(false);
    expect(await restoreIfMissing(localStorage, idb)).toBe("nothing");
  });

  it("mirrors records, then restores them after localStorage is wiped", async () => {
    localStorage.setItem(STORAGE_KEY, RECORDS);
    expect(await mirrorNow(localStorage, idb)).toBe(true);
    localStorage.clear(); // eviction / user cleared site data but IndexedDB survived
    expect(await restoreIfMissing(localStorage, idb)).toBe("restored");
    expect(localStorage.getItem(STORAGE_KEY)).toBe(RECORDS);
  });

  it("never overwrites records that are already in localStorage", async () => {
    localStorage.setItem(STORAGE_KEY, RECORDS);
    await mirrorNow(localStorage, idb);
    const newer = JSON.stringify({ checkins: [{ record_id: "c1" }, { record_id: "c2" }], reactionTests: [] });
    localStorage.setItem(STORAGE_KEY, newer);
    expect(await restoreIfMissing(localStorage, idb)).toBe("present");
    expect(localStorage.getItem(STORAGE_KEY)).toBe(newer);
  });

  it("ignores a corrupt or wrongly shaped mirror", async () => {
    for (const bad of ["{not json", JSON.stringify({ checkins: "x" }), JSON.stringify([1, 2])]) {
      localStorage.setItem(STORAGE_KEY, bad);
      await mirrorNow(localStorage, idb);
      localStorage.clear();
      expect(await restoreIfMissing(localStorage, idb)).toBe("nothing");
      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    }
  });
});

describe("requestPersistence", () => {
  it("returns null where the Storage API is missing", async () => {
    expect(await requestPersistence({} as Navigator)).toBeNull();
  });
  it("reports whether persistence was granted", async () => {
    expect(await requestPersistence({ storage: { persist: async () => true } } as unknown as Navigator)).toBe(true);
    expect(await requestPersistence({ storage: { persist: async () => false, persisted: async () => false } } as unknown as Navigator)).toBe(false);
  });
  it("never throws", async () => {
    expect(await requestPersistence({ storage: { persist: async () => { throw new Error("denied"); } } } as unknown as Navigator)).toBeNull();
  });
});

describe("startDurability", () => {
  it("is a harmless no-op without IndexedDB", () => {
    const stop = startDurability(localStorage, undefined);
    expect(typeof stop).toBe("function");
    stop();
  });

  it("mirrors changes on pagehide so a later wipe can be recovered", async () => {
    const stop = startDurability(localStorage, idb);
    const next = JSON.stringify({ checkins: [{ record_id: "c9" }], reactionTests: [] });
    localStorage.setItem(STORAGE_KEY, next);
    window.dispatchEvent(new Event("pagehide"));
    await vi.waitFor(async () => {
      localStorage.clear();
      expect(await restoreIfMissing(localStorage, idb)).toBe("restored");
      expect(localStorage.getItem(STORAGE_KEY)).toBe(next);
    });
    stop();
  });

  it("stops mirroring after cleanup", async () => {
    const stop = startDurability(localStorage, idb);
    stop();
    localStorage.setItem(STORAGE_KEY, RECORDS);
    window.dispatchEvent(new Event("pagehide"));
    await new Promise((r) => setTimeout(r, 50));
    localStorage.clear();
    expect(await restoreIfMissing(localStorage, idb)).toBe("nothing");
  });
});

describe("restoreBeforeRender", () => {
  it("restores records so the first render already has them", async () => {
    localStorage.setItem(STORAGE_KEY, RECORDS);
    await mirrorNow(localStorage, idb);
    localStorage.clear();
    expect(await restoreBeforeRender(localStorage, idb)).toBe("restored");
    expect(localStorage.getItem(STORAGE_KEY)).toBe(RECORDS);
  });

  it("returns 'nothing' without IndexedDB, on errors, and never waits past the timeout", async () => {
    expect(await restoreBeforeRender(localStorage, undefined)).toBe("nothing");
    const broken = { open: () => { throw new Error("blocked"); } } as unknown as IDBFactory;
    expect(await restoreBeforeRender(localStorage, broken)).toBe("nothing");
    const hanging = { open: () => ({}) } as unknown as IDBFactory; // request that never fires
    const t0 = Date.now();
    expect(await restoreBeforeRender(localStorage, hanging, 60)).toBe("nothing");
    expect(Date.now() - t0).toBeLessThan(1000);
  });
});
