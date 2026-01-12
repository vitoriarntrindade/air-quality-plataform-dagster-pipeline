from __future__ import annotations

from pathlib import Path
import great_expectations as gx

GE_ROOT = Path("data/ge/great_expectations").resolve()


def get_context() -> gx.DataContext:
    GE_ROOT.mkdir(parents=True, exist_ok=True)
    return gx.get_context(context_root_dir=str(GE_ROOT))
