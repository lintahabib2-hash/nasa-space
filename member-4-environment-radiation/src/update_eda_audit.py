import pandas as pd

path = "audit/data_audit.csv"
df = pd.read_csv(path, encoding="utf-8-sig")

updates = {
    "EDA ISS series definition": {
        "check": "EDA telemetry series context",
        "result": "NASA identifies ISS cabin/flight hardware and ground-control telemetry",
        "details": "EDA overview confirms cabin and hardware telemetry; temperature and RH include flight and ground hardware units. Exact sensor mapping for each column is not specified.",
        "status": "VERIFIED",
    },
    "EDA mission timeline boundaries": {
        "check": "EDA mission timeline boundaries",
        "result": "Launch and LAR Return timestamps match NASA EDA milestones",
        "details": "Launch: 2014-09-21 09:49; LAR Return: 2014-10-25 19:36. Counts were verified using these official boundaries.",
        "status": "VERIFIED",
    },
    "EDA reuse terms": {
        "check": "EDA reuse terms",
        "result": "Public data view/download; redistribution under NASA SMD Science Information Policy",
        "details": "OSDR public access and redistribution guidance reviewed. Preserve dataset-specific citation. This does not establish a blanket license for every dataset.",
        "status": "VERIFIED",
    },
}

for old_name, new_values in updates.items():
    mask = df["check"] == old_name

    if not mask.any():
        print("WARNING: Audit entry not found:", old_name)
        continue

    for column, value in new_values.items():
        df.loc[mask, column] = value

df.to_csv(path, index=False, encoding="utf-8-sig")

print("\nUPDATED AUDIT ENTRIES")
print(df[df["check"].isin(
    [item["check"] for item in updates.values()]
)][["check", "result", "status"]].to_string(index=False))

print("\nTotal audit entries:", len(df))
print("\nStatus counts:")
print(df["status"].value_counts().to_string())
