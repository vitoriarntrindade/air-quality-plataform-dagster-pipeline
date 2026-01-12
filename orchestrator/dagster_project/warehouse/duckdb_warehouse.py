from __future__ import annotations

from pathlib import Path
from typing import Optional

import duckdb

# Diretório base de dados (relativo à raiz do projeto)
DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class DuckDBWarehouse:
    def __init__(self, db_path: str | Path | None = None, use_docker_paths: bool = False) -> None:
        if db_path is None:
            db_path = DATA_DIR / "warehouse.duckdb"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.use_docker_paths = use_docker_paths

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    def upsert_views(self) -> None:
        """
        Cria views em cima de arquivos Parquet (Bronze/Silver/Gold).
        Como é view, Metabase enxerga "tabelas" sem você precisar carregar dados.
        
        Usa paths que funcionam tanto no host quanto no Docker (onde /data está montado).
        """
        con = self.connect()
        try:
            # Se use_docker_paths=True, usa /data (para Docker)
            # Senão, usa o diretório do warehouse.duckdb (para host)
            if self.use_docker_paths:
                base_path = "/data"
            else:
                base_path = str(self.db_path.parent.resolve())
            
            scorecard_pattern = f"{base_path}/gold/scorecards/data_quality/*/scorecard.parquet"
            ge_results_pattern = f"{base_path}/ge/results/silver_measurements/*/validation_result.json"

            # Se houve carga anterior como tabela, garantir troca para view.
            con.execute("DROP TABLE IF EXISTS gold_data_quality_scorecard;")
            con.execute("DROP TABLE IF EXISTS ge_validation_results;")

            con.execute(
                f"""
                CREATE OR REPLACE VIEW gold_data_quality_scorecard AS
                SELECT * FROM read_parquet('{scorecard_pattern}');
                """
            )
            con.execute(
                f"""
                CREATE OR REPLACE VIEW ge_validation_results AS
                SELECT * FROM read_json_auto('{ge_results_pattern}');
                """
            )
        finally:
            con.close()
