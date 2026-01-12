from __future__ import annotations

import json
import os
from typing import Any, Dict

from dagster import DailyPartitionsDefinition, asset

from orchestrator.dagster_project.gold.scorecard_builder import build_scorecard_rows


daily_partitions = DailyPartitionsDefinition(start_date="2026-01-01")


@asset(
    partitions_def=daily_partitions,
    deps=["quality_silver_measurements_ge"],
    group_name="gold",
)
def gold_data_quality_scorecard(context) -> Dict[str, Any]:
    dt = context.partition_key
    src = f"data/ge/results/silver_measurements/dt={dt}/validation_result.json"

    with open(src, "r", encoding="utf-8") as f:
        validation_json = json.load(f)

    df = build_scorecard_rows(validation_json, dt=dt, dataset="silver.measurements")

    out_dir = f"data/gold/scorecards/data_quality/dt={dt}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/scorecard.parquet"
    df.to_parquet(out_path, index=False)

    context.add_output_metadata({"dt": dt, "rows": int(df.shape[0]), "path": out_path})
    return {"dt": dt, "rows": int(df.shape[0]), "path": out_path}
