"""Pytest configuration"""

import sys
from pathlib import Path


THIS_DIR = Path(__file__).parent
TESTS_DIR_PARENT = (THIS_DIR / "..").resolve()

# ensure that `from tests ...` import statements work within the tests/ dir
sys.path.insert(0, str(TESTS_DIR_PARENT))
