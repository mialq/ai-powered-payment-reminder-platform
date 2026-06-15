"""
Script: 07_criar_silver_comportamento_cliente.py

Objetivo:
    Criar uma tabela Silver consolidada por cliente com variáveis de comportamento
    de pagamento, métricas de atraso, indicadores financeiros e classificação de risco.

Entrada:
    data/silver/silver_pagamentos_parcelas.parquet

Saída:
    data/silver/silver_comportamento_pagamento_cliente.parquet

Responsabilidade desta etapa:
    - Agregar os pagamentos por cliente.
    - Criar métricas reutilizáveis de comportamento de pagamento.
    - Criar perfil de pagamento.
    - Criar nível de risco.
    - Manter nomes em português, caixa baixa e snake_case.

Observação:
    Esta ainda é uma camada Silver, pois estamos enriquecendo os dados e criando
    variáveis reutilizáveis. A camada Gold será criada depois, com indicadores
    finais para Power BI e negócio.
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_silver = raiz_projeto / "data" / "silver"
caminho_silver.mkdir(parents=True, exist_ok=True)

# Arquivo de entrada:
# Silver transacional em nível de parcela/pagamento.
arquivo_silver_pagamentos = caminho_silver / "silver_pagamentos_parcelas.parquet"

# Arquivo de saída:
# Silver enriquecida em nível de cliente.
arquivo_silver_comportamento_cliente = caminho_silver / "silver_comportamento_pagamento_cliente.parquet"

# Arquivo temporário:
# Evita sobrescrever a Silver oficial antes da criação terminar com sucesso.
arquivo_silver_comportamento_cliente_tmp = caminho_silver / "silver_comportamento_pagamento_cliente_tmp.parquet"


# =============================================================================
# 2. VALIDAÇÕES INICIAIS E LIMPEZA CONTROLADA
# =============================================================================

if not arquivo_silver_pagamentos.exists():
    raise FileNotFoundError(
        f"Arquivo Silver de pagamentos não encontrado: {arquivo_silver_pagamentos}"
    )

arquivos_para_remover = [
    arquivo_silver_comportamento_cliente_tmp,

    # Arquivo antigo antes da reorganização do pipeline
    caminho_silver / "silver_customer_payment_features.parquet",
]

for arquivo in arquivos_para_remover:
    if arquivo.exists():
        arquivo.unlink()
        print(f"Arquivo removido da Silver: {arquivo}")


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()

print("Iniciando criação da Silver de comportamento de pagamento por cliente...")


# =============================================================================
# 4. CRIAÇÃO DA SILVER CONSOLIDADA POR CLIENTE
# =============================================================================

# Esta etapa agrega os pagamentos tratados da Silver transacional por cliente.
# O resultado é uma tabela reutilizável para a camada Gold, Power BI e análises.
# Aqui nascem as métricas de comportamento, perfil de pagamento e nível de risco.
con.execute(f"""
    COPY (
        WITH metricas_cliente AS (
            SELECT
                id_cliente,

                COUNT(*) AS qtd_parcelas_total,

                COUNT(*) FILTER (
                    WHERE status_pagamento <> 'sem_pagamento_registrado'
                ) AS qtd_parcelas_validas,

                SUM(flg_pagamento_atrasado) AS qtd_parcelas_atraso,
                SUM(flg_pagamento_antecipado) AS qtd_pagas_antecipado,
                SUM(flg_pagamento_no_prazo) AS qtd_pagas_no_prazo,

                ROUND(
                    100.0 * SUM(flg_pagamento_atrasado)
                    / NULLIF(
                        COUNT(*) FILTER (
                            WHERE status_pagamento <> 'sem_pagamento_registrado'
                        ),
                        0
                    ),
                    2
                ) AS taxa_atraso_pct,

                ROUND(AVG(dif_dias_vencimento), 2) AS media_dias_vs_vencimento,

                ROUND(
                    AVG(CASE WHEN dias_atraso > 0 THEN dias_atraso END),
                    2
                ) AS media_dias_atraso,

                MAX(dias_atraso) AS maior_atraso_dias,
                MAX(dias_antecipacao) AS maior_antecipacao_dias,

                ROUND(SUM(valor_previsto), 2) AS valor_previsto_total,
                ROUND(SUM(valor_pago), 2) AS valor_pago_total,

                ROUND(
                    SUM(valor_pago) - SUM(valor_previsto),
                    2
                ) AS dif_valor_pago_previsto_total,

                SUM(flg_nulo_critico) AS qtd_registros_com_nulo_critico,
                SUM(qtd_nulos_criticos) AS qtd_campos_criticos_nulos,

                SUM(flg_pagamento_parcial) AS qtd_pagamentos_parciais,
                SUM(flg_pagamento_acima_previsto) AS qtd_pagamentos_acima_previsto

            FROM read_parquet('{arquivo_silver_pagamentos.as_posix()}')
            GROUP BY id_cliente
        )

        SELECT
            id_cliente,
            qtd_parcelas_total,
            qtd_parcelas_validas,
            qtd_parcelas_atraso,
            qtd_pagas_antecipado,
            qtd_pagas_no_prazo,

            COALESCE(taxa_atraso_pct, 0) AS taxa_atraso_pct,
            COALESCE(media_dias_vs_vencimento, 0) AS media_dias_vs_vencimento,
            COALESCE(media_dias_atraso, 0) AS media_dias_atraso,
            COALESCE(maior_atraso_dias, 0) AS maior_atraso_dias,
            COALESCE(maior_antecipacao_dias, 0) AS maior_antecipacao_dias,

            valor_previsto_total,
            valor_pago_total,
            dif_valor_pago_previsto_total,

            qtd_registros_com_nulo_critico,
            qtd_campos_criticos_nulos,
            qtd_pagamentos_parciais,
            qtd_pagamentos_acima_previsto,

            CASE
                WHEN qtd_parcelas_validas = 0 THEN 'comportamento_desconhecido'

                WHEN qtd_parcelas_atraso = 0
                 AND qtd_pagas_antecipado >= qtd_pagas_no_prazo
                THEN 'pagador_antecipado'

                WHEN qtd_parcelas_atraso = 0
                THEN 'pagador_no_prazo'

                WHEN taxa_atraso_pct < 10
                THEN 'baixo_atraso'

                WHEN taxa_atraso_pct >= 10
                 AND taxa_atraso_pct < 30
                THEN 'atraso_moderado'

                WHEN taxa_atraso_pct >= 30
                THEN 'alto_atraso'

                ELSE 'comportamento_desconhecido'
            END AS perfil_pagamento,

            CASE
                WHEN qtd_parcelas_validas = 0 THEN 'risco_desconhecido'

                WHEN taxa_atraso_pct >= 30
                  OR maior_atraso_dias >= 30
                THEN 'alto_risco'

                WHEN taxa_atraso_pct >= 10
                  OR media_dias_atraso >= 5
                  OR maior_atraso_dias >= 10
                THEN 'medio_risco'

                ELSE 'baixo_risco'
            END AS nivel_risco,

            current_timestamp AS dt_processamento_silver

        FROM metricas_cliente
    )
    TO '{arquivo_silver_comportamento_cliente_tmp.as_posix()}'
    (FORMAT PARQUET);
