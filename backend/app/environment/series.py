"""Common environment series wrappers

Owner: Member 4 (Environment & Radiation)
"""

from typing import Dict, Any
from app.environment.osdr_eda import get_environment_series as get_eda_series


def get_environment_series() -> Dict[str, Any]:
    """Return the primary NASA RR-1 EDA environment series."""
    return get_eda_series()
