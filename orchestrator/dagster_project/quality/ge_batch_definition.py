from __future__ import annotations
import great_expectations as gx

from orchestrator.dagster_project.quality.ge_asset import (
    DATASOURCE_NAME,
    ASSET_NAME,
    BATCH_DEF_NAME,
    DAILY_PATH_REGEX,
)


def ensure_daily_batch_definition(context: gx.DataContext) -> None:
    asset = (
        context.data_sources
        .get(DATASOURCE_NAME)
        .get_asset(ASSET_NAME)
    )

    try:
        asset.get_batch_definition(BATCH_DEF_NAME)
        return
    except Exception:
        pass

    asset.add_batch_definition_daily(
        name=BATCH_DEF_NAME,
        regex=DAILY_PATH_REGEX,
        sort_ascending=True,
    )
