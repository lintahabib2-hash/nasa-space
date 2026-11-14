import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"
df = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")

df["Controller_Time_GMT"] = pd.to_datetime(df["Controller_Time_GMT"])

boundary = pd.Timestamp("2014-09-27 13:35")

before = df[df["Controller_Time_GMT"] < boundary]
after = df[df["Controller_Time_GMT"] >= boundary]

for name, data in [("BEFORE", before), ("AFTER", after)]:
    print(f"\n{name} TRANSITION")
    print("Records:", len(data))
    print("Start:", data["Controller_Time_GMT"].min())
    print("End:", data["Controller_Time_GMT"].max())
    print("Ground CO2:")
    print(data["CO2_ppm_Ground"].describe().round(2).to_string())

print("\nPhase comparison finished.")