""")


# =============================================================================
# 5. SUBSTITUIÇÃO SEGURA DO ARQUIVO OFICIAL
# =============================================================================

# O arquivo é criado primeiro como temporário.
# Somente depois que a criação termina com sucesso, ele substitui o arquivo oficial.
# Isso evita deixar a Silver corrompida caso o processo seja interrompido.
if arquivo_silver_comportamento_cliente.exists():
    arquivo_silver_comportamento_cliente.unlink()
    print(f"Arquivo Silver anterior removido: {arquivo_silver_comportamento_cliente}")

arquivo_silver_comportamento_cliente_tmp.replace(arquivo_silver_comportamento_cliente)

print(
    "Silver de comportamento por cliente criada com sucesso: "
    f"{arquivo_silver_comportamento_cliente}"
)


# =============================================================================
# 6. VALIDAÇÃO RÁPIDA
# =============================================================================

total_clientes = con.execute(f"""
    SELECT COUNT(*)
    FROM read_parquet('{arquivo_silver_comportamento_cliente.as_posix()}')
""").fetchone()[0]

print(f"Total de clientes na Silver de comportamento: {total_clientes}")


resumo_risco = con.execute(f"""
    SELECT
        nivel_risco,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_comportamento_cliente.as_posix()}')
    GROUP BY nivel_risco
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por nível de risco:")
print(resumo_risco)


resumo_perfil = con.execute(f"""
    SELECT
        perfil_pagamento,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_comportamento_cliente.as_posix()}')
    GROUP BY perfil_pagamento
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por perfil de pagamento:")
print(resumo_perfil)


amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_silver_comportamento_cliente.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Silver de comportamento por cliente:")
print(amostra)

print("\nCriação da Silver de comportamento por cliente concluída com sucesso.")