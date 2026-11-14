import csv
from pathlib import Path

project = Path(__file__).resolve().parent.parent
audit_file = project / "audit" / "data_audit.csv"

new_rows = [
    {
        "check": "EDA telemetry raw file",
        "result": "RR-1_EDA_Telemetry_table.csv",
        "details": "Original CSV copied into data/raw",
        "status": "PASS",
    },
    {
        "check": "EDA telemetry dimensions",
        "result": "12087 rows x 7 columns",
        "details": "Column structure inspected",
        "status": "PASS",
    },
    {
        "check": "EDA telemetry missing values",
        "result": "0",
        "details": "No missing values in any telemetry column",
        "status": "PASS",
    },
    {
        "check": "EDA telemetry timestamps",
        "result": "0 invalid; 0 duplicates; sorted",
        "details": "All timestamps parsed successfully and are ordered",
        "status": "PASS",
    },
    {
        "check": "EDA telemetry sampling interval",
        "result": "300 seconds for 12071 intervals",
        "details": "16 intervals differ from the typical 5-minute cadence",
        "status": "REVIEW",
    },
    {
        "check": "EDA telemetry large gaps",
        "result": "9 intervals greater than 5 minutes",
        "details": "Includes 20-minute and 33-minute gaps; other gaps are 6 or 8 minutes",
        "status": "REVIEW",
    },
    {
        "check": "EDA radiation raw file",
        "result": "RR-1_EDA_Radiation_table.csv",
        "details": "39 daily records; original CSV copied into data/raw",
        "status": "PASS",
    },
    {
        "check": "EDA radiation date coverage",
        "result": "2014-09-21 to 2014-10-29",
        "details": "39 unique, sorted dates with one-day intervals",
        "status": "PASS",
    },
    {
        "check": "EDA radiation missing values",
        "result": "0",
        "details": "No missing values in radiation table",
        "status": "PASS",
    },
    {
        "check": "EDA radiation dose arithmetic",
        "result": "Maximum difference 0.01 for Total; 0.02 for Accumulated",
        "details": "Total approximately equals GCR + SAA; Accumulated approximately equals cumulative Total, allowing rounding",
        "status": "REVIEW",
    },
    {
        "check": "EDA summary verification",
        "result": "6 of 6 metrics matched",
        "details": "Max, Min, Mean and Median recalculated from telemetry and matched to displayed summary after rounding",
        "status": "VERIFIED",
    },
    {
        "check": "EDA repeated telemetry readings",
        "result": "Long identical-value runs detected",
        "details": "ISS CO2, ISS temperature and humidity, and Ground humidity include repeated-value plateaus; causes unknown",
        "status": "REVIEW",
    },
    {
        "check": "EDA Ground CO2 transition",
        "result": "Mean 754.06 before; 3303.16 after",
        "details": "Boundary 2014-09-27 13:35; 2131 records before and 9956 after; cause unknown",
        "status": "REVIEW",
    },
    {
        "check": "EDA mission timeline boundaries",
        "result": "358 before launch; 1828 after return",
        "details": "Classified using supplied milestone timestamps; official interpretation of ISS series remains unconfirmed",
        "status": "REVIEW",
    },
    {
        "check": "EDA radiation accumulated column meaning",
        "result": "Values consistent with cumulative sum of Total",
        "details": "Column label includes mGy_d; official definition and tooltip interpretation require confirmation",
        "status": "REVIEW",
    },
    {
        "check": "EDA ISS series definition",
        "result": "Not independently confirmed",
        "details": "Official documentation needed to establish exact meaning of ISS-labelled environmental series",
        "status": "NOT_DONE",
    },
    {
        "check": "EDA reuse terms",
        "result": "Not independently confirmed",
        "details": "NASA EDA terms and conditions require review before reuse claims",
        "status": "NOT_DONE",
    },
    {
        "check": "EDA scientific validation",
        "result": "Not performed",
        "details": "Structural and numerical checks do not establish sensor accuracy or scientific validity",
        "status": "NOT_DONE",
    },
]

with audit_file.open("r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    existing_rows = list(reader)
    fieldnames = reader.fieldnames

existing_checks = {row["check"] for row in existing_rows}

rows_to_add = [
    row for row in new_rows
    if row["check"] not in existing_checks
]

if rows_to_add:
    with audit_file.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerows(rows_to_add)

print("Existing audit entries:", len(existing_rows))
print("New EDA entries added:", len(rows_to_add))
print("Total audit entries:", len(existing_rows) + len(rows_to_add))
print("Audit update finished.")