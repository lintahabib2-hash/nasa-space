
# Source Registry

> Owner: Member 1 (Coordination, Science, Pitch)
>
> Audit reference: Astronaut Health Monitoring – Comprehensive Data & Resource Audit, reviewed 2026-11-13.
>
> Important: A source being listed here does not mean its raw data has been downloaded or integrated into the project.

## 1. Official NASA / CSA Challenge Resources

| ID | Source | URL | What it supports | Limitations / Notes |
|---|---|---|---|---|
| C01 | NASA Human Research Program Risks | https://www.nasa.gov/hrp/risks/ | Evidence-based health risk descriptions, including cardiovascular, sleep, fitness, immune, behavioral, ocular and radiation risks. | Research and risk context only. Does not provide astronaut-level continuous vital recordings or clinical thresholds. |
| C02 | NASA HRP Five Hazards | https://www.nasa.gov/hrp/hazards/ | The five exploration hazards: radiation, isolation/confinement, distance, gravity and hostile/closed environments. | Supports hazard explanations, not cabin telemetry or operational alert policies. |
| C03 | NASA HRP Ongoing Research | https://www.nasa.gov/hrp/ongoing-hrp-research/ | Research areas and measurement approaches that can inform indicator selection. | Does not provide downloadable data for every research activity described. |
| C04 | Canadian Space Agency: Monitoring Radiation and Astronaut Health | https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp | Radiation monitoring context and space radiation instruments, including CANS. | Does not provide a patient-level radiation time series or personal dose recommendations. |
| C05 | Canadian Space Agency: Why Conduct Science Experiments in Space? | https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp | Background on long-duration spaceflight, microgravity, radiation and isolation. | General science context; not a numerical astronaut vital-sign dataset. |

## 2. NASA Measured / Analog Data Sources

| ID | Source | URL | What it supports | Limitations / Current status |
|---|---|---|---|---|
| D01 | NASA OSDR Environmental Data Application (EDA) | https://visualization.osdr.nasa.gov/eda/ | Environmental measurements such as CO2, temperature, relative humidity and radiation from selected ISS experiments or hardware. | Tables and export options were verified in the audit, but raw files were not retrieved. Confirm mission, sensor location, units and sampling interval before use. |
| D02 | NASA OSDR RadLab | https://visualization.osdr.nasa.gov/radlab/gui/overview/ | Radiation instrument readings and historical radiation context from ISS / beyond-LEO platforms. | Export options were documented, but no raw file was retrieved. Instrument readings must not be presented as an individual's personal dose or health risk. |
| D03 | NASA NLSP UTMB Bedrest Campaign 1 Actigraphy | https://nlsp.nasa.gov/search/data/details/e26501eb-7d7a-5012-8c8e-c5bdb3eecaf6?dataType=DATASETS | Sleep-related measures such as sleep duration, latency and efficiency in a bed-rest analog study. | Ground-based bed-rest participants, not astronauts sleeping in space. Actual files and access conditions still require verification. |
| D06 | NASA OSDR Study OSD-575 | https://osdr.nasa.gov/bio/repo/data/studies/OSD-575 | Serum metabolic, immune and cardiac-related biomarker research context. | Sample-based measurements, not continuous wearable readings. Verify individual files and sampling details before use. |
| D18 | NASA Human Research Program Standard Measures | https://www.nasa.gov/reference/standard-measures/ | Standardized categories for sleep, activity, cognition, blood, urine and fitness measurements. | Not all astronaut records are publicly downloadable. |
| D19 | NASA Human Research Roadmap Evidence Reports | https://humanresearchroadmap.nasa.gov/evidence/ | Scientific evidence about spaceflight health risks, including sleep and cardiovascular risks. | Evidence reports support explanations; they are not themselves continuous sensor datasets. |

## 3. External Earth-Based Reference Sources

| ID | Source | URL | What it supports | Limitations / Notes |
|---|---|---|---|---|
| E01 | WESAD Dataset | https://archive.ics.uci.edu/dataset/465/wesad | Independent testing of physiological signal processing methods. | Earth-based wearable dataset; never label its records as NASA or astronaut data. |
| E02 | BIDMC PPG and Respiration Dataset | https://www.physionet.org/content/bidmc/1.0.0/ | Independent testing of physiological signal processing methods. | Hospital-based Earth data; separate from astronaut records and spaceflight measurements. |

## 4. Team-Created Demonstration Data

| ID | Source | What it supports | Limitations / Notes |
|---|---|---|---|
| X01 | Team-created simulated crew records | Demonstrating daily check-ins, personal trends, missing-data cases and the prototype interface. | Fictional demonstration data only. Must never be described as NASA-measured or actual astronaut observations. |

## 5. Provenance and Usage Rules

1. Every displayed measurement must identify its source and provenance.
2. Use the appropriate provenance category: `nasa_measured`, `analog_measured`, `external_earth`, `simulated` or `manually_entered`.
3. Do not combine different people, missions, locations or study populations as if they belong to one astronaut.
4. Do not describe simulated records as real NASA observations.
5. Do not interpret instrument radiation readings as personal biological risk or individual accumulated dose.
6. Do not present trends or prototype indicators as medical diagnoses or validated clinical predictions.
7. If a dataset has not been downloaded and inspected, clearly state that it has not yet been ingested.
8. Keep the original source URL and measurement context available wherever evidence is displayed.

## 6. Download / Integration Status

| Source ID | Status at time of audit |
|---|---|
| C01–C05 | Official challenge research resources reviewed. |
| D01 | Data tables verified; raw export not retrieved. |
| D02 | Export options documented; raw file not retrieved. |
| D03 | Dataset entry verified; actual files not inspected. |
| D06 | Study identified; individual files require verification. |
| D18–D19 | NASA program / evidence resources identified. |
| E01–E02 | External reference datasets identified; use only for separate method testing. |
| X01 | Team-created simulated data; demonstration use only. |

> Last audit review: 2026-11-13.
