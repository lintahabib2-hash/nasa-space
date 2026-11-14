// Local persistence for check-ins and reaction results (Member 5). Data stays in this browser.
// Member 6 can swap this for IndexedDB or the shared storage service without changing callers.
import type { CheckinRecord } from "./checkinSchema";
import type { ReactionRecord } from "../reaction-time/reactionLogic";

export const STORAGE_KEY = "crew-vitals.checkins.v1";

export interface LocalRecords {
  checkins: CheckinRecord[];
  reactionTests: ReactionRecord[];
}

const EMPTY: LocalRecords = { checkins: [], reactionTests: [] };

export function readRecords(storage: Storage = localStorage): LocalRecords {
  let raw: string | null;
  try {
    raw = storage.getItem(STORAGE_KEY);
  } catch (e) {
    throw new Error(`Could not read saved data: ${(e as Error).message}`);
  }
  if (!raw) return { checkins: [], reactionTests: [] };
  try {
    const parsed = JSON.parse(raw) as LocalRecords;
    if (!parsed || !Array.isArray(parsed.checkins) || !Array.isArray(parsed.reactionTests)) {
      throw new Error("Stored data does not match the NASA Space Health Monitoring Agent format.");
    }
    return parsed;
  } catch (e) {
    throw new Error(`Could not read saved data: ${(e as Error).message}`);
  }
}

export function saveRecords(records: LocalRecords, storage: Storage = localStorage): void {
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(records));
  } catch (e) {
    throw new Error(`Could not save data in this browser: ${(e as Error).message}`);
  }
}

export function appendCheckin(record: CheckinRecord, storage: Storage = localStorage): LocalRecords {
  const current = readRecords(storage);
  const next = { ...current, checkins: [...current.checkins, record] };
  saveRecords(next, storage);
  return next;
}

export function appendReaction(record: ReactionRecord, storage: Storage = localStorage): LocalRecords {
  const current = readRecords(storage);
  const next = { ...current, reactionTests: [...current.reactionTests, record] };
  saveRecords(next, storage);
  return next;
}

export function emptyRecords(): LocalRecords {
  return { ...EMPTY, checkins: [], reactionTests: [] };
}
