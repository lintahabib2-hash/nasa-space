import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"
df = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")

df["Controller_Time_GMT"] = pd.to_datetime(df["Controller_Time_GMT"])

launch = pd.Timestamp("2014-09-21 09:49")
return_time = pd.Timestamp("2014-10-25 19:36")

before_launch = df[df["Controller_Time_GMT"] < launch]
after_return = df[df["Controller_Time_GMT"] > return_time]

print("MISSION TIMELINE CHECK")
print("=" * 60)

print("\nBEFORE LAUNCH")
print("Records:", len(before_launch))
print("Start:", before_launch["Controller_Time_GMT"].min())
print("End:", before_launch["Controller_Time_GMT"].max())

print("\nAFTER RETURN")
print("Records:", len(after_return))
print("Start:", after_return["Controller_Time_GMT"].min())
print("End:", after_return["Controller_Time_GMT"].max())

print("\nTimeline verification finished.")