"""Compatibility CLI for the standalone research prototype.

Production implementation: backend.app.adapters.nlsp_preview
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.adapters.nlsp_preview import *


if __name__ == "__main__":
    main()
