# Environment and radiation audit sheet

> Owner: Member 4 (Environment & Radiation): Muhammad Bilal Hussain.
> Moved here from `member-4-environment-radiation/README.md` during integration. Paths updated:
> adapter `backend/app/environment/osdr_eda.py`, `get_environment_series()` in `backend/app/environment/series.py`,
> audit records [environment-audit.csv](environment-audit.csv), RadLab first 100 rows `data/nasa/radlab/first_100_rows.csv`.
>
> **Open item:** the instrument/sensor ID for the RR-1 series is not given in the export.
> Fallback (cited static chart, not ingested data): [data/fallback/](../data/fallback/README.md).

## EDA RR-1 telemetry: first 100 rows (the chosen source)

Rows 1–100 of `RR-1_EDA_Telemetry_table.csv`, saved unchanged as `data/nasa/osdr-eda/first_100_rows.csv`.

| Check | Result |
|---|---|
| Mission tag | RR-1 (from the EDA export; rodent-habitat experiment, not crew data) |
| Instrument / sensor ID | Not given in the export |
| Time column | `Controller_Time_GMT`, minute precision, read as UTC |
| Time span | 2014-09-20 03:59 to 12:14 UTC |
| Sampling interval | 300 s for all 99 intervals; sorted; 0 duplicate timestamps |
| Missing values | 0 blank cells in all 7 columns |
| Units (from column names) | `degC` (temperature), `percent` (relative humidity), `ppm` (CO2) |
| Negative / non-finite | 0 in every column |

| Column | Min | Max | Median | Distinct values |
|---|---:|---:|---:|---:|
| Temp_degC_Ground | 22.7 | 24.1 | 23.4 | 15 |
| Temp_degC_ISS | 22.8 | 24.1 | 23.4 | 14 |
| RH_percent_Ground | 36 | 43 | 38 | 8 |
| RH_percent_ISS | 36 | 39 | 37 | 4 |
| CO2_ppm_Ground | 456 | 494 | 476 | 18 |
| CO2_ppm_ISS | 2621 | 2653 | 2641 | 9 |

Outliers: no value is physically implausible. A robust |z| > 5 screen flags 43 ISS CO2 rows, but only because that
column moves in tiny steps (9 distinct values across 32 ppm), so its median absolute deviation is very small; these are
not treated as outliers. The adapter only quarantines physically impossible (negative) readings.

## Primary Data Source (NASA EDA — RR-1)

- **Source ID:** D01
- **Source Name:** NASA Environmental Data Application (EDA)
- **Citation URL:** https://visualization.osdr.nasa.gov/eda/
- **Access Date:** 14 November 2026
- **Version Status:** Not displayed in the EDA pages checked.

