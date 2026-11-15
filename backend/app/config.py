"""Settings (paths, CORS, environment).

Owner: Member 6 (Backend, Integration, QA & Deployment)

Everything is overridable with environment variables so CI, tests and the demo laptop can
point at their own database without code changes:

    CREW_VITALS_DB      SQLite file (default backend/.runtime/crew_vitals.sqlite3; ":memory:" allowed)
    CREW_VITALS_CORS    comma-separated allowed origins (default: local Vite dev + preview)
    CREW_VITALS_SEED    "1" (default) loads the X01 simulated scenarios on first start
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ORIGINS = (
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:4173", "http://127.0.0.1:4173",
)


@dataclass(frozen=True)
class Settings:
    repo_root: Path = REPO_ROOT
    db_path: str = field(default_factory=lambda: os.environ.get(
        "CREW_VITALS_DB", str(REPO_ROOT / "backend" / ".runtime" / "crew_vitals.sqlite3")))
    cors_origins: Tuple[str, ...] = field(default_factory=lambda: tuple(
        o.strip() for o in os.environ.get("CREW_VITALS_CORS", ",".join(DEFAULT_ORIGINS)).split(",") if o.strip()))
    seed_simulated: bool = field(default_factory=lambda: os.environ.get("CREW_VITALS_SEED", "1") != "0")

    @property
    def x01_path(self) -> Path:
        return self.repo_root / "data" / "simulated" / "X01_crew_scenarios.json"

    @property
    def knowledge_path(self) -> Path:
        return self.repo_root / "shared" / "knowledge" / "knowledge.json"

    @property
    def sources_path(self) -> Path:
        return self.repo_root / "shared" / "knowledge" / "source-registry.json"

    @property
    def schemas_dir(self) -> Path:
        return self.repo_root / "shared" / "schemas"

    @property
    def snapshot_dir(self) -> Path:
        return self.repo_root / "frontend" / "public" / "data"

    @property
    def mocks_dir(self) -> Path:
        return self.repo_root / "shared" / "mocks"
