"""Compatibility CLI for the standalone research prototype.

Production implementation: backend.app.adapters.osd575_serum
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.adapters.osd575_serum import *


if __name__ == "__main__":
    main()
