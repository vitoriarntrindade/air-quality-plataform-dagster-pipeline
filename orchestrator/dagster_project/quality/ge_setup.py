from __future__ import annotations

import great_expectations as gx

from orchestrator.dagster_project.quality.ge_bootstrap import get_context
from orchestrator.dagster_project.quality.ge_datasource import ensure_local_filesystem_datasource
from orchestrator.dagster_project.quality.ge_asset import ensure_silver_measurements_asset
from orchestrator.dagster_project.quality.ge_batch_definition import ensure_daily_batch_definition
from orchestrator.dagster_project.quality.ge_suites import ensure_silver_measurements_suite, SUITE_NAME
from orchestrator.dagster_project.quality.ge_validation_definition import ensure_validation_definition


def setup_all() -> tuple[gx.DataContext, gx.ValidationDefinition]:
    context = get_context()
    ensure_local_filesystem_datasource(context)
    ensure_silver_measurements_asset(context)
    ensure_daily_batch_definition(context)
    ensure_silver_measurements_suite(context)
    vd = ensure_validation_definition(context)
    return context, vd
