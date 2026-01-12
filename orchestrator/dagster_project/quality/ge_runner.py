from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import great_expectations as gx

from orchestrator.dagster_project.quality.ge_bootstrap import ensure_context
from orchestrator.dagster_project.quality.ge_suites import (
    SUITE_SILVER_MEASUREMENTS,
    ensure_silver_measurements_suite,
)


def validate_silver_measurements_parquet(parquet_abs_path: str) -> Dict[str, Any]:
    """
    Valida um parquet Silver usando Great Expectations (Data Context + Suite),
    alimentando o Validator via batch_data (pandas DataFrame).

    Isso evita dependência de datasource/connector (que muda bastante no GE 1.x).
    """
    context = ensure_context()
    ensure_silver_measurements_suite(context)

    df = pd.read_parquet(parquet_abs_path)

    validator = context.get_validator(
        batch_data=df,
        expectation_suite_name=SUITE_SILVER_MEASUREMENTS,
    )

    result = validator.validate()
    return result.to_json_dict()
