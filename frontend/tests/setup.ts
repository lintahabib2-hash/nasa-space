import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// jsdom has no ResizeObserver; Recharts' ResponsiveContainer needs one.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
(globalThis as unknown as { ResizeObserver: typeof ResizeObserverStub }).ResizeObserver ??= ResizeObserverStub;

afterEach(() => cleanup());

// Newer Node versions (24+/25) ship their own global `localStorage`. Without --localstorage-file it
// is broken and shadows jsdom's working one ("localStorage.clear is not a function"). If the global
// is unusable, install a simple in-memory Storage so the tests behave the same on every Node version.
function storageWorks(): boolean {
  try {
    return typeof globalThis.localStorage?.clear === "function";
  } catch {
    return false;
  }
}
if (!storageWorks()) {
  const data = new Map<string, string>();
  const memoryStorage = {
    get length() { return data.size; },
    clear: () => data.clear(),
    getItem: (k: string) => (data.has(k) ? (data.get(k) as string) : null),
    key: (i: number) => [...data.keys()][i] ?? null,
    removeItem: (k: string) => { data.delete(k); },
    setItem: (k: string, v: string) => { data.set(k, String(v)); },
  } as Storage;
  for (const target of [globalThis, (globalThis as { window?: object }).window]) {
    if (target) Object.defineProperty(target, "localStorage", { value: memoryStorage, configurable: true, writable: true });
  }
}
