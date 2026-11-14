"""Crew Vitals Member 2 offline localhost demo and analytics API.

No cloud, network fetching, synthetic observations, or externally hosted assets.
Research files must already exist locally. Bind to 127.0.0.1 only.
This local prototype is not a medical device or a production authentication layer.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from urllib.parse import parse_qs, urlsplit

try:
    from .analytics import get_baseline_result, validated
    from .eda_adapter import load_eda_preview
    from .offline_research import cft70_view, inspiration_view, radlab_view
except ImportError:
    from analytics import get_baseline_result, validated
    from eda_adapter import load_eda_preview
    from offline_research import cft70_view, inspiration_view, radlab_view

ALLOWED_FIELDS = (
    "subject_id", "study_id", "source_id", "provenance_kind",
    "measurement", "value", "units", "timestamp_utc",
)
MAX_BODY = 8192


def normalize_checkin(payload: object) -> dict:
    """A narrow, explicit demo contract: locally entered sleep duration only."""
    if not isinstance(payload, dict) or set(payload) != set(ALLOWED_FIELDS):
        raise ValueError(f"Expected exactly these fields: {', '.join(ALLOWED_FIELDS)}")
    for key in ("subject_id", "study_id", "source_id"):
        val = payload[key]
        if not isinstance(val, str) or not 1 <= len(val) <= 80 or not all(c.isalnum() or c in "_-" for c in val):
            raise ValueError(f"Invalid {key}")
    if payload["provenance_kind"] != "crew_self_report":
        raise ValueError("Only crew_self_report observations can be entered locally")
    if payload["measurement"] != "sleep_duration" or payload["units"] != "hours":
        raise ValueError("This version accepts sleep_duration measured in hours only")
    when, value = validated(payload)
    if when > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError("Future-dated check-ins are not accepted")
    return {**payload, "value": value, "timestamp_utc": when.isoformat().replace("+00:00", "Z")}


class OfflineStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id TEXT NOT NULL, study_id TEXT NOT NULL,
                source_id TEXT NOT NULL, provenance_kind TEXT NOT NULL,
                measurement TEXT NOT NULL, value REAL NOT NULL,
                units TEXT NOT NULL, timestamp_utc TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                UNIQUE(subject_id,study_id,source_id,provenance_kind,measurement,units,timestamp_utc)
            )""")

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(str(self.path), timeout=10)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def put(self, payload: object) -> dict:
        record = normalize_checkin(payload)
        now = datetime.now(timezone.utc).isoformat()
        with self.lock, self._connect() as db:
            try:
                cur = db.execute("""INSERT INTO checkins
                    (subject_id, study_id, source_id, provenance_kind, measurement,
                     value, units, timestamp_utc, created_at_utc)
                    VALUES (:subject_id, :study_id, :source_id, :provenance_kind, :measurement,
                            :value, :units, :timestamp_utc, :created_at_utc)""",
                    {**record, "created_at_utc": now})
            except sqlite3.IntegrityError as exc:
                raise ValueError("Duplicate observation for this series and timestamp") from exc
            return {"id": cur.lastrowid, **record, "created_at_utc": now}

    def list_subject(self, subject_id: str, limit: int = 2000) -> list[dict]:
        if not isinstance(subject_id, str) or not 1 <= len(subject_id) <= 80:
            raise ValueError("subject_id required")
        with self.lock, self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM checkins WHERE subject_id=? ORDER BY timestamp_utc DESC, id DESC LIMIT ?",
                (subject_id, limit),
            )][::-1]

    def latest_analysis(self, subject_id: str) -> dict:
        series = self.list_subject(subject_id)
        if not series:
            return {"status": "no_observations", "reasons": ["No check-ins stored for this subject"], "not_medical_diagnosis": True}
        current = series[-1]
        compatible = [row for row in series[:-1] if all(
            row[key] == current[key] for key in (
                "subject_id", "study_id", "source_id", "provenance_kind", "measurement", "units"
            )
        )]
        result = get_baseline_result(compatible, current)
        result["time_precision"] = "timestamp_utc"
        result["analysis_context"] = "locally entered check-ins; demo statistical rule only"
        result["timestamp_utc"] = current["timestamp_utc"]
        return result


