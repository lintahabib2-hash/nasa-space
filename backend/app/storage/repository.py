"""Read/write observations and check-ins.

Owner: Member 6 (Backend, Integration, QA & Deployment)

Local SQLite persistence (standard library only, no server to run, works offline). Rules:

* Everything written is validated first. An observation must pass `contracts.Observation`;
  a check-in must pass shared/schemas/checkin.schema.json (the contract Member 5 owns).
* Writes are idempotent. The same series + timestamp overwrites instead of duplicating, so
  retrying a request can never create the duplicate-timestamp groups that Member 2's analytics
  (rightly) refuses to score.
* A check-in and the observations derived from it are written in ONE transaction.
* Nothing here computes a status. Analytics stays in backend/app/analytics.
"""

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from jsonschema import Draft202012Validator

from ..contracts import Observation

SCHEMA_VERSION = 1

_DDL = """
CREATE TABLE IF NOT EXISTS observations (
    subject_id TEXT NOT NULL, study_id TEXT NOT NULL, source_id TEXT NOT NULL,
    provenance_kind TEXT NOT NULL, measurement TEXT NOT NULL, units TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL, value REAL, quality_state TEXT NOT NULL, reference_url TEXT,
    PRIMARY KEY (subject_id, study_id, source_id, provenance_kind, measurement, units, timestamp_utc)
);
CREATE INDEX IF NOT EXISTS ix_obs_subject_measure ON observations (subject_id, measurement, timestamp_utc);
CREATE TABLE IF NOT EXISTS checkins (
    record_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, timestamp_utc TEXT NOT NULL, payload TEXT NOT NULL
);
"""

_OBS_COLUMNS = ("subject_id", "study_id", "source_id", "provenance_kind", "measurement",
                "units", "timestamp_utc", "value", "quality_state", "reference_url")


class RepositoryError(ValueError):
    """Raised for data the repository refuses to store."""


