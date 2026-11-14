
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"

telemetry = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")
summary = pd.read_csv(base / "RR-1_EDA_Summary_table.csv")

summary = summary.set_index("Unnamed: 0")

mapping = {
    "CO2 Ground [PPM]": "CO2_ppm_Ground",
    "CO2 ISS [PPM]": "CO2_ppm_ISS",
    "Relative Humidity Ground [%]": "RH_percent_Ground",
    "Relative Humidity ISS [%]": "RH_percent_ISS",
    "Temperature Ground [C]": "Temp_degC_Ground",
    "Temperature ISS [C]": "Temp_degC_ISS",
}

stats = ["Max", "Min", "Mean", "Median"]

print("SUMMARY VS RECALCULATED TELEMETRY")
print("=" * 65)

for label, column in mapping.items():
    original = summary.loc[label, stats].astype(float).round(2)

    recalculated = (
        telemetry[column]
        .agg(["max", "min", "mean", "median"])
        .set_axis(stats)
        .round(2)
    )

    print(f"\nMetric: {label}")
    print("Summary:     ", original.to_dict())
    print("Recalculated:", recalculated.to_dict())
    print("Match:", original.equals(recalculated))

print("\nVerification finished.")
