"""Make the service modules importable in tests, and the repo's engine/ locally.

In production `engine/` is copied next to main.py by engine/export_web.py, so the
same `import engine.demo_index` works in both places.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

for p in (str(HERE), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)
