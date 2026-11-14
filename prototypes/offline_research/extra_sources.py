"""Auditable, opt-in acquisition of additional historical NASA data.

This is a NETWORKED ACQUISITION UTILITY, NOT a runtime dependency for Crew Vitals.
The application stays offline: operators obtain data once, inspect provenance,
and place only approved snapshots in their local research store.

Official NASA references:
  https://visualization.osdr.nasa.gov/radlab/gui/data-api/
  https://api.nasa.gov/  (OSDR Study Data File API)
  https://osdr.nasa.gov/bio/repo/data/studies/OSD-575

RadLab is instrument/spacecraft dosimetry, NOT individual exposure.
OSD-575 indexes public/restricted file candidates, not clinical diagnosis data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

RADLAB_BASE = "https://visualization.osdr.nasa.gov/radlab/api/"
OSDR_FILES = "https://osdr.nasa.gov/osdr/data/osd/files/575"
SOURCE_RADLAB = "NASA_OSDR_RADLAB_ISS_DOSTEL_SAMPLE"
SOURCE_OSD575 = "NASA_OSDR_OSD-575_INDEX"
MAX_BYTES = 5_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str) -> bytes:
    """Only invoked by an explicit command; bounded response and clear HTTP errors."""
    req = Request(url, headers={"User-Agent": "CrewVitals-Research-Audit/1.0"})
    with urlopen(req, timeout=30) as resp:
        payload = resp.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("Download exceeds 5 MB limit; narrow the query")
        content_type = resp.headers.get("Content-Type", "").lower()
        if "html" in content_type or payload.lstrip().lower().startswith(b"<!doctype html"):
            raise ValueError("Received HTML instead of data; check the API URL")
        if not payload.strip():
            raise ValueError("Empty API response")
        return payload


def radlab_query() -> str:
    """Bounded ISS instrument sample; no dose-value selection bias."""
    expression = (
        "(spacecraft=ISS)"
        "AND(instrument=DosTel)"
        "AND(timestamp>=2022-04-01T23:00)"
        "AND(timestamp<2022-04-02T01:05)"
    )
    return RADLAB_BASE + "?" + urlencode({
        "query": expression,
        "fields": "absorbed_dose_rate,dose_equivalent_rate",
        "format": "csv",
    })


def audit_radlab(raw: bytes) -> dict:
    """Check CSV structure and numerical measurements; do not infer UTC."""
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("RadLab response is not UTF-8 CSV") from exc
    reader = csv.DictReader(io.StringIO(decoded))
    fields = reader.fieldnames or []
    if "timestamp" not in fields or "instrument_id" not in fields:
        raise ValueError(f"Missing timestamp/instrument_id, found: {fields}")
    measures = [name for name in ("absorbed_dose_rate", "dose_equivalent_rate") if name in fields]
    if not measures:
        raise ValueError("No documented radiation dose-rate field in response")
    rows = list(reader)
    if not rows:
        raise ValueError("Zero measurements; change the time window or instrument")
    if len(rows) > 100_000:
        raise ValueError("Too many rows in sample")
    missing = {name: 0 for name in measures}
    nonmissing = {name: 0 for name in measures}
    minmax: dict[str, list[float] | None] = {name: None for name in measures}
    instrument_ids: set[str] = set()
    timestamps = []
    seen = set()
    duplicates = 0
    offset_aware_count = 0
    for index, row in enumerate(rows, start=2):
        inst = (row.get("instrument_id") or "").strip()
        raw_timestamp = (row.get("timestamp") or "").strip()
        if not inst or not raw_timestamp:
            raise ValueError(f"Missing instrument or timestamp in CSV row {index}")
        try:
            parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Unparseable timestamp in CSV row {index}") from exc
        offset_aware_count += int(parsed.tzinfo is not None)
        timestamps.append(raw_timestamp)
        instrument_ids.add(inst)
        key = (inst, raw_timestamp)
        if key in seen:
            duplicates += 1
        seen.add(key)
        for name in measures:
            cell = (row.get(name) or "").strip()
            if cell.upper() in ("", "NA", "N/A", "NULL", "NAN"):
                missing[name] += 1
                continue
            try:
                value = float(cell)
            except ValueError as exc:
                raise ValueError(f"Invalid {name} in CSV row {index}") from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {name} in CSV row {index}")
            nonmissing[name] += 1
            lohi = minmax[name]
            minmax[name] = [value, value] if lohi is None else [min(lohi[0], value), max(lohi[1], value)]
    if not any(nonmissing.values()):
        raise ValueError("All dose-rate measurements missing")
    return {
        "source_id": SOURCE_RADLAB,
        "source_url": "https://visualization.osdr.nasa.gov/radlab/gui/data-api/",
        "source_type": "historical_spacecraft_instrument_measurements",
        "study_population": "ISS instrument observations; NOT individual astronaut radiation exposure",
        "rows": len(rows),
        "instrument_ids": sorted(instrument_ids),
        "timestamp_first_as_provided": min(timestamps),
        "timestamp_last_as_provided": max(timestamps),
        "timestamp_has_explicit_offset_rows": offset_aware_count,
        "timestamp_timezone_assumption": "none; consult RadLab instrument documentation",
        "duplicate_instrument_timestamp_pairs": duplicates,
        "measurements": {
            key: {
                "units": {"absorbed_dose_rate": "microgray/hour", "dose_equivalent_rate": "microsievert/hour"}[key],
                "valid_rows": nonmissing[key],
                "missing_rows": missing[key],
                "min_max": minmax[key],
            } for key in measures
        },
        "clinical_validation": False,
    }


def osdr_file_candidates(payload: dict) -> list[dict]:
    """Inventory file records without guessing public/restricted access flags."""
    files = []
    seen = set()

    def visit(node):
        if isinstance(node, dict):
            remote = node.get("remote_url")
            if isinstance(remote, str) and remote and remote not in seen:
                seen.add(remote)
                name = next((node.get(k) for k in ("file_name", "filename", "name") if isinstance(node.get(k), str)), None)
                if not name:
                    name = remote.split("file=")[-1].split("/")[-1][:180]
                files.append({
                    "file_name": name,
                    "remote_url": remote,
                    "access": "NOT_VERIFIED_FILE_LEVEL",
                    "candidate_data": any(t in name.lower() for t in ("transformed", "submitted", ".csv", ".tsv")),
                })
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(payload)
    return files


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("radlab-fetch", help="Download bounded NASA dosimetry sample")
    fetch.add_argument("--out", required=True)
    audit = sub.add_parser("radlab-audit", help="Audit previously downloaded raw CSV offline")
    audit.add_argument("csv_path")
    audit.add_argument("--out", required=True)
    idx = sub.add_parser("osd575-index", help="Fetch NASA file manifest, NOT the biological data")
    idx.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.command == "radlab-fetch":
        url = radlab_query()
        raw = fetch_bytes(url)
        report = audit_radlab(raw)
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        report.update({"download_query": url, "sha256": sha256(raw),
                       "downloaded_at_utc": datetime.now(timezone.utc).isoformat()})
        write_json(path.with_suffix(path.suffix + ".audit.json"), report)
        print(json.dumps(report, indent=2))
    elif args.command == "radlab-audit":
        raw = Path(args.csv_path).read_bytes()
        report = audit_radlab(raw)
        report["sha256"] = sha256(raw)
        write_json(Path(args.out), report)
        print(json.dumps(report, indent=2))
    elif args.command == "osd575-index":
        raw = fetch_bytes(OSDR_FILES)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("OSDR file endpoint did not return JSON") from exc
        manifest = {
            "source_id": SOURCE_OSD575,
            "source_url": "https://osdr.nasa.gov/bio/repo/data/studies/OSD-575",
            "files_api": OSDR_FILES,
            "index_sha256": sha256(raw),
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "study_scope": "Four Inspiration4 astronauts; sparse pre/post-flight serum sampling",
            "access_policy": "File-specific access must be checked. Some NASA human data may be restricted; never download locked files or imply redistribution rights.",
            "files_found": osdr_file_candidates(payload),
            "number_found": len(osdr_file_candidates(payload)),
        }
        write_json(Path(args.out), manifest)
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
