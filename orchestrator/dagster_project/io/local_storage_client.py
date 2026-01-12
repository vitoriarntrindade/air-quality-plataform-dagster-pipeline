from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from orchestrator.dagster_project.io.storage_client import StorageClient


class LocalStorageClient(StorageClient):
    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path)

    def _full_path(self, relative_path: str) -> Path:
        return self.base_path / relative_path

    def mkdirs(self, path: str) -> None:
        self._full_path(path).mkdir(parents=True, exist_ok=True)

    def write_json(self, path: str, data: Dict[str, Any]) -> None:
        full_path = self._full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def read_json(self, path: str) -> Dict[str, Any]:
        full_path = self._full_path(path)
        return json.loads(full_path.read_text(encoding="utf-8"))

    def exists(self, path: str) -> bool:
        return self._full_path(path).exists()

    def list(self, prefix: str) -> List[str]:
        root = self._full_path(prefix)
        if not root.exists():
            return []
        return [str(p.relative_to(self.base_path)) for p in root.rglob("*") if p.is_file()]
