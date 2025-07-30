import sys
from pathlib import Path

# Ensure project root is on sys.path for tests
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Also add the `src` directory for projects using a src-layout
SRC_DIR = ROOT_DIR / "src"
if SRC_DIR.is_dir() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
