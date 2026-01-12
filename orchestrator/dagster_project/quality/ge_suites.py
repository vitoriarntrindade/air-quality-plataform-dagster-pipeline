from __future__ import annotations

import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeBetween,
    ExpectCompoundColumnsToBeUnique,
)

SUITE_NAME = "silver.measurements"


def ensure_silver_measurements_suite(context: gx.DataContext) -> None:
    try:
        context.suites.get(name=SUITE_NAME)
        return
    except Exception:
        pass

    suite = ExpectationSuite(name=SUITE_NAME)

    suite.add_expectation(
        ExpectColumnValuesToNotBeNull(column="location_id")
    )
    suite.add_expectation(
        ExpectColumnValuesToNotBeNull(column="parameter")
    )
    suite.add_expectation(
        ExpectColumnValuesToNotBeNull(column="value")
    )
    suite.add_expectation(
        ExpectColumnValuesToBeBetween(column="value", min_value=0)
    )
    suite.add_expectation(
        ExpectCompoundColumnsToBeUnique(
            column_list=["location_id", "parameter", "datetime"]
        )
    )

    context.suites.add(suite)
