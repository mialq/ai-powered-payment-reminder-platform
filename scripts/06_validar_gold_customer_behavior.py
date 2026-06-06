from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]

gold_file = PROJECT_ROOT / "data" / "gold" / "gold_customer_payment_behavior.parquet"

if not gold_file.exists():
    raise FileNotFoundError(f"Arquivo Gold não encontrado: {gold_file}")

con = duckdb.connect()

print("Arquivo Gold encontrado:")
print(gold_file)

total = con.execute(f"""
    SELECT COUNT(*)
    FROM read_parquet('{gold_file.as_posix()}')
""").fetchone()[0]

print(f"\nTotal de clientes na Gold: {total}")

risk = con.execute(f"""
    SELECT
        risk_level,
        COUNT(*) AS total_customers
    FROM read_parquet('{gold_file.as_posix()}')
    GROUP BY risk_level
    ORDER BY total_customers DESC
""").df()

print("\nResumo por risco:")
print(risk)

sample = con.execute(f"""
    SELECT *
    FROM read_parquet('{gold_file.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra:")
print(sample)

print("\nValidação da Gold concluída com sucesso.")