### Attribution
Data and visualizations are courtesy of the Environmental Data Application (EDA) (https://visualization.osdr.nasa.gov/eda/). Version: not displayed on the site (accessed 14 Nov 2026).

### Repository Data Policy & Sample Note
- Due to re-use terms, only an approved small sample dataset is stored in this repository. 
- For the complete dataset, please visit the official [NASA EDA Website](https://visualization.osdr.nasa.gov/eda/).

---

## Project Role

NASA Space Apps Challenge - Environment & Radiation Specialist.

## Responsibilities

- Inspect NASA OSDR, Environmental Data App (EDA), and RadLab data sources.
- Identify relevant environmental and radiation datasets.
- Download original data without modifying it.
- Inspect columns, data types, missing values, timestamps, and numerical quality.
- Verify scientific field definitions and units using official documentation.
- Prepare verified data and audit records for the team.

---

## 1. RadLab Initial Inspection

### Data Source

NASA RadLab API

https://visualization.osdr.nasa.gov/radlab/api/

### Initial Query

- Spacecraft: ISS
- Instrument: DosTel
- Start: 2022-04-01 23:00 UTC
- End: 2022-04-02 01:05 UTC
- Format: CSV

### Initial Results

- HTTP Status: 200
- Records: 180
- Columns: 11
- DosTel1 records: 84
- DosTel2 records: 96
- Missing values: 0
- Exact duplicate rows: 0
- Invalid timestamps: 0
- Earliest timestamp: 2022-04-01 23:00:00 UTC
- Latest timestamp: 2022-04-02 01:04:40 UTC

### Observed Columns

timestamp, instrument_id, absorbed_dose_rate, altitude, b, flux, instrument, l, latitude, longitude, spacecraft

### Units from Official RadLab API Documentation

| Field | Unit |
|---|---|
| absorbed_dose_rate | microGy/hour (μGy/hour) |
| flux | cm^-2 sr^-1 s^-1 |
| altitude | km |
| b | nT |
| l | Unitless |
| latitude | Degrees |
| longitude | Degrees |

Source: NASA RadLab Data API documentation.

https://visualization.osdr.nasa.gov/radlab/gui/data-api/

### Numerical Quality Checks

- Non-finite numerical values: 0
- Negative absorbed dose rate values: 0
- Negative flux values: 0
- Zero absorbed dose rate values: 0
- Latitude outside -90 to 90 degrees: 0
- Longitude outside -180 to 180 degrees: 0

### Timestamp and Sampling Checks

- Repeated timestamps within the same instrument: 0
- Median sampling interval: 100 seconds for both instruments
- Sampling intervals are variable.
- Gaps greater than 150 seconds: 4
- DosTel1 gaps: 1055, 185, and 154 seconds
- DosTel2 gap: 195 seconds
- Longest observed gap: 1055 seconds

### Instrument Timestamp Coverage

- Common start: 2022-04-01 23:00:00 UTC
- Common end: 2022-04-02 01:04:33 UTC
- Common duration: 2 hours, 4 minutes, 33 seconds
- DosTel1 records within common coverage: 83
- DosTel2 records within common coverage: 96

Note: Large time gaps are documented for investigation. They have not been classified as instrument failures or confirmed missing data.

---

## 2. NASA Environmental Data App (EDA) — RR-1 Inspection

### Data Source

NASA Environmental Data App (EDA)

https://visualization.osdr.nasa.gov/eda/

### Dataset Files

Three RR-1 CSV files were downloaded (kept locally in `data/nasa/osdr-eda/raw/`, not committed):

- `RR-1_EDA_Telemetry_table.csv`
- `RR-1_EDA_Radiation_table.csv`
- `RR-1_EDA_Summary_table.csv`

The original files in the parent project directory were left unchanged.

### Telemetry Table

- Records: 12,087
- Columns: 7
- Columns:
   - Controller_Time_GMT
   - Temp_degC_Ground
   - Temp_degC_ISS
   - RH_percent_Ground
   - RH_percent_ISS
   - CO2_ppm_Ground
   - CO2_ppm_ISS
- Missing values: 0
- Invalid timestamps: 0
- Duplicate timestamps: 0
- Timestamps sorted: Yes
- Start: 2014-09-20 03:59:00
- End: 2014-11-01 03:54:00

### Telemetry Sampling Interval

- Total intervals: 12,086
- Typical interval: 300 seconds (5 minutes)
- 300-second intervals: 12,071
- Non-300-second intervals: 15

The 15 other intervals are:
- 180 seconds: 1
- 240 seconds: 5
- 360 seconds: 6
- 480 seconds: 1
- 1200 seconds: 1
- 1980 seconds: 1

### Telemetry Gaps Greater Than 5 Minutes

Nine intervals were identified:

| Date (2014) | Gap |
|---|---:|
| September 24 | 6 minutes |
| October 1 | 6 minutes |
| October 1 | 6 minutes |
| October 6 | 20 minutes |
| October 8 | 6 minutes |
| October 15 | 33 minutes |
| October 22 | 6 minutes |
| October 22 | 8 minutes |
| October 29 | 6 minutes |

The 20-minute and 33-minute gaps are the largest observed gaps. These are timestamp intervals and do not independently establish sensor failure or data loss.

### M3 Environment Fixture

The M4 environment adapter uses the NASA EDA RR-1 telemetry source (repository Source ID: `D01`) and reads `data/nasa/osdr-eda/raw/RR-1_EDA_Telemetry_table.csv` (not committed). The adapter is `backend/app/environment/osdr_eda.py`; `get_environment_series()` is in `backend/app/environment/series.py`.

- Source telemetry: 12,087 rows, ordered by `Controller_Time_GMT`.
- Fixture series: 300 `CO2_ppm_ISS` points selected at even row-index intervals from the timestamp-sorted data, retaining both endpoints.
- Missing and non-finite CO2 readings are serialized as JSON `null`, never as `0` or `NaN`. The current source file contains no missing telemetry readings.
- M3 fixture: `frontend/src/features/environment-context/fixtures/environment.sample.json`.
- The environment context card citation note uses the same attribution and version/access-date text shown above.
- Fixture `source_id`: `NASA_OSDR_EDA_RR1`; repository source registry ID: `D01`.
- Integrated into the main project structure; the dashboard card is `frontend/src/features/environment-context/EnvironmentContextCard.tsx`.

### Radiation Table

- Records: 39
- Columns: 5
- Date range: 2014-09-21 to 2014-10-29
- Missing values: 0
- Invalid dates: 0
- Duplicate dates: 0
- Dates sorted: Yes
- All 38 date intervals are one day.

Observed columns:

- Date
- GCR_Dose_mGy_d
- SAA_Dose_mGy_d
- Total_Dose_mGy_d
- Accumulated_Dose_mGy_d

### Radiation Arithmetic Checks

- Total dose approximately equals GCR dose + SAA dose.
- Maximum absolute difference: 0.01.
- Accumulated dose approximately equals the cumulative sum of Total dose.
- Maximum absolute difference: 0.02.

These small differences are consistent with rounding. The official definition and unit interpretation of the accumulated-dose column still require confirmation.

### Summary Table Verification

The summary table contains 10 rows and 6 columns.

Six telemetry metrics were independently recalculated:

- Ground CO2
- ISS CO2
- Ground relative humidity
- ISS relative humidity
- Ground temperature
- ISS temperature

Max, Min, Mean, and Median matched the summary values after rounding to two decimal places.

Result: 6 of 6 metric comparisons matched.

### Repeated-Value Plateaus

Long consecutive identical readings were identified:

- ISS CO2: 2646 ppm for 1,837 records, from September 21 04:24 to September 27 13:25.
- ISS temperature: 26.8 °C for 314 records.
- ISS relative humidity: 70% for 314 records.
- Additional repeated-value runs were found in ISS and Ground humidity.

These are observations, not confirmed sensor faults. Their causes remain unknown.

### Ground CO2 Transition

A marked change was observed around September 27, 2014 at 13:50.

| Measurement | Before | After |
|---|---:|---:|
| Records | 2,134 | 9,953 |
| Mean | 754.20 ppm | 3,303.90 ppm |
| Minimum | 438 ppm | 1,840 ppm |
| Maximum | 1,498 ppm | 4,690 ppm |

The cause of this transition has not been established.

### Mission Timeline Boundaries

Using the supplied milestone timestamps:

- Before launch boundary: 358 records.
- After return boundary: 1,828 records.

These are timestamp-based classifications. The official meaning of the ISS-labelled environmental series and milestone interpretation still require confirmation.

---

## 3. Audit Records

The combined audit file contains RadLab and EDA inspection records:

- `audit/data_audit.csv`

Current audit count: 37 entries.

| Status | Count |
|---|---:|
| PASS | 21 |
| REVIEW | 8 |
| VERIFIED | 6 |
| NOT_DONE | 2 |

The audit records document structural checks, numerical observations, review items, and pending scientific/source verification.

---

## 6. Important Limitations

- These are historical datasets, not live telemetry feeds.
- RR-1 EDA data must not automatically be interpreted as astronaut cabin telemetry.
- Repeated readings and abrupt changes have not been assigned causes.
- Basic data-quality checks do not establish scientific accuracy.
- No astronaut safety thresholds or risk classifications have been assumed.
- The environment adapter prepares the M3 sample fixture; no risk engine or astronaut risk classifications have been implemented.
- Dataset reuse and licensing conditions must be checked before making reuse claims.