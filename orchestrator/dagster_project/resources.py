from __future__ import annotations

from dagster import resource
from orchestrator.dagster_project.io.local_storage_client import LocalStorageClient


@resource
def storage_client_resource(_context) -> LocalStorageClient:
    return LocalStorageClient(base_path="./data")
