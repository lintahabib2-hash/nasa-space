import { useEffect, useState, useSyncExternalStore } from "react";
import { getSnapshotManifest } from "../services/apiClient";
import { useOfflineState } from "./register";
import "./offline-badge.css";

const onlineStore = {
  subscribe(cb: () => void) {
    window.addEventListener("online", cb);
    window.addEventListener("offline", cb);
    return () => { window.removeEventListener("online", cb); window.removeEventListener("offline", cb); };
  },
  get: () => navigator.onLine,
};

/** Shows whether the app can be used with no connection, and whether it is offline right now. */
export function OfflineBadge() {
  const sw = useOfflineState();
  const online = useSyncExternalStore(onlineStore.subscribe, onlineStore.get, () => true);
  const [files, setFiles] = useState<number | null>(null);

  useEffect(() => {
    const ctrl = new AbortController();
    getSnapshotManifest({ signal: ctrl.signal }).then((m) => setFiles(Object.keys(m.files).length)).catch(() => setFiles(null));
    return () => ctrl.abort();
  }, []);

  const ready = sw === "ready";
  const label = !online
    ? (ready ? "Offline: using saved data" : "Offline")
    : ready ? "Offline ready" : sw === "registering" ? "Preparing offline mode…" : sw === "dev" ? "Dev mode (no offline cache)" : "Offline mode unavailable";
  const tone = ready ? "ok" : sw === "registering" || sw === "dev" ? "pending" : "warn";

  return (
    <span
      className={`offline-badge offline-badge--${tone}`}
      role="status"
      data-testid="offline-badge"
      data-sw-state={sw}
      data-online={online ? "true" : "false"}
      title={files ? `${files} data files are saved on this device for offline use.` : undefined}
    >
      <span aria-hidden="true" className="offline-badge__dot" />
      {label}
    </span>
  );
}
