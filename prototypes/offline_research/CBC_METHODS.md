# OSD-569 Inspiration4 CBC: source-preserving descriptive comparisons

The adapter reads NASA OSD-569 **original submitted long-form CBC** measurements. It does not use the transformed file's potentially erroneous `hemoglobin_value_percent` field as a source of units: original submitted `HEMOGLOBIN` records state `g/dL`.

For each pseudonymized participant and each of five selected CBC measurements (hemoglobin, hematocrit, white blood cells, red blood cells, platelet count), a provisional median uses only three pre-flight measurements `L-92`, `L-44`, `L-3`, when all are available. Observed measurements at `R+1`, `R+45`, `R+82`, `R+194` are compared separately; the analysis never uses later readings to build the pre-flight reference.

Source measurements outside their **source-provided** ranges are preserved and flagged. In particular, C003 `L-92` platelet count `12.9 Thousand/uL` is present in the original file; the adapter does not silently replace it. Range flags indicate a source-data review need, **not clinical diagnosis**. Three widely separated pre-flight blood tests do not support a clinically validated personalized baseline.

The implementation uses synthetic unit-test fixtures to verify input validation, correct units, source anomalies, nonfinite rejection, duplicate rejection, missing pre-flight data, and future-leakage avoidance. No synthetic values are presented as NASA observations. Keep raw files and exported comparisons outside the public repository unless redistribution permission is confirmed.
