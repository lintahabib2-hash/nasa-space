"""Export API outputs to frontend/public/data for offline static deploy

Owner: Member 6 (Backend, Integration, QA & Deployment)

Runs the SAME service functions the HTTP routes use, against a throw-away in-memory database
seeded only with the simulated X01 scenarios, and writes the answers as static JSON. The deployed
site (no Python server) then serves identical data from ./data/*.json, and the Service Worker
caches those files for offline use.

    python backend/scripts/export_static_snapshot.py          # (re)write the files
    python backend/scripts/export_static_snapshot.py --check  # exit 1 if committed files are stale

Output is deterministic (sorted keys, no wall-clock time) so --check is reliable in CI.
Also writes shared/mocks/*.json (one mock API response per scenario) for early integration.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.config import Settings  # noqa: E402
from backend.app.services import (  # noqa: E402
    baselines_for_subject, compute_baseline, environment_payload, open_repository, read_json,
)

# snapshot file -> the live API path it stands in for (used by frontend/src/services/apiClient.ts)
API_PATHS = {
    "environment.json": "/api/environment",
    "knowledge.json": "/api/knowledge",
    "sources.json": "/api/sources",
    "baselines.json": "/api/baseline/all?subject_id=<subject_id>",
}
MOCK_SCENARIOS = {"stable": "X01_stable", "drift": "X01_downward_drift", "missing": "X01_missing_observation"}


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def build_files(settings: Settings) -> Dict[Path, str]:
    repo = open_repository(Settings(db_path=":memory:", repo_root=settings.repo_root, seed_simulated=True))
    try:
        baselines = {s: baselines_for_subject(repo, s) for s in repo.subjects()}
        out: Dict[Path, str] = {
            settings.snapshot_dir / "environment.json": dumps(environment_payload()),
            settings.snapshot_dir / "knowledge.json": dumps(read_json(settings.knowledge_path)),
            settings.snapshot_dir / "sources.json": dumps(read_json(settings.sources_path)),
            settings.snapshot_dir / "baselines.json": dumps(baselines),
        }
        manifest = {
            "schema": "crew-vitals/snapshot@1",
            "generated_by": "backend/scripts/export_static_snapshot.py",
            "contains_real_astronaut_data": False,
            "files": {
                p.name: {"sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(), "bytes": len(t.encode("utf-8")),
                         "api_path": API_PATHS[p.name]}
                for p, t in out.items()
            },
        }
        out[settings.snapshot_dir / "manifest.json"] = dumps(manifest)
        for name, subject in MOCK_SCENARIOS.items():
            result = compute_baseline(repo, subject, "sleep_duration")
            out[settings.mocks_dir / f"baseline-{name}.json"] = dumps(result)
        return out
    finally:
        repo.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if files on disk differ from a fresh export")
    args = parser.parse_args(argv)
    files = build_files(Settings())
    stale = [p for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            print("Stale snapshot files (run: python backend/scripts/export_static_snapshot.py):")
            for p in stale:
                print(f"  {p.relative_to(ROOT)}")
            return 1
        print(f"Snapshot is up to date ({len(files)} files).")
        return 0
    for p, text in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
