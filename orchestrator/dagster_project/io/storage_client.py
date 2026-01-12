from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StorageClient(ABC):
    @abstractmethod
    def write_json(self, path: str, data: Dict[str, Any]) -> None: ...

    @abstractmethod
    def read_json(self, path: str) -> Dict[str, Any]: ...

    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def list(self, prefix: str) -> List[str]: ...

    @abstractmethod
    def mkdirs(self, path: str) -> None: ...
