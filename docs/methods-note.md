# Crew Vitals — Data Science and Analytics Methods

## 1. Scope

Crew Vitals provides non-diagnostic statistical analysis of
locally entered crew check-ins and separate, historical
NASA research visualizations.

The software does not provide medical diagnoses, astronaut
fitness clearance, clinical risk predictions, or emergency
decision support.

Research populations, subjects, measurements, studies, and
instruments must never be combined into a fabricated
single-person health history.

## 2. Personalized check-in analytics

Production implementation:
`backend/app/analytics/baseline.py`

Input observations include:
- subject_id, study_id, source_id
- provenance_kind, measurement, value, units
- timestamp_utc

A comparison uses only previous observations matching the
same subject, study, source, provenance, measurement and units.

Observations at or after the current timestamp are excluded.
Invalid values and duplicate historical timestamps are rejected
from reference construction and counted separately.

The current local check-in API supports sleep duration in
hours, bounded from 0 to 24.

### Statistical reference

At least five valid prior readings are needed.

For eligible historical values x:

    center = median(x)
    MAD = median(abs(x - center))
    robust_z = (current - center) / (1.4826 * MAD)

A zero MAD produces `insufficient_scale`, not a forced score.

When enough history exists, the last two historical readings
are reserved along with the current reading for persistence
testing. The reference is calculated without those three
readings.

The demonstration rule requires three consecutive observations
on the same side of a robust-z threshold of 3.0.

Possible results include:
- insufficient_history
- insufficient_scale
- insufficient_persistence_history
- no_persistent_flag
- review

These are software/statistical states, not clinical diagnoses.

The threshold and persistence policy are illustrative,
not clinically calibrated or validated.

A result of `no_persistent_flag` does not mean healthy.

## 3. Engineering scenarios

Implementation:
`backend/app/adapters/simulated_crew.py`

The X01 fixture contains:
- stable observations
- a sustained downward-deviation example
- a missing-observation example

Every fixture uses `provenance_kind=simulated`.

These records are artificial regression-test inputs, not
astronaut measurements or NASA source data. Missing values
are rejected from the numerical history, never imputed.

## 4. NASA bed-rest actigraphy

Source: NASA Life Sciences Portal, UTMB Campaign 1.
Source ID: NASA_NLSP_BRSMAct_UTMB_C1

The audited table contains 207 dated records from three
human bed-rest analog participants.

Measurements include sleep duration, sleep efficiency
and sleep latency.

Observations have calendar-date precision only.
No minute-level observation timestamps are invented.

Retrospective trends use available prior observations.
Missing measurements remain missing.

The pre-test data are insufficient to establish a reliable
pre-intervention physiological reference for most subjects.

These participants are not in-flight astronauts.

## 5. NASA CFT70 daily intake

Source: NASA NLSP MR016G CFT70.

The reviewed data contain 1,388 daily energy-intake records
from 14 participants.

A participant-specific reference uses ordinary numeric
pre-test day records only, with a minimum of five valid
pre-test observations.

The reference uses median and MAD; comparisons between
study phases are descriptive.

Ambiguous X1/X2 day labels are preserved but excluded
from reference construction pending interpretation.

Nutrition was influenced by the study protocol.
Changes in energy intake do not establish changes
in astronaut health.

The associated 2D/3D echocardiography data are reported
separately and do not supply an adequate repeated
pre-intervention cardiac reference.

## 6. Inspiration4 serum and blood-count research

Sources:
- NASA OSDR OSD-575: comprehensive metabolic panel
- NASA OSDR OSD-569: complete blood count

The studied cohort contains four astronauts.

Pre-flight sampling points:
L-92, L-44 and L-3.

Post-flight sampling points:
R+1, R+45, R+82 and R+194.

For a measurement with all three pre-flight observations
present, a provisional individual reference is their median.

Later measurements never contribute to that reference.

These are sparse, mission-relative laboratory observations.
They are not real-time physiological telemetry.

The serum analysis generates 80 comparison records.
The blood-count analysis generates 80 records, including
missing observations and source-range review flags.

The original CBC source is used to preserve measurement units.
Hemoglobin is expressed in g/dL.

The unusual C003 L-92 platelet observation is preserved
and flagged for review, not silently corrected.

A laboratory reference-range flag is not a diagnosis.

## 7. Historical NASA environment and radiation

NASA OSDR EDA RR-1:
12,087 historical environmental observations.

The environmental data describe experimental ground/ISS
instrument conditions and must not be assigned to a
specific person's health record.

NASA RadLab DosTel sample:
180 historical readings from DosTel1 and DosTel2.

The acquired sample includes absorbed dose rate in
microgray/hour. Dose-equivalent-rate values are unavailable.

Instrument identities are preserved separately.
Unverified timestamp timezone information is not invented.

The readings cannot establish an individual's radiation
exposure or clinical risk.

The primary environment implementation belongs to Member 4.

## 8. Offline operation

The independently tested research console uses localhost HTTP
and SQLite, and works with previously downloaded local data.

Check-ins remain separate from historical research sources.
Local observations were verified after a server restart.

No cloud inference service is required by the local prototype.

This does not establish that the team's future public
deployment has equivalent offline capabilities, privacy
protections or clinical validation.

## 9. Validation and reproducibility

Automated tests cover:
- subject and study separation
- valid units and numerical values
- duplicate and future-record rejection
- missingness preservation
- zero-MAD and short-history behavior
- statistical persistence
- original-source quality flags
- research provenance checks
- adapter import compatibility
- local persistence and HTTP behavior

Both the legacy and production analytics tests are run by
`.github/workflows/member2-tests.yml`.

Raw NASA files, generated research reports and local SQLite
databases are stored outside the public source repository.

The small X01 engineering fixture is explicitly synthetic
and may be committed as test data.

## 10. Limitations

No reported analysis is a clinical diagnostic model.
No estimated sensitivity, specificity or clinical accuracy
has been established.

No different participant or mission is cross-joined to
create a fictional continuous astronaut history.

Research findings should be presented with their source URL,
study population, measurement units, provenance, missingness
and uncertainty.

Production API schemas and deployment decisions require
review by the team integration owner.
