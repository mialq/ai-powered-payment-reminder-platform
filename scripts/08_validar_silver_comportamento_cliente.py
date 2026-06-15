"""
Script: 08_validar_silver_comportamento_cliente.py

Objetivo:
    Validar a Silver de comportamento de pagamento por cliente.

Entrada:
    data/silver/silver_comportamento_pagamento_cliente.parquet

Responsabilidade desta validação:
    - Confirmar se o arquivo existe.
    - Validar volume de clientes.
    - Validar colunas esperadas.
    - Validar padrão de nomes em português, caixa baixa e snake_case.
    - Validar valores categóricos de perfil_pagamento e nivel_risco.
    - Validar regras de atraso, risco e métricas agregadas.
    - Medir cobertura com a Silver de clientes/cadastro, quando existir.
"""

from pathlib import Path
import re
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_silver = raiz_projeto / "data" / "silver"

arquivo_silver_comportamento = (
    caminho_silver / "silver_comportamento_pagamento_cliente.parquet"
)

arquivo_silver_clientes = (
    caminho_silver / "silver_clientes_cadastro.parquet"
)


# =============================================================================
# 2. VALIDAÇÃO DE EXISTÊNCIA DO ARQUIVO
# =============================================================================

if not arquivo_silver_comportamento.exists():
    raise FileNotFoundError(
        f"Arquivo Silver de comportamento não encontrado: {arquivo_silver_comportamento}"
    )

print("Arquivo Silver de comportamento encontrado:")
print(arquivo_silver_comportamento)


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()


# =============================================================================
# 4. RESUMO DE VOLUME
# =============================================================================

resumo_volume = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        COUNT(DISTINCT id_cliente) AS total_clientes_distintos,
        COUNT(*) - COUNT(DISTINCT id_cliente) AS registros_duplicados
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nResumo de volume:")
print(resumo_volume)


# =============================================================================
# 5. ESTRUTURA DA TABELA
# =============================================================================

