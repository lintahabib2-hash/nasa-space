import math
from typing import Optional

import pytest

from app.environment.osdr_eda import parse_co2_value
from app.environment.series import get_environment_series


def test_environment_series_has_m3_co2_structure_and_300_points() -> None:
    environment = get_environment_series()

    assert environment["source_id"] == "NASA_OSDR_EDA_RR1"
    assert len(environment["series"]) == 1

    co2_series = environment["series"][0]
    assert co2_series["measurement"] == "co2_iss"
    assert co2_series["label"] == "CO2 (ISS)"
    assert co2_series["units"] == "ppm"

    points = co2_series["points"]
    assert len(points) == 300
    timestamps = [point["timestamp_utc"] for point in points]
    assert timestamps == sorted(timestamps)
    assert timestamps[0] == environment["time_start_utc"]
    assert timestamps[-1] == environment["time_end_utc"]

    for point in points:
        value = point["value"]
        assert value is None or math.isfinite(value)
        assert point["quality_state"] == ("missing" if value is None else "valid")


@pytest.mark.parametrize("value", [None, "", " ", "NaN", "Infinity", "-Infinity"])
def test_missing_or_non_finite_co2_values_become_null(
    value: Optional[str],
) -> None:
    assert parse_co2_value(value) is None


def test_zero_co2_reading_is_not_treated_as_missing() -> None:
    assert parse_co2_value("0") == 0.0