def create_server(*, db_path: str | Path, bedrest_json: str | Path | None = None,
                  eda_csv: str | Path | None = None, cft70_json: str | Path | None = None,
                  cmp_json: str | Path | None = None, cbc_json: str | Path | None = None,
                  radlab_csv: str | Path | None = None, port: int = 8766) -> ThreadingHTTPServer:
    store = OfflineStore(db_path)
    bedrest_path = Path(bedrest_json) if bedrest_json else None
    eda_path = Path(eda_csv) if eda_csv else None
    eda_preview = load_eda_preview(eda_path) if eda_path and eda_path.is_file() else None
    cft70_path = Path(cft70_json) if cft70_json else None
    cmp_path = Path(cmp_json) if cmp_json else None
    cbc_path = Path(cbc_json) if cbc_json else None
    radlab_path = Path(radlab_csv) if radlab_csv else None
    ui_file = Path(__file__).resolve().parent / "ui" / "index.html"
    panels_js = ui_file.with_name("research_panels.js")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # Avoid logging sensitive subject IDs or payloads

        def _reply(self, status: int, obj: object):
            raw = json.dumps(obj, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            parts = urlsplit(self.path)
            try:
                if parts.path == "/research-panels.js":
                    raw = panels_js.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                    return
                if parts.path in ("/", "/index.html"):
                    raw = ui_file.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                    return
                if parts.path == "/api/health":
                    return self._reply(200, {"status": "ok", "mode": "local_offline", "clinical_validated": False,
                        "research": {"bedrest_available": bool(bedrest_path and bedrest_path.is_file()), "eda_available": eda_preview is not None,
                        "cft70_available": bool(cft70_path and cft70_path.is_file()),
                        "cmp_available": bool(cmp_path and cmp_path.is_file()),
                        "cbc_available": bool(cbc_path and cbc_path.is_file()),
                        "radlab_available": bool(radlab_path and radlab_path.is_file())}})
                if parts.path == "/api/research/bedrest":
                    if not bedrest_path or not bedrest_path.is_file():
                        return self._reply(404, {"error": "Local NASA bed-rest JSON not configured"})
                    data = json.loads(bedrest_path.read_text(encoding="utf-8"))
                    if data.get("source_id") != "NASA_NLSP_BRSMAct_UTMB_C1" or data.get("provenance_kind") != "analog_measured":
                        raise ValueError("Bed-rest provenance mismatch")
                    return self._reply(200, data)
                if parts.path == "/api/research/cft70":
                    if cft70_path is None or not cft70_path.is_file():
                        return self._reply(404, {"error": "CFT70 research JSON not configured"})
                    params = parse_qs(parts.query)
                    return self._reply(200, cft70_view(cft70_path, params.get("subject_id", [None])[0]))
                if parts.path == "/api/research/inspiration4":
                    params = parse_qs(parts.query)
                    study = params.get("study", ["cbc"])[0]
                    filepath = {"cmp": cmp_path, "cbc": cbc_path}.get(study)
                    if filepath is None or not filepath.is_file():
                        return self._reply(404, {"error": "Requested Inspiration4 research JSON not configured"})
                    return self._reply(200, inspiration_view(
                        filepath, study, params.get("subject_id", [None])[0],
                        params.get("measurement", [None])[0]))
                if parts.path == "/api/research/radlab":
                    if radlab_path is None or not radlab_path.is_file():
                        return self._reply(404, {"error": "RadLab instrument CSV not configured"})
                    params = parse_qs(parts.query)
                    return self._reply(200, radlab_view(radlab_path, params.get("instrument_id", [None])[0]))
                if parts.path == "/api/research/environment":
                    if eda_preview is None:
                        return self._reply(404, {"error": "Local NASA EDA CSV not configured"})
                    return self._reply(200, eda_preview)
                params = parse_qs(parts.query)
                if parts.path == "/api/checkins":
                    sid = params.get("subject_id", [""])[0]
                    return self._reply(200, {"records": store.list_subject(sid)})
                if parts.path == "/api/analytics/latest":
                    sid = params.get("subject_id", [""])[0]
                    return self._reply(200, store.latest_analysis(sid))
                return self._reply(404, {"error": "Unknown route"})
            except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
                return self._reply(400, {"error": str(exc)})

        def do_POST(self):
            if urlsplit(self.path).path != "/api/checkins":
                return self._reply(404, {"error": "Unknown route"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= MAX_BODY:
                    raise ValueError("Invalid JSON body size")
                if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                    raise ValueError("Expected application/json")
                payload = json.loads(self.rfile.read(size))
                return self._reply(201, {"record": store.put(payload)})
            except (ValueError, TypeError, OSError, json.JSONDecodeError) as exc:
                return self._reply(400, {"error": str(exc)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description="Offline Crew Vitals Member 2 prototype")
    parser.add_argument("--db", required=True, help="Local SQLite destination outside Git")
    parser.add_argument("--bedrest-json", help="Previously exported NASA bed-rest trends JSON")
    parser.add_argument("--eda-csv", help="Original NASA RR-1 EDA CSV")
    parser.add_argument("--cft70-json", help="Previously generated NASA CFT70 research JSON")
    parser.add_argument("--cmp-json", help="Previously generated Inspiration4 CMP comparison JSON")
    parser.add_argument("--cbc-json", help="Previously generated Inspiration4 CBC comparison JSON")
    parser.add_argument("--radlab-csv", help="Downloaded audited NASA RadLab CSV")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = create_server(db_path=args.db, bedrest_json=args.bedrest_json, eda_csv=args.eda_csv, cft70_json=args.cft70_json, cmp_json=args.cmp_json,
                           cbc_json=args.cbc_json, radlab_csv=args.radlab_csv, port=args.port)
    print(f"Crew Vitals local demo http://127.0.0.1:{server.server_port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