schema = con.execute(f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nColunas da Silver de comportamento:")
print(schema)


# =============================================================================
# 6. VALIDAÇÃO DE COLUNAS ESPERADAS
# =============================================================================

colunas_esperadas = {
    "id_cliente",
    "qtd_parcelas_total",
    "qtd_parcelas_validas",
    "qtd_parcelas_atraso",
    "qtd_pagas_antecipado",
    "qtd_pagas_no_prazo",
    "taxa_atraso_pct",
    "media_dias_vs_vencimento",
    "media_dias_atraso",
    "maior_atraso_dias",
    "maior_antecipacao_dias",
    "valor_previsto_total",
    "valor_pago_total",
    "dif_valor_pago_previsto_total",
    "qtd_registros_com_nulo_critico",
    "qtd_campos_criticos_nulos",
    "qtd_pagamentos_parciais",
    "qtd_pagamentos_acima_previsto",
    "perfil_pagamento",
    "nivel_risco",
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
    print("Colunas fora do padrão minúsculo/snake_case:")
    for coluna in colunas_fora_padrao:
        print(f"- {coluna}")
else:
    print("Todas as colunas estão em minúsculo e snake_case.")


# =============================================================================
# 8. AMOSTRA
# =============================================================================

amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Silver de comportamento:")
print(amostra)


# =============================================================================
# 9. RESUMO POR NÍVEL DE RISCO
# =============================================================================

resumo_risco = con.execute(f"""
    SELECT
        nivel_risco,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
    GROUP BY nivel_risco
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por nível de risco:")
print(resumo_risco)


# =============================================================================
# 10. RESUMO POR PERFIL DE PAGAMENTO
# =============================================================================

resumo_perfil = con.execute(f"""
    SELECT
        perfil_pagamento,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
    GROUP BY perfil_pagamento
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por perfil de pagamento:")
print(resumo_perfil)


# =============================================================================
# 11. VALIDAÇÃO DE VALORES CATEGÓRICOS PERMITIDOS
# =============================================================================

valores_invalidos = con.execute(f"""
    SELECT
        SUM(
            CASE
                WHEN nivel_risco NOT IN (
                    'baixo_risco',
                    'medio_risco',
                    'alto_risco',
                    'risco_desconhecido'
                )
                THEN 1 ELSE 0
            END
        ) AS nivel_risco_invalido,

        SUM(
            CASE
                WHEN perfil_pagamento NOT IN (
                    'pagador_antecipado',
                    'pagador_no_prazo',
                    'baixo_atraso',
                    'atraso_moderado',
                    'alto_atraso',
                    'comportamento_desconhecido'
                )
                THEN 1 ELSE 0
            END
        ) AS perfil_pagamento_invalido

    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nValidação de valores categóricos permitidos:")
print(valores_invalidos)


# =============================================================================
# 12. VALIDAÇÃO DE CAIXA BAIXA NOS CAMPOS CATEGÓRICOS
# =============================================================================

validacao_caixa_baixa = con.execute(f"""
    SELECT
        SUM(CASE WHEN nivel_risco <> LOWER(nivel_risco) THEN 1 ELSE 0 END) AS nivel_risco_com_maiuscula,
        SUM(CASE WHEN perfil_pagamento <> LOWER(perfil_pagamento) THEN 1 ELSE 0 END) AS perfil_pagamento_com_maiuscula
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nValidação de caixa baixa em campos categóricos:")
print(validacao_caixa_baixa)


# =============================================================================
# 13. VALIDAÇÃO DE REGRAS NUMÉRICAS
# =============================================================================

validacao_numerica = con.execute(f"""
    SELECT
        SUM(CASE WHEN qtd_parcelas_total < 0 THEN 1 ELSE 0 END) AS qtd_parcelas_total_negativa,
        SUM(CASE WHEN qtd_parcelas_validas < 0 THEN 1 ELSE 0 END) AS qtd_parcelas_validas_negativa,
        SUM(CASE WHEN qtd_parcelas_validas > qtd_parcelas_total THEN 1 ELSE 0 END) AS parcelas_validas_maior_que_total,
        SUM(CASE WHEN qtd_parcelas_atraso < 0 THEN 1 ELSE 0 END) AS qtd_atraso_negativa,
        SUM(CASE WHEN qtd_pagas_antecipado < 0 THEN 1 ELSE 0 END) AS qtd_antecipado_negativa,
        SUM(CASE WHEN qtd_pagas_no_prazo < 0 THEN 1 ELSE 0 END) AS qtd_no_prazo_negativa,
        SUM(CASE WHEN taxa_atraso_pct < 0 OR taxa_atraso_pct > 100 THEN 1 ELSE 0 END) AS taxa_atraso_fora_intervalo,
        SUM(CASE WHEN maior_atraso_dias < 0 THEN 1 ELSE 0 END) AS maior_atraso_negativo,
        SUM(CASE WHEN maior_antecipacao_dias < 0 THEN 1 ELSE 0 END) AS maior_antecipacao_negativa
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nValidação de regras numéricas:")
print(validacao_numerica)


# =============================================================================
# 14. RESUMO FINANCEIRO
# =============================================================================

resumo_financeiro = con.execute(f"""
    SELECT
        ROUND(SUM(valor_previsto_total), 2) AS valor_previsto_total_geral,
        ROUND(SUM(valor_pago_total), 2) AS valor_pago_total_geral,
        ROUND(SUM(dif_valor_pago_previsto_total), 2) AS dif_valor_total_geral,
        SUM(qtd_pagamentos_parciais) AS total_pagamentos_parciais,
        SUM(qtd_pagamentos_acima_previsto) AS total_pagamentos_acima_previsto,
        SUM(qtd_registros_com_nulo_critico) AS total_registros_com_nulo_critico,
        SUM(qtd_campos_criticos_nulos) AS total_campos_criticos_nulos
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nResumo financeiro:")
print(resumo_financeiro)


# =============================================================================
# 15. COBERTURA COM A SILVER DE CLIENTES
# =============================================================================

if arquivo_silver_clientes.exists():
    cobertura_clientes = con.execute(f"""
        SELECT
            COUNT(*) AS total_clientes_comportamento,
            SUM(CASE WHEN c.id_cliente IS NOT NULL THEN 1 ELSE 0 END) AS clientes_com_cadastro,
            SUM(CASE WHEN c.id_cliente IS NULL THEN 1 ELSE 0 END) AS clientes_sem_cadastro,
            ROUND(
                100.0 * SUM(CASE WHEN c.id_cliente IS NOT NULL THEN 1 ELSE 0 END)
                / COUNT(*),
                2
            ) AS pct_clientes_com_cadastro
        FROM read_parquet('{arquivo_silver_comportamento.as_posix()}') b
        LEFT JOIN read_parquet('{arquivo_silver_clientes.as_posix()}') c
            ON b.id_cliente = c.id_cliente
    """).df()

    print("\nCobertura com a Silver de clientes:")
    print(cobertura_clientes)
else:
    print("\nSilver de clientes não encontrada. Cobertura com cadastro não validada.")


# =============================================================================
# 16. VALIDAÇÃO DE METADADO DE PROCESSAMENTO
# =============================================================================

validacao_processamento = con.execute(f"""
    SELECT
        MIN(dt_processamento_silver) AS menor_dt_processamento,
        MAX(dt_processamento_silver) AS maior_dt_processamento,
        COUNT(DISTINCT dt_processamento_silver) AS qtd_datas_processamento
    FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
""").df()

print("\nValidação da data de processamento:")
print(validacao_processamento)


print("\nValidação da Silver de comportamento por cliente concluída.")