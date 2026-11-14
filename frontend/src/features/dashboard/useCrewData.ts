import { useEffect, useState } from "react";
import { FIXTURE_BUNDLES, loadApiBundle } from "./dataSource";
import type { CrewBundle, DataMode } from "./types";

export type LoadState =
  | { kind: "loading" }
  | { kind: "ready"; bundles: CrewBundle[] }
  | { kind: "error"; message: string };

export function useCrewData(mode: DataMode, subjectId: string): LoadState {
  const [state, setState] = useState<LoadState>(
    mode === "fixtures" ? { kind: "ready", bundles: FIXTURE_BUNDLES } : { kind: "loading" },
  );

  useEffect(() => {
    if (mode === "fixtures") {
      setState({ kind: "ready", bundles: FIXTURE_BUNDLES });
      return;
    }
    const ctrl = new AbortController();
    setState({ kind: "loading" });
    loadApiBundle(subjectId, ctrl.signal)
      .then((b) => setState({ kind: "ready", bundles: [b] }))
      .catch((err: unknown) => {
        if (ctrl.signal.aborted) return;
        setState({ kind: "error", message: err instanceof Error ? err.message : String(err) });
      });
    return () => ctrl.abort();
  }, [mode, subjectId]);

  return state;
}
