
# Hazard → Risk → Indicator → Source Mapping

> Owner: Member 1 (Coordination, Science, Pitch)
>
> Purpose: Connect NASA-recognized spaceflight hazards with health risks, measurable indicators and supporting scientific sources.
>
> Important: Indicators support awareness and review only. They are not validated clinical diagnostic or prediction thresholds.

## 1. Hazard-to-Indicator Mapping

| Spaceflight hazard / context | Health risk | Possible indicator | Supporting source | Interpretation and limitation |
|---|---|---|---|---|
| Isolation and confinement | Sleep and circadian disruption | Sleep duration, sleep timing, sleep quality check-in and activity patterns | C01, C02, C03, D03, D18, D19 | Review personal trends. Do not claim a specific value diagnoses sleep impairment. |
| Isolation and confinement | Behavioral health challenges and stress | Voluntary mood and stress self-report; brief cognitive task results | C01, C02, C03, D18, D19 | Self-reported information is not a psychiatric diagnosis. Avoid diagnosing mental health conditions from voice or task results. |
| Altered gravity / microgravity | Physical deconditioning | Exercise completion, exercise minutes and mobility or strength measurements when available | C01, C02, C03, D18, D19 | Exercise records alone cannot prove prevention or measurement of muscle and bone loss. |
| Altered gravity / microgravity | Cardiovascular adaptation | Resting heart rate, blood pressure and heart-rate variability when valid measurements are available | C01, C03, D18, D19 | Measurement context matters. Do not claim arrhythmia prediction without validated targets. |
| Radiation | Space radiation exposure context | Radiation instrument dose rate, flux and event timestamps | C01, C02, C04, D02 | Instrument readings are not automatically an individual's personal dose or biological risk. |
| Hostile / closed environment | Environmental health concerns | CO2, temperature, relative humidity, light and noise when measured | C02, C03, D01 | Identify the sensor location and measurement context. Do not assume experiment-hardware measurements represent an astronaut's personal exposure. |
| Distance from Earth | Limited access to immediate medical support | Check-in availability, data availability and local/offline access status | C02, C05 | These are operational support indicators, not direct measurements of a medical condition. |
| Multiple exploration hazards | Ocular, immune and other physiological risks | OCT, laboratory panels, immune markers or other specialized measurements if legitimately available | C01, C03, D05, D06, D18, D19 | These measurements are outside the initial prototype scope unless verified data and suitable expertise are available. |

## 2. Priority Indicators for the Prototype

### P0 — Initial Prototype

| Indicator | Input / measurement | Intended use |
|---|---|---|
| Sleep duration | User-entered or simulated sleep hours | Show personal sleep trends. |
| Sleep quality | Optional self-reported rating | Show changes in self-reported sleep quality. |
| Activity / exercise | User-entered or simulated activity minutes | Review activity patterns over time. |
| Resting heart rate | Valid user-entered or simulated measurement | Display personal measurement trends. |
| Mood / stress check-in | Optional self-reported response | Support personal awareness, not diagnosis. |
| Environmental context | Verified NASA environmental observations, if successfully retrieved | Display historical environmental conditions separately from personal health measurements. |

### P1 — Optional Extensions

| Indicator | Input / measurement | Intended use |
|---|---|---|
| Cognitive task performance | Brief task measurements, if implemented | Display task performance trends without diagnosing impairment. |
| Radiation context | Verified NASA instrument observations | Show historical instrument readings with source and units. |
| Biomarker context | Verified laboratory study measurements | Provide research context only; do not mix with daily check-ins. |

### Deferred — Not Part of the Initial Prototype

- Medical diagnosis or treatment recommendations.
- Prediction of disease or medical emergencies.
- Individual cancer-risk estimation from radiation instrument readings.
- SANS diagnosis using facial appearance.
- Bone or muscle loss estimation from exercise records alone.
- Clinical decisions based on unvalidated cognitive or behavioral indicators.

## 3. Source Reference Key

| Source ID | Source name |
|---|---|
| C01 | NASA Human Research Program Risks |
| C02 | NASA HRP Five Hazards |
| C03 | NASA HRP Ongoing Research |
| C04 | Canadian Space Agency radiation monitoring resource |
| C05 | Canadian Space Agency science in space resource |
| D01 | NASA OSDR Environmental Data Application |
| D02 | NASA OSDR RadLab |
| D03 | NASA NLSP UTMB Bedrest Campaign 1 Actigraphy |
| D05 | NASA OSDR OSD-569 |
| D06 | NASA OSDR OSD-575 |
| D18 | NASA Human Research Program Standard Measures |
| D19 | NASA Human Research Roadmap Evidence Reports |

See `docs/source-registry.md` for source URLs and limitations.

## 4. Scientific and Data-Handling Rules

1. Every indicator must have a clear definition, unit and source.
2. Identify whether a value is NASA-measured, analog-measured, external, simulated or manually entered.
3. Do not join different populations, missions or locations using timestamp alone.
4. Do not treat bed-rest participants as astronauts in space.
5. Do not combine laboratory biomarkers with daily wearable measurements as if they were the same measurement type.
6. Do not interpret environmental readings as personal astronaut exposure without supporting evidence.
7. Do not create clinical alert thresholds without validated scientific justification.
8. Missing or invalid measurements must be identified rather than silently replaced.
9. Personal baselines must use the individual's own available history, not another person's records.
10. Display supporting evidence and limitations wherever indicators are presented.

## 5. Review Status

- Initial hazard-to-risk mapping prepared from the comprehensive source audit dated 2026-11-13.
- Indicator selection is a research-informed prototype proposal.
- Final implementation must be checked against the actual data available in the project.
- Member 1 scientific review is required before these mappings are used in the final presentation.

> Status: Initial science mapping prepared; implementation and source availability still require verification.
