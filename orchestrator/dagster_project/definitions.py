from dagster import (
    AssetSelection,
    Definitions,
    build_schedule_from_partitioned_job,
    define_asset_job,
    load_assets_from_modules,
)

from orchestrator.dagster_project import resources
from orchestrator.dagster_project.assets import (bronze_assets, silver_assets,
                                                 gold_scorecard_assets, warehouse_refresh,
                                                 quality_assets)


all_assets = load_assets_from_modules(
    [bronze_assets, silver_assets, gold_scorecard_assets, warehouse_refresh, quality_assets]
)

daily_pipeline_job = define_asset_job(
    name="daily_pipeline_job",
    selection=AssetSelection.keys(
        "bronze_mock_measurements_raw",
        "silver_measurements",
        "quality_silver_measurements_ge",
        "gold_data_quality_scorecard",
        "warehouse_duckdb_refresh",
    ),
)

daily_pipeline_schedule = build_schedule_from_partitioned_job(
    job=daily_pipeline_job,
    name="daily_pipeline_schedule",
)

defs = Definitions(
    assets=all_assets,
    resources={
        "storage": resources.storage_client_resource,
    },
    jobs=[daily_pipeline_job],
    schedules=[daily_pipeline_schedule],
)
