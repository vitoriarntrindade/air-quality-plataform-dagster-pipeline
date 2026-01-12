from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from dagster import DailyPartitionsDefinition, asset

from orchestrator.dagster_project.io.storage_client import StorageClient


daily_partitions = DailyPartitionsDefinition(start_date="2026-01-01")


def _partition_dt(context) -> str:
    return context.partition_key


@asset(
    partitions_def=daily_partitions,
    required_resource_keys={"storage"},
    group_name="bronze",
)
def bronze_mock_measurements_raw(context) -> Dict[str, Any]:
    storage: StorageClient = context.resources.storage
    dt = _partition_dt(context)

    payload = {
        "meta": {
            "source": "mock",
            "dt": dt,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "results": [
            {
                "locationId": 123,
                "city": "São Paulo",
                "country": "BR",
                "parameter": "pm25",
                "value": 12.3,
                "unit": "µg/m³",
                "datetime": f"{dt}T12:00:00+00:00",
            }
        ],
    }

    path = f"bronze/measurements/dt={dt}/measurements.json"

    if storage.exists(path):
        context.log.warning("Bronze já existe para dt=%s em %s. Mantendo arquivo.", dt, path)
        return {"path": path, "skipped": True}

    storage.write_json(path, payload)

    context.add_output_metadata(
        {
            "dt": dt,
            "storage_path": path,
            "record_count": len(payload.get("results", [])),
            "source": "mock",
        }
    )
    return {"path": path, "skipped": False}
