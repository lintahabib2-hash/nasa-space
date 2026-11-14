"""Compatibility layer for the standalone offline prototype."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.analytics.baseline import (
    MIN_REFERENCE,
    PERSISTENCE_COUNT,
    DEMO_Z_THRESHOLD,
    REQUIRED,
    SERIES_ID,
    timestamp,
    validated,
    get_observations,
    get_baseline_result,
)
