// localStorage / IndexedDB persistence
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// Member 5's check-in store keeps records in localStorage through a small synchronous API that
// the form and history depend on. We do not change that API. This module adds durability:
//
//   1. asks the browser to mark storage persistent (so it is not evicted under disk pressure),
//   2. mirrors the records into IndexedDB (a second, independent store), and
//   3. restores them from the mirror if localStorage was cleared or evicted but IndexedDB was not.
//
// Everything stays on the device. Nothing here touches the network.
import { STORAGE_KEY } from "../features/checkin/checkinStore";

const DB_NAME = "crew-vitals-mirror";
const STORE = "kv";

function openDb(idb: IDBFactory): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = idb.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function idbRequest<T>(idb: IDBFactory, mode: IDBTransactionMode, run: (s: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  const db = await openDb(idb);
  try {
    return await new Promise<T>((resolve, reject) => {
      const tx = db.transaction(STORE, mode);
      const req = run(tx.objectStore(STORE));
      tx.oncomplete = () => resolve(req.result);
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  } finally {
    db.close();
  }
}

export type RestoreResult = "present" | "restored" | "nothing";

/** Copy the current check-in records into IndexedDB. Returns false when there is nothing to copy. */
export async function mirrorNow(storage: Storage = localStorage, idb: IDBFactory = indexedDB): Promise<boolean> {
  const raw = storage.getItem(STORAGE_KEY);
  if (raw === null) return false;
  await idbRequest(idb, "readwrite", (s) => s.put(raw, STORAGE_KEY));
  return true;
}

/** If localStorage lost the records but the IndexedDB mirror still has them, put them back. */
export async function restoreIfMissing(storage: Storage = localStorage, idb: IDBFactory = indexedDB): Promise<RestoreResult> {
  if (storage.getItem(STORAGE_KEY) !== null) return "present";
  const mirrored = await idbRequest<string | undefined>(idb, "readonly", (s) => s.get(STORAGE_KEY));
  if (typeof mirrored !== "string") return "nothing";
  try {
    const parsed = JSON.parse(mirrored);
    if (!parsed || !Array.isArray(parsed.checkins) || !Array.isArray(parsed.reactionTests)) return "nothing";
  } catch {
    return "nothing"; // a corrupt mirror must never overwrite anything
  }
  storage.setItem(STORAGE_KEY, mirrored);
  return "restored";
}

/**
 * Run before the app renders: the check-in page reads localStorage once on mount, so a restore that
 * finishes later would not show up until the next navigation. Never throws and never waits longer
 * than `timeoutMs`, so a broken or slow IndexedDB cannot stop the app from starting.
 */
export async function restoreBeforeRender(
  storage: Storage = localStorage,
  idb: IDBFactory | undefined = typeof indexedDB === "undefined" ? undefined : indexedDB,
  timeoutMs = 1500,
): Promise<RestoreResult> {
  if (!idb) return "nothing";
  const guard = new Promise<RestoreResult>((resolve) => setTimeout(() => resolve("nothing"), timeoutMs));
  try {
    return await Promise.race([restoreIfMissing(storage, idb), guard]);
  } catch {
    return "nothing"; // storage blocked or IndexedDB unavailable
  }
}

/** Ask the browser not to evict this origin's storage. null = not supported. */
export async function requestPersistence(nav: Navigator = navigator): Promise<boolean | null> {
  if (!nav.storage?.persist) return null;
  try {
    return (await nav.storage.persist()) || (await nav.storage.persisted?.()) || false;
  } catch {
    return null;
  }
}

/**
 * Start mirroring for the app's lifetime (call after restoreBeforeRender). Safe to call anywhere: if IndexedDB or localStorage is
 * unavailable (private mode, blocked storage) it quietly does nothing, and the app keeps working.
 * Returns a cleanup function.
 */
export function startDurability(storage: Storage = localStorage, idb: IDBFactory | undefined = typeof indexedDB === "undefined" ? undefined : indexedDB): () => void {
  if (!idb) return () => {};
  let lastRaw: string | null = null;
  let stopped = false;

  const sync = () => {
    if (stopped) return;
    try {
      const raw = storage.getItem(STORAGE_KEY);
      if (raw === lastRaw) return;
      lastRaw = raw;
      void mirrorNow(storage, idb).catch(() => { lastRaw = null; });
    } catch { /* storage blocked: nothing to mirror */ }
  };
  const onHide = () => { if (document.visibilityState === "hidden") sync(); };

  void requestPersistence();
  sync();

  const timer = window.setInterval(sync, 5000);
  window.addEventListener("pagehide", sync);
  document.addEventListener("visibilitychange", onHide);
  return () => {
    stopped = true;
    window.clearInterval(timer);
    window.removeEventListener("pagehide", sync);
    document.removeEventListener("visibilitychange", onHide);
  };
}
