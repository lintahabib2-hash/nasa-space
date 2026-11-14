# CFT70 source-preserving research integration

**Status:** descriptive research only; no clinical prediction or astronaut diagnosis.

## Real archived files
- `MR016G_CFT70_DAILY_INTAKE/MR016G_CFT70_DAILY_INTAKE` within the NASA MR016G archive:
  1,388 recorded daily energy-intake rows, 14 people; unit **kcal/day**.
- `BRSMCF_CFT70/BRSMCF_CFT70_2D_Echo_All` within the BRSMCF archive:
  184 examinations, 37 people, **one PRE_TEST exam per person**.
- `BRSMCF_CFT70/BRSMCF_CFT70_3D_Echo_All`:
  510 analyst-records, 37 people; repeated analyzers at the same phase/day
  **must not** be treated as independent historical days.
- The 2D seven-participant file is a subset, **not new people or extra sessions**.
- Both archives contain **other campaigns**; the implementation only reads
  the explicitly named CFT70 members.

## Reference method
For each distinct `Subject`, use only numeric-label `PRE_TEST` intake rows,
requiring at least 5 records. Calculate median and median absolute deviation
(MAD) separately for each subject. Preserve unusual `X1`/`X2` records with
their source labels, but **exclude them from numeric pre-reference** until their
semantics are established. Compare `IN_TEST` and `POST_TEST` intake against
the frozen pre-test median, in **kcal/day**. Do not insert synthetic timestamps.

This is a descriptive comparison of daily diet, not a medical alert. CFT70
dietary intake was standardized and adjusted as part of study procedures;
changes may reflect the protocol and energy requirements, not deterioration.
Do not call it a cardiovascular baseline or assume individual astronaut data.

## Source URLs
- MR016G clinical nutritional assessment:
  https://nlsp.nasa.gov/search/data/details/72616c68-3046-5d36-8f1d-a26d856107ff?dataType=EXPERIMENTS
- BRSMCF cardiovascular function:
  https://nlsp.nasa.gov/search/data/details/9af6f9ba-3730-54ab-a82a-1a32798667ae?dataType=EXPERIMENTS

## Command
From `nasa-space` root:

```bash
python member2/cft70_research.py \
  --intake-archive ../member2/data/raw/cft70_mr016g/MR016G_1794654792388.zip \
  --echo-archive ../member2/data/raw/cft70_brsmcf/BRSMCF_1794654583920.zip \
  --out ../member2/reports/cft70_research.json

python -m unittest discover -s member2/tests -v
```

**Keep source archives and generated JSON outside git** pending specific
redistribution review. Exported research information is not live telemetry.
The program is offline once both source archives have been downloaded.

## Integration
Use `nutrition.participants[].observations[]` only for the nutrition-research
view. `cardiovascular_coverage` is an eligibility/quality audit, not an
independent cardiovascular diagnosis. The program reports overlapping
participant identifiers but does not merge the two experimental tables.
