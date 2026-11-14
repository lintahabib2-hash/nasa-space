
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"
df = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")

columns = [
    "CO2_ppm_ISS",
    "Temp_degC_ISS",
    "RH_percent_ISS",
    "RH_percent_Ground",
    "Temp_degC_Ground",
]

print("CONSECUTIVE IDENTICAL READING CHECK")
print("=" * 70)

for column in columns:
    groups = df[column].ne(df[column].shift()).cumsum()

    runs = (
        df.groupby(groups)
        .agg(
            value=(column, "first"),
            records=(column, "size"),
            start=("Controller_Time_GMT", "first"),
            end=("Controller_Time_GMT", "last"),
        )
        .query("records >= 50")
        .sort_values("records", ascending=False)
    )

    print(f"\nCOLUMN: {column}")

    if runs.empty:
        print("No consecutive identical run of 50 or more records.")
    else:
        print(runs.head(10).to_string(index=False))

print("\nPlateau verification finished.")
