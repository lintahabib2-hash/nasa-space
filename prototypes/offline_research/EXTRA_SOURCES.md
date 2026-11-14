# M2.4 — Additional NASA data intake (offline-first)

This module adds **source acquisition and auditing only**; it is not a medical model,
and does not imply that all available NASA data are incorporated in Crew Vitals.
No network calls occur in tests or in the operational Crew Vitals app.

## 1. NASA RadLab — historical ISS instrument data

Source documentation: https://visualization.osdr.nasa.gov/radlab/gui/data-api/

From the repo root, with the current Python environment:

```bash
python member2/extra_sources.py radlab-fetch \
  --out ../member2/data/raw/radlab/iss_dostel_2022-04-01.csv
```

The bounded NASA API query covers `2022-04-01T23:00` through `2022-04-02T01:05` (source timestamp precision). Output is a raw CSV and a companion `.audit.json` that includes SHA-256 and dose-rate units. A successful fetch is **not guaranteed**: the API, archive or instrument may be unavailable; report the actual error. Run an offline-only audit later with:

```bash
python member2/extra_sources.py radlab-audit \
  ../member2/data/raw/radlab/iss_dostel_2022-04-01.csv \
  --out ../member2/reports/radlab_audit.json
```

**Interpretation:** absorbed dose rate is in microgray/hour; dose-equivalent rate is in microsievert/hour. These are physically different quantities. Measurements come from spacecraft instruments, **not individual astronaut dose or diagnosis**. Audit metadata does not fill in missing instrument context or assume a timezone for timestamp strings lacking an explicit offset. Consult NASA RadLab instrument metadata before visualizing.

## 2. NASA OSD-575 — Inspiration4 human serum biomarkers

Study: https://osdr.nasa.gov/bio/repo/data/studies/OSD-575

Use NASA's official OSDR file listing API to discover candidates:

```bash
python member2/extra_sources.py osd575-index \
  --out ../member2/reports/osd575_files.json
```

**This command does not download study measurement files.** Carefully inspect the returned file manifest for publicly accessible processed/transformed assay tables, verify file-level permissions, units, sample IDs and timepoint labels, then download only permitted files through the NASA Files panel or an approved download URL. Some OSDR human biological data are **controlled-access** despite broad study-level openness; no restricted data should be bypassed or redistributed.

Only after inspecting the *actual* assay columns should we build a numerical adapter. Keep pre-flight and post-flight sampling sparse; do not reinterpret it as daily or continuously sensed data. Do not merge an Inspiration4 sample with unrelated bed-rest or RR-1 records by date.

## 3. CSA PRET — cognitive-performance ground research (candidate)

https://open.canada.ca/data/en/dataset/c22fa749-b005-4956-bf68-2ac2b9e68d31

The Canadian Space Agency's open catalog describes PRET data and uses the Open Government Licence – Canada. However, its listed file links point to an old FTP archive; **a working data download and numerical schema have not been confirmed**. This source is not yet integrated or used to calibrate cognitive check-in scores. If usable records become available, identify instrument/test version, units, participant and trial identifiers, missing values, and licence/attribution before integration.

## Integrity and shipping

- Store acquisition outputs in `../member2/data/raw/` and `../member2/reports/` outside the Git repository.
- Verify local audit results and **preserve originals**.
- Never serve potentially restricted data through the public demo.
- Annotate every module with `measured_instrument`, `measured_human_spaceflight`, `measured_human_analog`, or `user_supplied` provenance as applicable.
- Keep the entire **operational application offline**: remote URLs are used only during an optional up-front data download.
- Run `python -m unittest discover -s member2/tests -v` before committing.
