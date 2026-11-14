from pathlib import Path

path = Path("README.md")
content = path.read_text(encoding="utf-8")

replacements = {
    "| REVIEW | 9 |": "| REVIEW | 8 |",
    "| VERIFIED | 3 |": "| VERIFIED | 6 |",
    "| NOT_DONE | 4 |": "| NOT_DONE | 2 |",

    "- [ ] Verify EDA Terms and Conditions and data reuse requirements.":
    "- [x] Review NASA OSDR public-access and redistribution guidance; preserve dataset-specific citation and conditions.",

    "- [ ] Confirm official definition of the EDA ISS-labelled series.":
    "- [x] Verify general EDA ISS/flight-hardware and ground-control telemetry context.",

    "- [ ] Confirm milestone timestamps and mission interpretation from official documentation.":
    "- [x] Verify launch and LAR Return timestamps against NASA EDA milestones.",

    "- [ ] Complete scientific validation and source-specific interpretation.":
    "- [ ] Complete scientific validation and exact sensor/column interpretation.",

}

for old, new in replacements.items():
    if old not in content:
        print("WARNING: Text not found:", old)
    else:
        content = content.replace(old, new)
        print("Updated:", old)

path.write_text(content, encoding="utf-8")
print("\nREADME update completed.")
