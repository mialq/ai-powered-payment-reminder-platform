"""
Script: 02_validar_bronze_arquivos.py

Objetivo:
    Validar se os arquivos Parquet da camada Bronze foram criados corretamente.

Arquivos validados:
    data/bronze/bronze_clientes_cadastro.parquet
    data/bronze/bronze_pagamentos_parcelas.parquet

Responsabilidade desta validação:
    - Confirmar se os arquivos existem.
    - Contar a quantidade de registros.
    - Exibir o schema das tabelas.
    - Exibir uma pequena amostra dos dados.
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_bronze = raiz_projeto / "data" / "bronze"

arquivos_bronze = {
    "clientes_cadastro": caminho_bronze / "bronze_clientes_cadastro.parquet",
    "pagamentos_parcelas": caminho_bronze / "bronze_pagamentos_parcelas.parquet",
}


# =============================================================================
# 2. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()

print("Iniciando validação dos arquivos da Bronze...")


# =============================================================================
# 3. VALIDAÇÃO DOS ARQUIVOS
# =============================================================================

for nome_tabela, arquivo in arquivos_bronze.items():
    print("\n" + "=" * 80)
    print(f"Validando arquivo: {nome_tabela}")
    print("=" * 80)

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo Bronze não encontrado: {arquivo}")

    print(f"Arquivo encontrado: {arquivo}")

    total_registros = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{arquivo.as_posix()}')
    """).fetchone()[0]

    print(f"Total de registros: {total_registros}")

    schema = con.execute(f"""
        DESCRIBE
        SELECT *
        FROM read_parquet('{arquivo.as_posix()}')
    """).df()

    print("\nColunas:")
    print(schema)

    amostra = con.execute(f"""
        SELECT *
        FROM read_parquet('{arquivo.as_posix()}')
        LIMIT 5
    """).df()

    print("\nAmostra:")
    print(amostra)


print("\nValidação da Bronze concluída com sucesso.")