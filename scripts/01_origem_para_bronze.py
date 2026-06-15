"""
Script: 01_origem_para_bronze.py

Objetivo:
    Converter arquivos CSV da pasta data/raw para arquivos Parquet na camada Bronze.

Entrada:
    data/raw/application_train.csv
    data/raw/installments_payments.csv

Saída:
    data/bronze/bronze_clientes_cadastro.parquet
    data/bronze/bronze_pagamentos_parcelas.parquet

Responsabilidade da camada Bronze:
    - Armazenar os dados em formato Parquet.
    - Manter os dados próximos da origem.
    - Não aplicar regra de negócio.
    - Garantir rastreabilidade dos arquivos originais.
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

# Descobre automaticamente a pasta raiz do projeto.
raiz_projeto = Path(__file__).resolve().parents[1]

# Pasta onde estão os arquivos CSV originais.
caminho_raw = raiz_projeto / "data" / "raw"

# Pasta onde serão gravados os arquivos Parquet da camada Bronze.
caminho_bronze = raiz_projeto / "data" / "bronze"

# Garante que a pasta Bronze exista.
caminho_bronze.mkdir(parents=True, exist_ok=True)

# =============================================================================
# 2. LIMPEZA CONTROLADA DE ARQUIVOS ANTIGOS DA BRONZE
# =============================================================================

# Remove apenas arquivos que este script controla.
# Não apagamos a pasta Bronze inteira para evitar excluir arquivos de outras tabelas,
# históricos, partições ou dados que possam ser usados por outras etapas do pipeline.
arquivos_para_remover = [
    caminho_bronze / "bronze_clientes_cadastro.parquet",
    caminho_bronze / "bronze_pagamentos_parcelas.parquet",

    # Arquivos antigos mantidos apenas por compatibilidade antes da padronização
    caminho_bronze / "bronze_application_train.parquet",
    caminho_bronze / "bronze_installments_payments.parquet",
]

for arquivo in arquivos_para_remover:
    if arquivo.exists():
        arquivo.unlink()
        print(f"Arquivo removido da Bronze: {arquivo}")

# =============================================================================
# 3. ARQUIVOS DE ORIGEM E NOMES PADRONIZADOS NA BRONZE
# =============================================================================

# A chave do dicionário define o nome final do arquivo Parquet.
# O valor do dicionário é o nome do arquivo CSV original.
arquivos_origem = {
    "clientes_cadastro": "application_train.csv",
    "pagamentos_parcelas": "installments_payments.csv"
}


# =============================================================================
# 4. CONEXÃO COM DUCKDB
# =============================================================================

# DuckDB será usado para ler os CSVs e gravar os arquivos Parquet.
con = duckdb.connect()

print("Iniciando carga Raw -> Bronze...")


# =============================================================================
# 5. CONVERSÃO DOS ARQUIVOS CSV PARA PARQUET
# =============================================================================

# Para cada arquivo CSV da origem, criamos um arquivo Parquet na camada Bronze.
# Nesta etapa não aplicamos regra de negócio; apenas mudamos o formato do arquivo
# e padronizamos o nome físico para português, caixa baixa e snake_case.
for nome_tabela, nome_arquivo in arquivos_origem.items():
    arquivo_entrada = caminho_raw / nome_arquivo
    arquivo_saida = caminho_bronze / f"bronze_{nome_tabela}.parquet"

    if not arquivo_entrada.exists():
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {arquivo_entrada}")

    if arquivo_saida.exists():
        arquivo_saida.unlink()
        print(f"Arquivo Bronze anterior removido: {arquivo_saida}")

    print(f"Convertendo {nome_arquivo} para {arquivo_saida.name}...")

    con.execute(f"""
        COPY (
            SELECT *
            FROM read_csv_auto('{arquivo_entrada.as_posix()}')
        )
        TO '{arquivo_saida.as_posix()}'
        (FORMAT PARQUET);
    """)

    print(f"Arquivo criado: {arquivo_saida}")


print("Bronze criada com sucesso.")