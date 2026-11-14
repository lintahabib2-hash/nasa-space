
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data" / "raw"

df = pd.read_csv(base / "RR-1_EDA_Telemetry_table.csv")
df["Controller_Time_GMT"] = pd.to_datetime(df["Controller_Time_GMT"])

start = pd.Timestamp("2014-09-27 12:30")
end = pd.Timestamp("2014-09-27 14:30")

window = df[
    df["Controller_Time_GMT"].between(start, end)
]

print("CO2 CHANGE AROUND 27 SEPTEMBER 2014")
print("=" * 65)

print(
    window[
        [
            "Controller_Time_GMT",
            "CO2_ppm_Ground",
            "CO2_ppm_ISS",
        ]
    ].to_string(index=False)
)

print("\nGround CO2 before and after 13:35:")

before = df.loc[
    df["Controller_Time_GMT"] < pd.Timestamp("2014-09-27 13:35"),
    "CO2_ppm_Ground",
].tail(100)

after = df.loc[
    df["Controller_Time_GMT"] >= pd.Timestamp("2014-09-27 13:35"),
    "CO2_ppm_Ground",
].head(100)

print("Previous 100 readings mean:", round(before.mean(), 2))
print("Next 100 readings mean:", round(after.mean(), 2))

print("\nJump verification finished.")
