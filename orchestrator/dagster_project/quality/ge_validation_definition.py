from __future__ import annotations

import great_expectations as gx

from orchestrator.dagster_project.quality.ge_asset import (
    DATASOURCE_NAME,
    ASSET_NAME,
    BATCH_DEF_NAME,
)
from orchestrator.dagster_project.quality.ge_suites import SUITE_NAME

VALIDATION_NAME = "validate_silver_measurements_daily"


def ensure_validation_definition(context: gx.DataContext) -> gx.ValidationDefinition:
    # Se já existe, retorna
    try:
        return context.validation_definitions.get(VALIDATION_NAME)
    except Exception:
        pass

    suite = context.suites.get(SUITE_NAME)
    batch_def = (
        context.data_sources
        .get(DATASOURCE_NAME)
        .get_asset(ASSET_NAME)
        .get_batch_definition(BATCH_DEF_NAME)
    )

    validation = gx.ValidationDefinition(
        name=VALIDATION_NAME,
        data=batch_def,
        suite=suite,
    )

    context.validation_definitions.add(validation)
    return validation
