SHELL := /bin/bash

PYTHON ?= python
DAGSTER_HOME ?= $(PWD)
DAGSTER_PORT ?= 3001

.PHONY: help venv install lint fmt dagster-ui job-daily asset-bronze asset-silver asset-quality asset-gold asset-warehouse clean-data clean-ge openaq-env up down build logs

help:
	@echo "Targets:"
	@echo "  venv           Create virtualenv (.venv)"
	@echo "  install        Install dependencies via uv"
	@echo "  lint           Run ruff (if available)"
	@echo "  fmt            Format via ruff (if available)"
	@echo "  dagster-ui     Start Dagster UI"
	@echo "  up             Start Metabase via Docker Compose"
	@echo "  down           Stop Metabase"
	@echo "  build          Build Metabase image"
	@echo "  logs           Follow Metabase logs"
	@echo "  job-daily      Run daily_pipeline_job for a date"
	@echo "  asset-bronze   Materialize bronze asset for a date"
	@echo "  asset-silver   Materialize silver asset for a date"
	@echo "  asset-quality  Materialize quality asset for a date"
	@echo "  asset-gold     Materialize gold asset for a date"
	@echo "  asset-warehouse Materialize warehouse refresh"
	@echo "  openaq-env     Example env vars for OpenAQ"
	@echo "  clean-data     Remove generated data files"
	@echo "  clean-ge       Remove GE results/docs"

venv:
	@$(PYTHON) -m venv .venv
	@echo "Activate with: source .venv/bin/activate"

install:
	@uv sync

lint:
	@ruff check . || echo "ruff not installed"

fmt:
	@ruff format . || echo "ruff not installed"

dagster-ui:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster dev -f orchestrator/dagster_project/definitions.py -p $(DAGSTER_PORT)

up:
	@docker compose up -d

down:
	@docker compose down

build:
	@docker compose build

logs:
	@docker compose logs -f

job-daily:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster job execute -f orchestrator/dagster_project/definitions.py -j daily_pipeline_job -p '{"date": "$(DATE)"}'

asset-bronze:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster asset materialize -f orchestrator/dagster_project/definitions.py -a bronze_mock_measurements_raw -p '{"date": "$(DATE)"}'

asset-silver:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster asset materialize -f orchestrator/dagster_project/definitions.py -a silver_measurements -p '{"date": "$(DATE)"}'

asset-quality:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster asset materialize -f orchestrator/dagster_project/definitions.py -a quality_silver_measurements_ge -p '{"date": "$(DATE)"}'

asset-gold:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster asset materialize -f orchestrator/dagster_project/definitions.py -a gold_data_quality_scorecard -p '{"date": "$(DATE)"}'

asset-warehouse:
	@DAGSTER_HOME=$(DAGSTER_HOME) dagster asset materialize -f orchestrator/dagster_project/definitions.py -a warehouse_duckdb_refresh

openaq-env:
	@echo "BRONZE_SOURCE=openaq"
	@echo "OPENAQ_API_KEY=***"
	@echo "OPENAQ_PARAMETERS=pm25,pm10,no2,o3"
	@echo "OPENAQ_LIMIT=500"
	@echo "AIR_QUALITY_CITY=São Paulo"
	@echo "AIR_QUALITY_COUNTRY=BR"

clean-data:
	@rm -rf data/bronze data/silver data/gold data/warehouse.duckdb

clean-ge:
	@rm -rf data/ge/results data/ge/great_expectations/uncommitted
