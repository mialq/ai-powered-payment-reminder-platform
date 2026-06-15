"""
Script: 06_validar_silver_clientes.py

Objetivo:
    Validar a Silver de clientes criada a partir da Bronze de cadastro.

Entrada:
    data/silver/silver_clientes_cadastro.parquet

Responsabilidade desta validação:
    - Confirmar se o arquivo existe.
    - Contar registros e clientes distintos.
    - Validar colunas esperadas.
    - Validar padrão de nomes em português, caixa baixa e snake_case.
    - Validar valores categóricos em caixa baixa.
    - Validar flags de qualidade.
    - Validar possíveis problemas financeiros e cadastrais.
"""

from pathlib import Path
import re
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

arquivo_silver_clientes = (
    raiz_projeto / "data" / "silver" / "silver_clientes_cadastro.parquet"
)


# =============================================================================
# 2. VALIDAÇÃO DE EXISTÊNCIA DO ARQUIVO
# =============================================================================

if not arquivo_silver_clientes.exists():
    raise FileNotFoundError(
        f"Arquivo Silver de clientes não encontrado: {arquivo_silver_clientes}"
    )

print("Arquivo Silver de clientes encontrado:")
print(arquivo_silver_clientes)


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()


# =============================================================================
# 4. CONTAGEM DE REGISTROS
# =============================================================================

resumo_volume = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        COUNT(DISTINCT id_cliente) AS total_clientes_distintos,
        COUNT(*) - COUNT(DISTINCT id_cliente) AS registros_duplicados
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
""").df()

print("\nResumo de volume:")
print(resumo_volume)


# =============================================================================
# 5. ESTRUTURA DA TABELA
# =============================================================================

schema = con.execute(f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
""").df()

print("\nColunas da Silver de clientes:")
print(schema)


# =============================================================================
# 6. VALIDAÇÃO DE COLUNAS ESPERADAS
# =============================================================================

colunas_esperadas = {
    "id_cliente",
    "flg_inadimplencia_historica",
    "tipo_contrato",
    "genero",
    "flg_possui_carro",
    "flg_possui_imovel",
    "qtd_filhos",
    "renda_total",
    "valor_credito",
    "valor_anuidade",
    "valor_bens",
    "tipo_acompanhante",
    "tipo_renda",
    "escolaridade",
    "estado_civil",
    "tipo_moradia",
    "populacao_relativa_regiao",
    "idade_anos",
    "tempo_emprego_anos",
    "idade_carro_anos",
    "flg_possui_celular",
    "flg_possui_telefone_emprego",
    "flg_possui_telefone_trabalho",
    "flg_celular_contatavel",
    "flg_possui_telefone",
    "flg_possui_email",
    "ocupacao",
    "qtd_membros_familia",
    "avaliacao_regiao_cliente",
    "avaliacao_regiao_cliente_cidade",
    "dia_semana_solicitacao",
    "hora_solicitacao",
    "fonte_externa_1",
    "fonte_externa_2",
    "fonte_externa_3",
    "qtd_obs_circulo_social_30d",
    "qtd_def_circulo_social_30d",
    "qtd_obs_circulo_social_60d",
    "qtd_def_circulo_social_60d",
    "dias_ultima_alteracao_telefone_ref",
    "qtd_consultas_credito_hora",
    "qtd_consultas_credito_dia",
    "qtd_consultas_credito_semana",
    "qtd_consultas_credito_mes",
    "qtd_consultas_credito_trimestre",
    "qtd_consultas_credito_ano",
    "arquivo_origem",
    "arquivo_bronze",
    "razao_credito_renda",
    "razao_anuidade_renda",
    "flg_id_cliente_nulo",
    "flg_renda_nula",
    "flg_credito_nulo",
    "flg_anuidade_nula",
    "flg_idade_nula",
    "flg_valor_negativo",
    "qtd_nulos_criticos",
    "flg_nulo_critico",
    "dt_processamento_silver",
}

colunas_atuais = set(schema["column_name"].tolist())

colunas_faltando = sorted(colunas_esperadas - colunas_atuais)
colunas_extras = sorted(colunas_atuais - colunas_esperadas)

print("\nValidação de colunas esperadas:")

if colunas_faltando:
    print("Colunas faltando:")
    for coluna in colunas_faltando:
        print(f"- {coluna}")
else:
    print("Todas as colunas esperadas existem.")

if colunas_extras:
    print("\nColunas extras encontradas:")
    for coluna in colunas_extras:
        print(f"- {coluna}")
else:
    print("Nenhuma coluna extra encontrada.")


# =============================================================================
# 7. VALIDAÇÃO DO PADRÃO DOS NOMES DAS COLUNAS
# =============================================================================

padrao_snake_case = re.compile(r"^[a-z0-9_]+$")

colunas_fora_padrao = [
    coluna
    for coluna in colunas_atuais
    if not padrao_snake_case.match(coluna)
]

print("\nValidação de padrão dos nomes das colunas:")

if colunas_fora_padrao:
    print("Colunas fora do padrão português/minúsculo/snake_case:")
    for coluna in colunas_fora_padrao:
        print(f"- {coluna}")
else:
    print("Todas as colunas estão em minúsculo e snake_case.")


