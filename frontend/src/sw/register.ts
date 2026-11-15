// Registers the service worker and exposes its state to the UI.
// Owner: Member 6 (Backend, Integration, QA & Deployment)
import { useSyncExternalStore } from "react";

export type OfflineState = "registering" | "ready" | "unsupported" | "failed" | "dev";

let state: OfflineState = "registering";
const listeners = new Set<() => void>();
const set = (s: OfflineState) => { state = s; listeners.forEach((l) => l()); };

export const getOfflineState = () => state;
export const subscribeOfflineState = (l: () => void) => { listeners.add(l); return () => { listeners.delete(l); }; };

/** Register ./sw.js (relative, so it works from a sub-path such as GitHub Pages). Never throws. */
export async function registerServiceWorker(): Promise<OfflineState> {
  if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) { set("unsupported"); return state; }
  if (!import.meta.env.PROD) { set("dev"); return state; } // the dev server has no sw.js
  try {
    await navigator.serviceWorker.register(new URL("sw.js", document.baseURI).href);
    await navigator.serviceWorker.ready; // an active worker exists, so the install-time precache finished
    set("ready");
  } catch (err) {
    console.warn("Service worker registration failed:", err);
    set("failed");
  }
  return state;
}

export const useOfflineState = () => useSyncExternalStore(subscribeOfflineState, getOfflineState, getOfflineState);

/** Test helper. */
export const __resetOfflineStateForTests = () => set("registering");
