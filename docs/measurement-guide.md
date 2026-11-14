# Measurement Guide: How and Why Each Indicator Is Taken in Space

> Owner: Member 1 (Coordination, Science, Pitch)  
> Status: Science review draft  
> Purpose: Explain the measurements used by Crew Vitals, their relevance to spaceflight, and their limitations.

## 1. Important measurement principles

Crew Vitals uses a combination of manually entered, self-reported, and sensor-based observations.

Not every measurement is collected continuously in space. The method depends on the indicator, available equipment, mission procedures, and crew workload.

The project distinguishes between:

- **Manually entered:** Information entered by a crew member.
- **Crew self-report:** Personal ratings or observations reported by a crew member.
- **NASA-measured:** Observations obtained from an identified NASA instrument or dataset.
- **Simulated:** Fictional values generated for software testing and demonstrations.

The dashboard's sample crew records are simulated data (X01). They are not actual astronaut health records or NASA measurements.

Measurements support personal trend awareness and human review. They do not independently diagnose diseases, determine fitness for duty, or prescribe treatment.

## 2. Indicator measurement guide

### 2.1 Sleep duration

**How measured:**  
Sleep duration can be estimated using wrist actigraphy or wearable devices that record movement. A sleep log can also be completed by the crew member to record sleep and wake times.

**Why it matters:**  
Spaceflight schedules, artificial lighting, operational demands, and changes in the sleep environment can affect sleep patterns. Monitoring sleep duration can help identify changes over time.

**Limitations:**
- Wearable estimates are not equivalent to laboratory sleep studies.
- Movement-based devices may misclassify periods of rest and sleep.
- Sleep duration alone does not establish sleep quality or fatigue.
- Crew Vitals does not apply a clinically validated sleep alert threshold.

### 2.2 Mood

**How measured:**  
A crew member voluntarily reports mood using a simple rating scale from 1 to 5.

**Why it matters:**  
Isolation, confinement, workload, and separation from family can influence psychological well-being during long-duration missions. Self-reporting provides a way to communicate personal experiences.

**Limitations:**
- Mood ratings are subjective.
- A simple rating cannot diagnose depression or another mental-health condition.
- A single rating does not establish a long-term pattern.
- Reporting must remain voluntary and respectful of privacy.

### 2.3 Stress

**How measured:**  
A crew member voluntarily reports perceived stress using a rating scale from 1 to 5.

**Why it matters:**  
Long missions involve demanding tasks, environmental constraints, isolation, and communication delays. Self-reported stress can help crews recognize changes in their own experiences.

**Limitations:**
- Stress ratings depend on personal perception.
- A rating does not identify the cause of stress.
- A simple scale is not a clinical assessment.
- Crew Vitals does not diagnose stress-related disorders.

### 2.4 Resting heart rate

**How measured:**  
Resting heart rate can be recorded using a wearable optical sensor, chest-strap monitor, or an approved manual pulse measurement method.

The measurement should include relevant context, such as the time of measurement, activity beforehand, and device used.

**Why it matters:**  
The cardiovascular system adapts to microgravity. Changes in fluid distribution and cardiovascular conditioning are important areas of human spaceflight research.

**Limitations:**
- Movement, sensor placement, and device quality can affect readings.
- Exercise, sleep, hydration, and other factors influence heart rate.
- A resting heart-rate value alone cannot diagnose a cardiovascular condition.
- Crew Vitals does not establish a medical alert threshold.

### 2.5 Systolic blood pressure

**How measured:**  
Blood pressure can be recorded using an approved automated blood-pressure monitor. The systolic value represents pressure in the arteries when the heart contracts.

Measurements should follow the applicable device and mission procedures.

**Why it matters:**  
Fluid shifts and cardiovascular adaptation during spaceflight can influence blood-pressure regulation. Monitoring provides information for understanding cardiovascular changes.

**Limitations:**
- Blood pressure varies with posture, activity, stress, and measurement conditions.
- Device accuracy and correct cuff placement matter.
- One reading cannot establish a medical condition.
- Crew Vitals does not recommend treatment based on an isolated reading.

### 2.6 Diastolic blood pressure

**How measured:**  
The diastolic value is recorded using the same approved blood-pressure measurement procedure. It represents arterial pressure when the heart relaxes between contractions.

**Why it matters:**  
Together with systolic pressure, diastolic pressure helps describe cardiovascular function and changes in blood-pressure regulation.

**Limitations:**
- Readings can vary between measurements.
- Measurement conditions and equipment influence accuracy.
- Diastolic pressure must be interpreted with appropriate clinical context.
- Crew Vitals does not independently classify a reading as medically normal or abnormal.

### 2.7 Blood glucose

**How measured:**  
Blood glucose can be measured using an approved blood-glucose meter and an appropriate blood sample. The record should indicate whether the measurement was fasting or non-fasting.

**Why it matters:**  
Glucose is an important source of energy. Metabolism, nutrition, physical activity, and stress are relevant to maintaining health during spaceflight.

