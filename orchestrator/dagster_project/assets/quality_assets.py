from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from dagster import DailyPartitionsDefinition, asset

from orchestrator.dagster_project.quality.ge_setup import setup_all  # seu setup_all idempotente


daily_partitions = DailyPartitionsDefinition(start_date="2026-01-01")


def _split_dt(dt: str) -> Dict[str, str]:
    year, month, day = dt.split("-")
    return {"year": year, "month": month, "day": day}


@asset(
    partitions_def=daily_partitions,
    group_name="quality",
    deps=["silver_measurements"],
)
def quality_silver_measurements_ge(context) -> Dict[str, Any]:
    dt = context.partition_key

    _, vd = setup_all()
    result = vd.run(batch_parameters=_split_dt(dt))

    out_path = f"data/ge/results/silver_measurements/dt={dt}/validation_result.json"
    out_dir = out_path.rsplit("/", 1)[0]
    import os, json
    os.makedirs(out_dir, exist_ok=True)

    payload = result.to_json_dict()
    payload["dagster"] = {
        "run_id": context.run_id,
        "partition_key": dt,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    context.add_output_metadata({"dt": dt, "ge_success": payload.get("success"), "path": out_path})
    return {"dt": dt, "success": payload.get("success"), "path": out_path}
