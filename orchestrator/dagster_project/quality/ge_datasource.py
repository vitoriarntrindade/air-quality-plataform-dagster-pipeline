from __future__ import annotations

from pathlib import Path
import great_expectations as gx

DATASOURCE_NAME = "local_filesystem"


def ensure_local_filesystem_datasource(context: gx.DataContext) -> None:
    """
    Garante que existe um PandasFilesystemDatasource apontando para ./data
    (compatível com GE 1.10).
    """
    try:
        context.data_sources.get(DATASOURCE_NAME)
        return
    except Exception:
        pass

    context.data_sources.add_pandas_filesystem(
        name=DATASOURCE_NAME,
        base_directory=str(Path("data").resolve()),
    )
