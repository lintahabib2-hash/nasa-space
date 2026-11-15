"""Application services shared by the HTTP routes and the static-snapshot exporter.

Owner: Member 6 (Backend, Integration, QA & Deployment)

Keeping the logic here (not in the route functions) is what guarantees the offline static
snapshot is byte-for-byte what the live API would have answered.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .analytics import get_baseline_result
from .config import Settings
from .environment.series import get_environment_series
from .storage import Repository

SERIES_KEYS = ("study_id", "source_id", "provenance_kind", "units")


def _series_key(rec: Dict[str, Any]) -> tuple:
    return tuple(rec[k] for k in SERIES_KEYS)


def no_observations(subject_id: str, measurement: str) -> Dict[str, Any]:
    return {
        "subject_id": subject_id, "measurement": measurement, "status": "no_observations",
        "quality_state": "missing", "reasons": ["No readings stored for this indicator"],
        "severity_basis": "unvalidated_demo_statistical_rule", "not_medical_diagnosis": True,
        "current_value": None, "baseline_value": None, "robust_z": None,
        "history_count": 0, "rejected_history_count": 0,
    }


def compute_baseline(repo: Repository, subject_id: str, measurement: str,
                     study_id: Optional[str] = None) -> Dict[str, Any]:
    """Score the latest reading of one series against that series' own prior readings.

    If a subject has several series for a measurement (different study/source/provenance),
    the series holding the most recent reading is scored. Only same-series readings are
    passed on, so sources can never be mixed (README ground rule 2).
    """
    rows = repo.list_observations(subject_id=subject_id, measurement=measurement, study_id=study_id)
    if not rows:
        return no_observations(subject_id, measurement)
    current = max(rows, key=lambda r: r["timestamp_utc"])
    key = _series_key(current)
    history = [r for r in rows if _series_key(r) == key and r is not current]
    return get_baseline_result(history, current)


def baselines_for_subject(repo: Repository, subject_id: str) -> List[Dict[str, Any]]:
    return [compute_baseline(repo, subject_id, m) for m in repo.measurements(subject_id)]


def environment_payload() -> Dict[str, Any]:
    """Member 4's validated environment series. Never carries a subject_id."""
    return get_environment_series()


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def open_repository(settings: Settings) -> Repository:
    repo = Repository(settings.db_path, settings.schemas_dir / "checkin.schema.json")
    if settings.seed_simulated:
        repo.seed_simulated(settings.x01_path)
    return repo
