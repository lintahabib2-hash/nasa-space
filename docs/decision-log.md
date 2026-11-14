
# Project Decision Log

> Owner: Member 1 (Coordination, Science, Pitch)
>
> Purpose: Record important scientific, technical, data and project-scope decisions for CREW VITALS.

## 1. Confirmed Project Decisions

| ID | Decision | Reason | Status |
|---|---|---|---|
| DEC-01 | Build CREW VITALS as an astronaut health-monitoring prototype. | Focus on health-related check-ins, personal trends and spaceflight risk awareness. | Agreed project direction |
| DEC-02 | Clearly distinguish NASA-measured, analog-measured, external, simulated and manually entered data. | Prevent incorrect claims about data origin. | Required |
| DEC-03 | Use simulated crew records for daily check-in demonstrations when real astronaut records are unavailable. | Demonstrate the application without inventing NASA observations. | Agreed |
| DEC-04 | Keep historical NASA environmental or radiation observations separate from simulated personal health records. | These sources represent different measurements and contexts. | Required |
| DEC-05 | Do not join different populations, missions or locations using timestamp alone. | Prevent misleading comparisons between unrelated datasets. | Required |
| DEC-06 | Provide trends and review-only information rather than medical diagnoses. | The prototype has no established clinical validation. | Required |
| DEC-07 | Prioritize an offline-capable check-in and evidence experience. | Connectivity may be limited during exploration missions. | Implementation to verify |
| DEC-08 | Display source information and limitations through an Evidence Drawer or equivalent interface. | Make the scientific basis of displayed information transparent. | Implementation to verify |

## 2. Data and Scientific Decisions

| ID | Decision | Reason |
|---|---|---|
| DATA-01 | NASA HRP challenge resources C01–C05 provide health-risk and research context. | They are not automatically downloadable longitudinal vital-sign datasets. |
| DATA-02 | NASA OSDR EDA (D01) is a candidate source for historical environmental observations. | Actual export and measurement context must be verified. |
| DATA-03 | NASA RadLab (D02) is a candidate source for historical radiation instrument observations. | Instrument readings must not be presented as individual biological risk. |
| DATA-04 | NASA NLSP bed-rest actigraphy (D03) is an analog research source. | Ground-based bed-rest measurements are not spaceflight astronaut observations. |
| DATA-05 | External Earth datasets must remain separate from NASA and astronaut data. | They may support independent method testing only. |
| DATA-06 | Specialized biomarkers and clinical measurements are outside the initial prototype unless verified and justified. | Avoid unsupported medical interpretation and unnecessary complexity. |

## 3. Open Questions Requiring Confirmation

| ID | Question | Responsible person | Status |
|---|---|---|---|
| OPEN-01 | Does the organizer accept NASA HRP risk resources together with independently retrieved NASA OSDR measurements as qualifying NASA data for Global Awards? | Member 1 | Awaiting organizer confirmation |
| OPEN-02 | Which NASA environmental dataset and mission will the team successfully retrieve and use? | Member 4 / Member 6 | To verify |
| OPEN-03 | Can the team retrieve and inspect a usable NASA RadLab export? | Member 4 / Member 6 | To verify |
| OPEN-04 | Which indicators are actually implemented in the final application? | Member 1 / Member 2 / Member 3 | To confirm |
| OPEN-05 | Does offline mode work for check-ins and previously available evidence? | Member 3 / Member 6 | Requires testing |
| OPEN-06 | Are all displayed source labels, units, timestamps and limitations visible in the final interface? | Member 1 / Member 6 | Requires review |

## 4. Decisions That Must Not Be Assumed

1. Do not assume that a dataset is downloaded because its website or catalog entry is available.
2. Do not assume that a NASA-related research page satisfies the challenge's specific NASA-data eligibility requirement.
3. Do not assume that historical environmental observations represent live spacecraft conditions.
4. Do not assume that simulated crew records represent actual astronauts.
5. Do not assume that a prototype trend is a validated clinical warning.
6. Do not claim that offline operation works until it has been tested.

## 5. Change History

| Date | Change |
|---|---|
| 2026-11-13 | Reviewed the comprehensive astronaut health data and resource audit. |
| 2026-11-14 | Prepared initial project, scientific and data-provenance decisions. |
| 2026-11-14 | Created and validated `shared/knowledge/knowledge.json` and `shared/knowledge/source-registry.json` as Member 1 shared knowledge deliverables. |
| 2026-11-14 | Connected the shared knowledge JSON to the frontend through `dataSource.ts`; production build passed using `npm.cmd run build`. |
| 2026-11-14 | Ran frontend tests: 38/42 passed. Three failures relate to unavailable localStorage in the test environment; one concerns the expected "Mars transit" label versus the current "Mars mission" wording. Referred for team review. |


> Review note: Update this document whenever the team confirms an open question or changes the project scope. Record the actual decision and date rather than assuming confirmation.
