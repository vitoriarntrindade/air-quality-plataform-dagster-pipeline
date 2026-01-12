from __future__ import annotations

from dagster import asset

from orchestrator.dagster_project.warehouse.duckdb_warehouse import DuckDBWarehouse


@asset(deps=["gold_data_quality_scorecard"], group_name="warehouse")
def warehouse_duckdb_refresh(context) -> None:
    DuckDBWarehouse().upsert_views()
    context.add_output_metadata({"db_path": "data/warehouse.duckdb"})
