
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

# Project folders
BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
AUDIT = BASE / "audit"

# Create folders if they do not exist
RAW.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)

# NASA RadLab API example query
URL = (
    "https://visualization.osdr.nasa.gov/radlab/api/"
    "?spacecraft=ISS"
    "&instrument=DosTel"
    "&timestamp>=2022-04-01T23:00"
    "&timestamp<2022-04-02T01:05"
    "&absorbed_dose_rate"
    "&flux"
    "&latitude"
    "&longitude"
    "&altitude"
    "&b"
    "&l"
    "&format=csv"
)

print("Connecting to NASA RadLab API...")

try:
    response = requests.get(URL, timeout=60)

    print("Requested URL:", response.url)
    print("HTTP Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))

    response.raise_for_status()

except requests.RequestException as error:
    print("NASA API request failed:", error)
    raise SystemExit(1)

# Save original response without modifying it
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

raw_path = RAW / f"radlab_probe_{timestamp}.csv"
raw_path.write_bytes(response.content)

print("\nOriginal raw file saved:", raw_path)

# Read downloaded CSV
try:
    df = pd.read_csv(raw_path)

except Exception as error:
    print("CSV parsing failed:", error)
    print("Response preview:")
    print(response.text[:500])
    raise SystemExit(1)

# Dataset inspection
print("\n========== DATASET OVERVIEW ==========")

print("Rows and columns:", df.shape)

print("\n========== COLUMN NAMES ==========")
print(list(df.columns))

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
print(df.isna().sum())

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

# Save first 100 rows for audit
audit_path = AUDIT / "first_100_rows.csv"
df.head(100).to_csv(audit_path, index=False)

print("\nFirst 100 rows saved:", audit_path)

# Inspect timestamp range
if "timestamp" in df.columns and not df.empty:

    ts = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True
    )

    print("\n========== TIMESTAMP RANGE ==========")
    print("Minimum:", ts.min())
    print("Maximum:", ts.max())

print("\nRadLab inspection completed.")