class Repository:
    def __init__(self, db_path: str, checkin_schema_path: Optional[Path] = None):
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        with self._lock:
            self._db.executescript(_DDL)
            found = self._db.execute("PRAGMA user_version").fetchone()[0]
            if found > SCHEMA_VERSION:
                raise RepositoryError(f"Database is from a newer app version ({found} > {SCHEMA_VERSION}).")
            self._db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._db.commit()
        self._checkin_validator = None
        if checkin_schema_path is not None:
            schema = json.loads(Path(checkin_schema_path).read_text(encoding="utf-8"))
            self._checkin_validator = Draft202012Validator(schema)

    # ---- observations -------------------------------------------------------------------

    def _upsert_observation(self, rec: Dict[str, Any]) -> None:
        self._db.execute(
            f"INSERT INTO observations ({','.join(_OBS_COLUMNS)}) VALUES ({','.join('?' * len(_OBS_COLUMNS))}) "
            "ON CONFLICT(subject_id, study_id, source_id, provenance_kind, measurement, units, timestamp_utc) "
            "DO UPDATE SET value=excluded.value, quality_state=excluded.quality_state, reference_url=excluded.reference_url",
            tuple(rec[c] for c in _OBS_COLUMNS),
        )

    def add_observations(self, observations: Iterable[Any]) -> int:
        """Validate every observation first, then write all of them atomically."""
        records: List[Dict[str, Any]] = []
        for i, obs in enumerate(observations):
            try:
                model = obs if isinstance(obs, Observation) else Observation.model_validate(obs)
            except Exception as exc:  # pydantic.ValidationError -> one clear message
                raise RepositoryError(f"observation[{i}] is invalid: {exc}") from exc
            records.append(model.to_record())
        with self._lock:
            try:
                for rec in records:
                    self._upsert_observation(rec)
                self._db.commit()
            except Exception:
                self._db.rollback()
                raise
        return len(records)

    def list_observations(self, subject_id: Optional[str] = None, measurement: Optional[str] = None,
                          study_id: Optional[str] = None, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses, args = [], []
        for col, val in (("subject_id", subject_id), ("measurement", measurement),
                         ("study_id", study_id), ("source_id", source_id)):
            if val is not None:
                clauses.append(f"{col} = ?")
                args.append(val)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock:
            rows = self._db.execute(
                f"SELECT {','.join(_OBS_COLUMNS)} FROM observations {where} ORDER BY timestamp_utc, measurement", args
            ).fetchall()
        return [dict(r) for r in rows]

    def subjects(self) -> List[str]:
        with self._lock:
            return [r[0] for r in self._db.execute("SELECT DISTINCT subject_id FROM observations ORDER BY 1")]

    def measurements(self, subject_id: str) -> List[str]:
        with self._lock:
            return [r[0] for r in self._db.execute(
                "SELECT DISTINCT measurement FROM observations WHERE subject_id = ? ORDER BY 1", (subject_id,))]

    # ---- check-ins ----------------------------------------------------------------------

    def validate_checkin(self, record: Any) -> None:
        if self._checkin_validator is None:
            raise RepositoryError("No check-in schema configured")
        errors = sorted(self._checkin_validator.iter_errors(record), key=lambda e: list(e.path))
        if errors:
            first = errors[0]
            where = ".".join(str(p) for p in first.path) or "(root)"
            raise RepositoryError(f"check-in invalid at {where}: {first.message}")

    def add_checkin(self, record: Dict[str, Any]) -> int:
        """Store a validated check-in and the observations derived from it. Returns #observations."""
        self.validate_checkin(record)
        derived = []
        for key, env in record["indicators"].items():
            if env["measurement"] != key or env["subject_id"] != record["subject_id"]:
                raise RepositoryError(f"indicator {key} does not match its envelope or the record subject")
            derived.append(Observation.model_validate({**env, "quality_state": "valid"}))
        with self._lock:
            try:
                self._db.execute(
                    "INSERT INTO checkins (record_id, subject_id, timestamp_utc, payload) VALUES (?,?,?,?) "
                    "ON CONFLICT(record_id) DO UPDATE SET payload=excluded.payload",
                    (record["record_id"], record["subject_id"], record["timestamp_utc"], json.dumps(record, sort_keys=True)),
                )
                for obs in derived:
                    self._upsert_observation(obs.to_record())
                self._db.commit()
            except Exception:
                self._db.rollback()
                raise
        return len(derived)

    def list_checkins(self, subject_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql, args = "SELECT payload FROM checkins", []
        if subject_id is not None:
            sql += " WHERE subject_id = ?"
            args.append(subject_id)
        with self._lock:
            rows = self._db.execute(sql + " ORDER BY timestamp_utc", args).fetchall()
        return [json.loads(r[0]) for r in rows]

    # ---- seeding / housekeeping ---------------------------------------------------------

    def seed_simulated(self, x01_path: Path) -> int:
        """Load the X01 engineering scenarios (simulated, never real astronaut data)."""
        data = json.loads(Path(x01_path).read_text(encoding="utf-8"))
        if data.get("provenance_kind") != "simulated" or data.get("not_real_astronaut_data") is not True:
            raise RepositoryError("Refusing to seed: X01 file is not labelled simulated / not real astronaut data")
        batch: List[Dict[str, Any]] = []
        for scenario in data["scenarios"]:
            batch.extend(scenario["history"])
            batch.append(scenario["current"])
        return self.add_observations(batch)

    def counts(self) -> Dict[str, int]:
        with self._lock:
            return {
                "observations": self._db.execute("SELECT COUNT(*) FROM observations").fetchone()[0],
                "checkins": self._db.execute("SELECT COUNT(*) FROM checkins").fetchone()[0],
            }

    def clear(self) -> None:
        with self._lock:
            self._db.execute("DELETE FROM observations")
            self._db.execute("DELETE FROM checkins")
            self._db.commit()

    def close(self) -> None:
        with self._lock:
            self._db.close()
