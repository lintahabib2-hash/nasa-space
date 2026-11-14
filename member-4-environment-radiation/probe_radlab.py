
import requests
import pandas as pd
from io import StringIO

API_URL = "https://visualization.osdr.nasa.gov/radlab/api/"

params = [
    ("spacecraft", "ISS"),
    ("instrument", "DosTel"),
    ("timestamp>=", "2022-04-01T23:00"),
    ("timestamp<", "2022-04-02T01:05"),
    ("flux", ""),
    ("format", "json")
]

print("Testing NASA RadLab API...")

try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=60
    )

    print("HTTP Status:", response.status_code)
    print("Request URL:", response.url)

    if response.status_code != 200:
        print("Server response:")
        print(response.text[:1500])
        raise SystemExit("API request unsuccessful.")

    df = pd.read_json(StringIO(response.text))

    print("\n--- COLUMNS ---")
    print(df.columns.tolist())

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES ---")
    print(df.isnull().sum())

    print("\n--- FIRST 5 ROWS ---")
    print(df.head())

    if "timestamp" in df.columns and not df.empty:
        timestamps = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
            utc=True
        )
        print("\n--- TIMESTAMP RANGE ---")
        print("Minimum:", timestamps.min())
        print("Maximum:", timestamps.max())

    print("\nTotal rows:", len(df))

except requests.RequestException as error:
    print("Request error:", error)
