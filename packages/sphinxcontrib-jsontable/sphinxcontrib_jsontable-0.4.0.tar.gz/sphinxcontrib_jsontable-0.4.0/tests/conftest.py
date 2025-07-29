import sys
from pathlib import Path

ROOT = str(Path(__file__).parent.parent.resolve())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
