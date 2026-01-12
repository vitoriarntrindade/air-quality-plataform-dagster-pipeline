from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd


def build_scorecard_rows(validation_json: Dict[str, Any], dt: str, dataset: str) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    results = validation_json.get("results", [])
    run_id = (validation_json.get("dagster") or {}).get("run_id")

    for item in results:
        exp_cfg = item.get("expectation_config", {})
        exp_type = exp_cfg.get("expectation_type")
        kwargs = exp_cfg.get("kwargs", {}) or {}
        meta = exp_cfg.get("meta", {}) or {}

        res = item.get("result", {}) or {}

        rows.append(
            {
                "dt": dt,
                "dataset": dataset,
                "suite_name": validation_json.get("expectation_suite_name"),
                "expectation_type": exp_type,
                "severity": meta.get("severity", "unknown"),
                "success": item.get("success"),
                "column": kwargs.get("column"),
                "column_list": kwargs.get("column_list"),
                "unexpected_count": res.get("unexpected_count"),
                "unexpected_percent": res.get("unexpected_percent"),
                "element_count": res.get("element_count"),
                "run_id": run_id,
                "validated_at_utc": (validation_json.get("dagster") or {}).get("validated_at_utc")
                or datetime.now(timezone.utc).isoformat(),
            }
        )

    return pd.DataFrame(rows)
