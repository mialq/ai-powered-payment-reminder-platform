from pathlib import Path
import duckdb

# Caminho raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]

parquet_file = PROJECT_ROOT / "data" / "bronze" / "bronze_installments_payments.parquet"

con = duckdb.connect()

df = con.execute(f"""
    SELECT *
    FROM read_parquet('{parquet_file.as_posix()}')
    LIMIT 5
""").df()

print(df)