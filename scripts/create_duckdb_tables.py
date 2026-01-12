#!/usr/bin/env python3
"""
Script para criar TABELAS (não views) no DuckDB a partir dos arquivos Parquet.
Deve ser executado de dentro do container Docker.
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
        # Dropar tabelas antigas se existirem
        print("Removendo tabelas/views antigas...")
        conn.execute("DROP VIEW IF EXISTS gold_data_quality_scorecard")
        conn.execute("DROP TABLE IF EXISTS gold_data_quality_scorecard")
        conn.execute("DROP VIEW IF EXISTS ge_validation_results")
        conn.execute("DROP TABLE IF EXISTS ge_validation_results")
        
        # Criar TABELA (materializada) em vez de VIEW
        print("Criando tabela: gold_data_quality_scorecard")
        conn.execute(f"""
            CREATE TABLE gold_data_quality_scorecard AS
            SELECT * FROM read_parquet('{SCORECARD_PATTERN}');
        """)
        
        print("Criando tabela: ge_validation_results")
        conn.execute(f"""
            CREATE TABLE ge_validation_results AS
            SELECT * FROM read_json_auto('{GE_RESULTS_PATTERN}');
        """)
        
        print("✓ Tabelas criadas com sucesso!")
        
        # Verificar
        print("\nTabelas disponíveis:")
        tables = conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            print(f"  - {table[0]}")
            count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
            print(f"    Registros: {count}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
