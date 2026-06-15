from pathlib import Path
import duckdb

# Caminho raiz do projeto
raiz_projeto = Path(__file__).resolve().parents[1]

# Arquivo Silver que queremos validar
arquivo_silver = raiz_projeto / "data" / "silver" / "silver_pagamentos_parcelas.parquet"

# Verifica se o arquivo existe
if not arquivo_silver.exists():
    raise FileNotFoundError(f"Arquivo Silver não encontrado: {arquivo_silver}")

con = duckdb.connect()

print("Arquivo Silver encontrado:")
print(arquivo_silver)


# 1. Conta registros
total = con.execute(f"""
    SELECT COUNT(*) 
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").fetchone()[0]

print(f"\nTotal de registros: {total}")


# 2. Mostra estrutura da tabela
schema = con.execute(f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").df()

print("\nColunas da Silver:")
print(schema)


# 3. Valida se as colunas esperadas existem
colunas_esperadas = {
    "id_cliente",
    "id_contrato_anterior",
    "versao_parcela",
    "numero_parcela",
    "dias_previsto_ref",
    "dias_pagamento_ref",
    "dif_dias_vencimento",
    "dias_atraso",
    "dias_antecipacao",
    "valor_previsto",
    "valor_pago",
    "dif_valor_pago_previsto",
    "status_pagamento",
    "status_valor_pagamento",
    "flg_pagamento_atrasado",
    "flg_pagamento_antecipado",
    "flg_pagamento_no_prazo",
    "flg_pagamento_parcial",
    "flg_pagamento_acima_previsto",
    "flg_valor_negativo",
    "flg_id_cliente_nulo",
    "flg_id_contrato_nulo",
    "flg_dia_previsto_nulo",
    "flg_dia_pagamento_nulo",
    "flg_valor_previsto_nulo",
    "flg_valor_pago_nulo",
    "flg_nulo_critico",
    "qtd_nulos_criticos",
    "arquivo_origem",
    "arquivo_bronze",
    "dt_processamento_silver"
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


# 4. Valida padrão dos nomes das colunas
colunas_fora_padrao = [
    coluna
    for coluna in colunas_atuais
    if coluna != coluna.lower() or " " in coluna
]

print("\nValidação de padrão dos nomes das colunas:")

if colunas_fora_padrao:
    print("Colunas fora do padrão minúsculo/snake_case:")
    for coluna in colunas_fora_padrao:
        print(f"- {coluna}")
else:
    print("Todas as colunas estão em minúsculo e sem espaços.")


# 5. Mostra amostra
amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_silver.as_posix()}')
    LIMIT 5
""").df()

print("\nAmostra da Silver:")
print(amostra)


# 6. Valida status de pagamento
status_pagamento = con.execute(f"""
    SELECT
        status_pagamento,
        COUNT(*) AS total
    FROM read_parquet('{arquivo_silver.as_posix()}')
    GROUP BY status_pagamento
    ORDER BY total DESC
""").df()

print("\nResumo por status de pagamento:")
print(status_pagamento)


# 7. Valida status do valor de pagamento
status_valor = con.execute(f"""
    SELECT
        status_valor_pagamento,
        COUNT(*) AS total
    FROM read_parquet('{arquivo_silver.as_posix()}')
    GROUP BY status_valor_pagamento
    ORDER BY total DESC
""").df()

print("\nResumo por status do valor de pagamento:")
print(status_valor)


# 8. Valida nulos críticos
qualidade = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        SUM(flg_nulo_critico) AS registros_com_nulo_critico,
        SUM(qtd_nulos_criticos) AS total_campos_criticos_nulos,
        SUM(flg_id_cliente_nulo) AS nulos_id_cliente,
        SUM(flg_id_contrato_nulo) AS nulos_id_contrato,
        SUM(flg_dia_previsto_nulo) AS nulos_dia_previsto,
        SUM(flg_dia_pagamento_nulo) AS nulos_dia_pagamento,
        SUM(flg_valor_previsto_nulo) AS nulos_valor_previsto,
        SUM(flg_valor_pago_nulo) AS nulos_valor_pago
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").df()

print("\nResumo de nulos críticos:")
print(qualidade)


# 9. Valida regras de atraso e antecipação
regras_atraso = con.execute(f"""
    SELECT
        SUM(CASE WHEN dias_atraso < 0 THEN 1 ELSE 0 END) AS registros_com_atraso_negativo,
        SUM(CASE WHEN dias_antecipacao < 0 THEN 1 ELSE 0 END) AS registros_com_antecipacao_negativa,
        SUM(CASE WHEN dif_dias_vencimento > 0 AND flg_pagamento_atrasado <> 1 THEN 1 ELSE 0 END) AS inconsistencias_flag_atraso,
        SUM(CASE WHEN dif_dias_vencimento < 0 AND flg_pagamento_antecipado <> 1 THEN 1 ELSE 0 END) AS inconsistencias_flag_antecipado,
        SUM(CASE WHEN dif_dias_vencimento IS NOT NULL AND dif_dias_vencimento = 0 AND flg_pagamento_no_prazo <> 1
        THEN 1 
        ELSE 0 
    END
) AS inconsistencias_flag_prazo
                            
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").df()

print("\nValidação das regras de atraso e antecipação:")
print(regras_atraso)


# 10. Valida se valores categóricos estão em caixa baixa
validacao_caixa_baixa = con.execute(f"""
    SELECT
        SUM(CASE WHEN status_pagamento <> LOWER(status_pagamento) THEN 1 ELSE 0 END) AS status_pagamento_com_maiuscula,
        SUM(CASE WHEN status_valor_pagamento <> LOWER(status_valor_pagamento) THEN 1 ELSE 0 END) AS status_valor_com_maiuscula
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").df()

print("\nValidação de caixa baixa em campos categóricos:")
print(validacao_caixa_baixa)


# 11. Valida valores financeiros
validacao_financeira = con.execute(f"""
    SELECT
        SUM(flg_valor_negativo) AS registros_com_valor_negativo,
        SUM(flg_pagamento_parcial) AS total_pagamentos_parciais,
        SUM(flg_pagamento_acima_previsto) AS total_pagamentos_acima_previsto,
        ROUND(100.0 * SUM(flg_pagamento_atrasado) / COUNT(*), 2) AS taxa_atraso_pct
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").df()

print("\nResumo financeiro e atraso:")
print(validacao_financeira)


print("\nValidação da Silver concluída.")