# =============================================================================
# 8. AMOSTRA DA SILVER
# =============================================================================

amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
    LIMIT 5
""").df()

print("\nAmostra da Silver de clientes:")
print(amostra)


# =============================================================================
# 9. RESUMOS CATEGÓRICOS
# =============================================================================

campos_categoricos = [
    "tipo_contrato",
    "genero",
    "tipo_acompanhante",
    "tipo_renda",
    "escolaridade",
    "estado_civil",
    "tipo_moradia",
    "ocupacao",
    "dia_semana_solicitacao",
]

for campo in campos_categoricos:
    resumo = con.execute(f"""
        SELECT
            {campo},
            COUNT(*) AS qtd_clientes
        FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
        GROUP BY {campo}
        ORDER BY qtd_clientes DESC
        LIMIT 20
    """).df()

    print(f"\nResumo por {campo}:")
    print(resumo)


# =============================================================================
# 10. VALIDAÇÃO DE CAIXA BAIXA NOS CAMPOS CATEGÓRICOS
# =============================================================================

expressoes_caixa_baixa = []

for campo in campos_categoricos:
    expressoes_caixa_baixa.append(
        f"SUM(CASE WHEN {campo} <> LOWER({campo}) THEN 1 ELSE 0 END) AS {campo}_com_maiuscula"
    )

query_caixa_baixa = f"""
    SELECT
        {", ".join(expressoes_caixa_baixa)}
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
"""

validacao_caixa_baixa = con.execute(query_caixa_baixa).df()

print("\nValidação de caixa baixa em campos categóricos:")
print(validacao_caixa_baixa)


# =============================================================================
# 11. VALIDAÇÃO DE QUALIDADE DOS DADOS
# =============================================================================

qualidade = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        SUM(flg_nulo_critico) AS registros_com_nulo_critico,
        SUM(qtd_nulos_criticos) AS total_campos_criticos_nulos,
        SUM(flg_id_cliente_nulo) AS nulos_id_cliente,
        SUM(flg_renda_nula) AS nulos_renda,
        SUM(flg_credito_nulo) AS nulos_credito,
        SUM(flg_anuidade_nula) AS nulos_anuidade,
        SUM(flg_idade_nula) AS nulos_idade,
        SUM(flg_valor_negativo) AS registros_com_valor_negativo
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
""").df()

print("\nResumo de qualidade dos dados:")
print(qualidade)


# =============================================================================
# 12. VALIDAÇÃO DE FLAGS BINÁRIAS
# =============================================================================

flags_binarias = [
    "flg_inadimplencia_historica",
    "flg_possui_carro",
    "flg_possui_imovel",
    "flg_possui_celular",
    "flg_possui_telefone_emprego",
    "flg_possui_telefone_trabalho",
    "flg_celular_contatavel",
    "flg_possui_telefone",
    "flg_possui_email",
    "flg_id_cliente_nulo",
    "flg_renda_nula",
    "flg_credito_nulo",
    "flg_anuidade_nula",
    "flg_idade_nula",
    "flg_valor_negativo",
    "flg_nulo_critico",
]

expressoes_flags = []

for flag in flags_binarias:
    expressoes_flags.append(
        f"SUM(CASE WHEN {flag} IS NOT NULL AND {flag} NOT IN (0, 1) THEN 1 ELSE 0 END) AS {flag}_fora_padrao"
    )

query_flags = f"""
    SELECT
        {", ".join(expressoes_flags)}
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
"""

validacao_flags = con.execute(query_flags).df()

print("\nValidação de flags binárias:")
print(validacao_flags)


# =============================================================================
# 13. VALIDAÇÃO FINANCEIRA E CADASTRAL
# =============================================================================

validacao_financeira = con.execute(f"""
    SELECT
        MIN(renda_total) AS menor_renda,
        MAX(renda_total) AS maior_renda,
        MIN(valor_credito) AS menor_credito,
        MAX(valor_credito) AS maior_credito,
        MIN(valor_anuidade) AS menor_anuidade,
        MAX(valor_anuidade) AS maior_anuidade,
        MIN(idade_anos) AS menor_idade,
        MAX(idade_anos) AS maior_idade,
        SUM(CASE WHEN idade_anos < 18 THEN 1 ELSE 0 END) AS clientes_menores_18,
        SUM(CASE WHEN idade_anos > 100 THEN 1 ELSE 0 END) AS clientes_maiores_100,
        SUM(CASE WHEN razao_credito_renda < 0 THEN 1 ELSE 0 END) AS razao_credito_renda_negativa,
        SUM(CASE WHEN razao_anuidade_renda < 0 THEN 1 ELSE 0 END) AS razao_anuidade_renda_negativa
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
""").df()

print("\nValidação financeira e cadastral:")
print(validacao_financeira)


# =============================================================================
# 14. VALIDAÇÃO DE METADADOS
# =============================================================================

metadados = con.execute(f"""
    SELECT
        arquivo_origem,
        arquivo_bronze,
        COUNT(*) AS total_registros
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
    GROUP BY arquivo_origem, arquivo_bronze
""").df()

print("\nValidação de metadados:")
print(metadados)


print("\nValidação da Silver de clientes concluída.")