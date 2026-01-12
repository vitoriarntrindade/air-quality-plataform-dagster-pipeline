#!/usr/bin/env python3
"""
Script para atualizar views do DuckDB.
Deve ser executado de dentro do container Docker ou ajustado para paths locais.
"""
import duckdb
from pathlib import Path

# Path do DuckDB (dentro do Docker é /data/warehouse.duckdb)
DB_PATH = "/data/warehouse.duckdb"

# Patterns para os arquivos
SCORECARD_PATTERN = "/data/gold/scorecards/data_quality/*/scorecard.parquet"
GE_RESULTS_PATTERN = "/data/ge/results/silver_measurements/*/validation_result.json"

def main():
    print(f"Conectando ao DuckDB em: {DB_PATH}")
    conn = duckdb.connect(DB_PATH)
    
    try:
        print("Criando view: gold_data_quality_scorecard")
        conn.execute(f"""
            CREATE OR REPLACE VIEW gold_data_quality_scorecard AS
            SELECT * FROM read_parquet('{SCORECARD_PATTERN}');
        """)
        
        print("Criando view: ge_validation_results")
        conn.execute(f"""
            CREATE OR REPLACE VIEW ge_validation_results AS
            SELECT * FROM read_json_auto('{GE_RESULTS_PATTERN}');
        """)
        
        print("✓ Views criadas com sucesso!")
        
        # Verificar
        print("\nTabelas/Views disponíveis:")
        print(conn.execute("SHOW TABLES").fetchall())
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
