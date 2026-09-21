import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

for p in (str(HERE), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)
