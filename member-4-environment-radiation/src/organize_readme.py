from pathlib import Path

path = Path("README.md")
content = path.read_text(encoding="utf-8")

completed_items = [
    "- [x] Review NASA OSDR public-access and redistribution guidance; preserve dataset-specific citation and conditions.",
    "- [x] Verify general EDA ISS/flight-hardware and ground-control telemetry context.",
    "- [x] Verify launch and LAR Return timestamps against NASA EDA milestones.",
]

for item in completed_items:
    content = content.replace(item + "\n", "")

marker = "\n\n### Pending"
insert = "\n\n" + "\n".join(completed_items)

if marker not in content:
    raise ValueError("Pending section not found. README unchanged.")

content = content.replace(marker, insert + marker, 1)

path.write_text(content, encoding="utf-8")
print("Completed tasks moved to Completed section.")
