from pathlib import Path
import duckdb

# Caminho raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Arquivo Silver que queremos validar
silver_file = PROJECT_ROOT / "data" / "silver" / "silver_installments_payments.parquet"

# Verifica se o arquivo existe
if not silver_file.exists():
    raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_file}")

con = duckdb.connect()

print("Arquivo Silver encontrado:")
print(silver_file)

# 1. Conta registros
total = con.execute(f"""
    SELECT COUNT(*) 
    FROM read_parquet('{silver_file.as_posix()}')
""").fetchone()[0]

print(f"\nTotal de registros: {total}")

# 2. Mostra colunas
schema = con.execute(f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{silver_file.as_posix()}')
""").df()

print("\nColunas da Silver:")
print(schema)

# 3. Mostra amostra
amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{silver_file.as_posix()}')
    LIMIT 5
""").df()

print("\nAmostra:")
print(amostra)

# 4. Valida status de pagamento
status = con.execute(f"""
    SELECT
        payment_status,
        COUNT(*) AS total
    FROM read_parquet('{silver_file.as_posix()}')
    GROUP BY payment_status
    ORDER BY total DESC
""").df()

print("\nResumo por status de pagamento:")
print(status)

print("\nValidação da Silver concluída com sucesso.")

