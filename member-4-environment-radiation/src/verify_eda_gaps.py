import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"
df = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")

df["Controller_Time_GMT"] = pd.to_datetime(df["Controller_Time_GMT"])

df = df.sort_values("Controller_Time_GMT").copy()

df["Previous_Time"] = df["Controller_Time_GMT"].shift(1)
df["Gap_Minutes"] = (
    df["Controller_Time_GMT"] - df["Previous_Time"]
).dt.total_seconds() / 60

gaps = df[df["Gap_Minutes"] > 5]

print("TELEMETRY GAPS GREATER THAN 5 MINUTES")
print("=" * 65)

print("Total gaps:", len(gaps))

print(
    gaps[
        ["Previous_Time", "Controller_Time_GMT", "Gap_Minutes"]
    ].to_string(index=False)
)

print("\nGap verification finished.")