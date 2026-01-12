# orchestrator/dagster_project/quality/ge_asset.py
from __future__ import annotations

import great_expectations as gx
from great_expectations.data_context import AbstractDataContext

DATASOURCE_NAME = "local_filesystem"
ASSET_NAME = "silver_measurements_parquet"
BATCH_DEF_NAME = "silver_measurements_daily"

# Arquivos salvos como:
# silver/measurements/dt=2026-01-10/measurements.parquet
DAILY_PATH_REGEX = (
    r"silver/measurements/dt="
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"/measurements\.parquet"
)


def ensure_silver_measurements_asset(context: AbstractDataContext) -> None:
    """
    Garante que existe um File Data Asset (parquet) compatível com
    PandasFilesystemDatasource.
    """
    ds = context.data_sources.get(DATASOURCE_NAME)

    # Asset (File Data Asset)
    try:
        ds.get_asset(ASSET_NAME)
    except Exception:
        ds.add_parquet_asset(name=ASSET_NAME)
