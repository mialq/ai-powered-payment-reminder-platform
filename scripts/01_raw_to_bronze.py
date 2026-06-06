import duckdb
from pathlib import Path

# 1. Descobre automaticamente a pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[1]

# 2. Define onde estão os arquivos RAW e onde serão salvos os arquivos BRONZE
RAW_DIR = BASE_DIR / "data" / "raw"
BRONZE_DIR = BASE_DIR / "data" / "bronze"

# 3. Garante que a pasta bronze existe
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

# 4. Lista dos arquivos que vamos converter
tables = {
    "application_train": "application_train.csv",
    "installments_payments": "installments_payments.csv"
}

# 5. Conecta no DuckDB
con = duckdb.connect()

print("Iniciando carga Raw → Bronze...")

# 6. Para cada CSV, cria um Parquet na camada Bronze
for table_name, file_name in tables.items():
    input_path = RAW_DIR / file_name
    output_path = BRONZE_DIR / f"bronze_{table_name}.parquet"

    print(f"Convertendo {file_name}...")

    con.execute(f"""
        COPY (
            SELECT *
            FROM read_csv_auto('{input_path}')
        )
        TO '{output_path}'
        (FORMAT PARQUET);
    """)

    print(f"Criado: {output_path}")

print("Bronze criada com sucesso.")