**Limitations:**
- Results depend on sampling conditions and device accuracy.
- Fasting and non-fasting measurements are not directly interchangeable.
- A single reading cannot diagnose diabetes or another metabolic condition.
- Crew Vitals does not apply unvalidated glucose alert limits or provide treatment instructions.

### 2.8 Body temperature

**How measured:**  
Body temperature can be recorded using an approved thermometer. The measurement method, such as oral or forehead measurement, should be documented.

**Why it matters:**  
Body temperature is one observation used when monitoring general health. It may be relevant when evaluating possible changes in health during a mission.

**Limitations:**
- Different measurement methods can produce different readings.
- Environmental conditions and measurement technique can affect results.
- Temperature alone cannot identify the cause of an illness.
- Crew Vitals does not independently diagnose infection or prescribe treatment.

### 2.9 Daily radiation badge dose

**How measured:**  
A personal radiation dosimeter, when provided and used under mission procedures, can record radiation exposure information for its wearer. The recorded value, instrument, units, and measurement period must be documented.

**Why it matters:**  
Space radiation is a significant human spaceflight hazard. Monitoring radiation exposure helps support radiation research and mission safety procedures.

**Limitations:**
- A personal dosimeter reading is not automatically equivalent to effective dose or biological risk.
- Instrument type, calibration, location, and radiation characteristics matter.
- Historical NASA environmental instrument readings are not the same as an individual crew member's badge reading.
- Radiation safety decisions must follow authorized mission procedures.
- Crew Vitals does not issue radiation shelter instructions or calculate personal cancer risk from a raw reading.

### 2.10 Exercise minutes

**How measured:**  
Exercise duration can be recorded using exercise-equipment logs, wearable activity devices, or crew-entered records. Aerobic and resistive exercise should be distinguished when the available data permits.

**Why it matters:**  
Microgravity reduces normal mechanical loading on bones and muscles. Exercise is an important countermeasure used in human spaceflight to support physical conditioning.

**Limitations:**
- Exercise duration does not establish exercise intensity.
- Logged minutes do not directly measure muscle strength or bone density.
- Equipment and activity type affect the interpretation of results.
- Exercise records alone cannot establish whether a countermeasure is effective for an individual.

## 3. Data provenance and interpretation

Every observation should retain its source and measurement context.

The project uses the following provenance categories:

| Provenance | Meaning |
|---|---|
| nasa_measured | Observation from an identified NASA measurement source |
| analog_measured | Observation from a ground-based spaceflight analog study |
| external_earth | Observation from an external Earth-based dataset |
| manually_entered | Value entered manually |
| crew_self_report | Value reported by a crew member |
| simulated | Fictional value created for demonstration or testing |

A measurement must never be labelled NASA-measured unless its source and provenance have been verified.

Different subjects, missions, studies, instruments, and locations must not be combined as though they represent one astronaut or one continuous measurement history.

## 4. How Crew Vitals uses measurements

Crew Vitals uses observations to support:

1. Personal trend visualization over time.
2. Comparison with an individual's available historical baseline.
3. Identification of missing, incomplete, or potentially unusual observations.
4. Display of relevant NASA research and hazard information.
5. Human review of observations with their original source and limitations.

A statistical trend or review status is not a clinical threshold. Missing information must remain unknown rather than being interpreted as a healthy result.

## 5. Scientific and safety boundaries

Crew Vitals is a decision-support prototype, not a medical diagnostic system.

It does not:

- Diagnose diseases or mental-health conditions.
- Predict medical emergencies or fitness for duty.
- Replace astronauts' medical teams or mission procedures.
- Prescribe medication, diet changes, exercise changes, or medical treatment.
- Treat simulated values as actual NASA observations.
- Infer individual radiation exposure from unrelated environmental datasets.

Any health concern must be handled through authorized crew medical and mission procedures.

## 6. Reference sources

- C01 — NASA Human Research Program: Risks of Human Spaceflight  
  https://www.nasa.gov/hrp/risks/

- C02 — NASA Human Research Program: Five Hazards of Human Spaceflight  
  https://www.nasa.gov/hrp/hazards/

- C03 — NASA Human Research Program: Ongoing Research  
  https://www.nasa.gov/hrp/ongoing-hrp-research/

- C04 — Canadian Space Agency: Monitoring Radiation for Astronaut Health  
  https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp

- C05 — Canadian Space Agency: Why Conduct Science in Space?  
  https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp

- D01 — NASA OSDR Environmental Data Application  
  https://visualization.osdr.nasa.gov/eda/

- D02 — NASA OSDR Radiation Laboratory  
  https://visualization.osdr.nasa.gov/radlab/gui/overview/

- D03 — NASA Life Sciences Data Archive: UTMB Bed Rest Actigraphy  
  https://nlsp.nasa.gov/search/data/details/e26501eb-7d7a-5012-8c8e-c5bdb3eecaf6?dataType=DATASETS

**Source limitation:** These references provide research context or access to measurement datasets. Their inclusion does not establish that every indicator is currently measured continuously aboard a spacecraft or that every dataset has been downloaded and validated for this prototype.
