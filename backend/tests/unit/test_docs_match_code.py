"""docs/thresholds.md must state the same numbers the analytics code uses.

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import re

from backend.app.analytics import baseline
from backend.app.config import REPO_ROOT


def test_threshold_block_in_docs_matches_the_code():
    text = (REPO_ROOT / "docs" / "thresholds.md").read_text(encoding="utf-8")
    block = re.search(r"```\n(MIN_REFERENCE.*?)```", text, re.S).group(1)
    documented = {k: float(v) for k, v in re.findall(r"^(\w+) = ([\d.]+)$", block, re.M)}
    assert documented == {
        "MIN_REFERENCE": float(baseline.MIN_REFERENCE),
        "PERSISTENCE_COUNT": float(baseline.PERSISTENCE_COUNT),
        "DEMO_Z_THRESHOLD": float(baseline.DEMO_Z_THRESHOLD),
    }


def test_every_measurement_the_code_accepts_is_documented():
    text = (REPO_ROOT / "docs" / "thresholds.md").read_text(encoding="utf-8")
    missing = [n for n in baseline.MEASUREMENT_RULES if n.replace("_bp", "") not in text and n not in text]
    assert not missing, f"missing from docs/thresholds.md: {missing}"
