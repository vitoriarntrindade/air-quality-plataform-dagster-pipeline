from __future__ import annotations

from typing import Any, Dict, List, Tuple

import polars as pl
from pydantic import ValidationError

from dagster import DailyPartitionsDefinition, asset

from orchestrator.dagster_project.contracts.silver_contracts import MeasurementRecord
from orchestrator.dagster_project.io.storage_client import StorageClient


daily_partitions = DailyPartitionsDefinition(start_date="2026-01-01")


def _partition_dt(context) -> str:
    return context.partition_key


def _bronze_path(dt: str) -> str:
    return f"bronze/measurements/dt={dt}/measurements.json"


def _silver_path(dt: str) -> str:
    return f"silver/measurements/dt={dt}/measurements.parquet"


@asset(
    partitions_def=daily_partitions,
    required_resource_keys={"storage"},
    group_name="silver",
)
def silver_measurements(context) -> Dict[str, Any]:
    storage: StorageClient = context.resources.storage
    dt = _partition_dt(context)

    bronze_path = _bronze_path(dt)
    if not storage.exists(bronze_path):
        raise FileNotFoundError(f"Bronze não encontrado para dt={dt}: {bronze_path}")

    raw = storage.read_json(bronze_path)
    raw_results = raw.get("results", [])

    valid_rows: List[dict] = []
    invalid_count = 0
    invalid_examples: List[str] = []

    for item in raw_results:
        try:
            rec = MeasurementRecord.model_validate(item)
            valid_rows.append(
                {
                    "location_id": rec.location_id,
                    "city": rec.city,
                    "country": rec.country,
                    "parameter": rec.parameter,
                    "value": rec.value,
                    "unit": rec.unit,
                    "datetime": rec.datetime,
                    "dt": dt,  # útil pro staging depois
                }
            )
        except ValidationError as exc:
            invalid_count += 1
            if len(invalid_examples) < 3:
                invalid_examples.append(str(exc))

    df = pl.DataFrame(valid_rows) if valid_rows else pl.DataFrame(
        schema={
            "location_id": pl.Int64,
            "city": pl.Utf8,
            "country": pl.Utf8,
            "parameter": pl.Utf8,
            "value": pl.Float64,
            "unit": pl.Utf8,
            "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
            "dt": pl.Utf8,
        }
    )

    # Garantir timezone UTC (se vier sem tz, a gente seta como UTC de forma pragmática)
    if df.height > 0:
        df = df.with_columns(
            pl.col("datetime")
            .cast(pl.Datetime(time_unit="us", time_zone="UTC"), strict=False)
        )

    # Dedup: location_id + parameter + datetime
    before_dedup = df.height
    if df.height > 0:
        df = df.unique(subset=["location_id", "parameter", "datetime"], keep="first")
    after_dedup = df.height

    # Persistir Parquet
    silver_path = _silver_path(dt)
    full_path = f"./data/{silver_path}"
    # garante pasta existir pelo storage client
    storage.mkdirs(f"silver/measurements/dt={dt}")

    df.write_parquet(full_path)

    context.add_output_metadata(
        {
            "dt": dt,
            "bronze_path": bronze_path,
            "silver_path": silver_path,
            "raw_count": len(raw_results),
            "valid_count": before_dedup,
            "invalid_count": invalid_count,
            "dedup_removed": max(0, before_dedup - after_dedup),
            "final_count": after_dedup,
            "invalid_examples": invalid_examples,
        }
    )

    return {
        "dt": dt,
        "silver_path": silver_path,
        "final_count": after_dedup,
        "invalid_count": invalid_count,
    }
