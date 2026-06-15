"""
Script: 09_criar_gold_indicadores_cliente.py

Objetivo:
    Criar a camada Gold de indicadores por cliente para consumo no Power BI
    e análise de priorização de contato.

Entradas:
    data/silver/silver_comportamento_pagamento_cliente.parquet
    data/silver/silver_clientes_cadastro.parquet

Saída:
    data/gold/gold_indicadores_cliente.parquet

Responsabilidade desta etapa:
    - Juntar comportamento de pagamento com dados cadastrais.
    - Manter todos os clientes com histórico de pagamento.
    - Sinalizar clientes sem cadastro.
    - Criar indicadores finais de negócio.
    - Criar prioridade de contato e ação recomendada.
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_silver = raiz_projeto / "data" / "silver"
caminho_gold = raiz_projeto / "data" / "gold"

caminho_gold.mkdir(parents=True, exist_ok=True)

arquivo_silver_comportamento = (
    caminho_silver / "silver_comportamento_pagamento_cliente.parquet"
)

arquivo_silver_clientes = (
    caminho_silver / "silver_clientes_cadastro.parquet"
)

arquivo_gold = caminho_gold / "gold_indicadores_cliente.parquet"

arquivo_gold_tmp = caminho_gold / "gold_indicadores_cliente_tmp.parquet"


# =============================================================================
# 2. VALIDAÇÕES INICIAIS E LIMPEZA CONTROLADA
# =============================================================================

if not arquivo_silver_comportamento.exists():
    raise FileNotFoundError(
        f"Arquivo Silver de comportamento não encontrado: {arquivo_silver_comportamento}"
    )

if not arquivo_silver_clientes.exists():
    raise FileNotFoundError(
        f"Arquivo Silver de clientes não encontrado: {arquivo_silver_clientes}"
    )

arquivos_para_remover = [
    arquivo_gold_tmp,

    # Arquivos antigos antes da padronização do projeto
    caminho_gold / "gold_customer_payment_behavior.parquet",
    caminho_gold / "gold_customer_payment_behavior_tmp.parquet",
]

for arquivo in arquivos_para_remover:
    if arquivo.exists():
        arquivo.unlink()
        print(f"Arquivo removido da Gold: {arquivo}")


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()

print("Iniciando criação da Gold de indicadores por cliente...")


# =============================================================================
# 4. CRIAÇÃO DA GOLD
# =============================================================================

# A Gold parte da Silver de comportamento para não perder clientes com histórico
# de pagamento. O cadastro entra como enriquecimento via LEFT JOIN.
# Quando o cliente não existe no cadastro, criamos flags e valores padrão.
con.execute(f"""
    COPY (
        SELECT
            b.id_cliente,

            -- Indicadores de comportamento de pagamento
            b.nivel_risco,
            b.perfil_pagamento,
            b.qtd_parcelas_total,
            b.qtd_parcelas_validas,
            b.qtd_parcelas_atraso,
            b.qtd_pagas_antecipado,
            b.qtd_pagas_no_prazo,
            b.taxa_atraso_pct,
            b.media_dias_vs_vencimento,
            b.media_dias_atraso,
            b.maior_atraso_dias,
            b.maior_antecipacao_dias,
            b.valor_previsto_total,
            b.valor_pago_total,
            b.dif_valor_pago_previsto_total,
            b.qtd_registros_com_nulo_critico,
            b.qtd_campos_criticos_nulos,
            b.qtd_pagamentos_parciais,
            b.qtd_pagamentos_acima_previsto,

            -- Cobertura cadastral
            CASE
                WHEN c.id_cliente IS NULL THEN 0
                ELSE 1
            END AS flg_cliente_com_cadastro,

            CASE
                WHEN c.id_cliente IS NULL THEN 'cliente_sem_cadastro'
                ELSE 'cliente_com_cadastro'
            END AS status_cadastro,

            -- Dados cadastrais tratados
            COALESCE(c.genero, 'cadastro_nao_disponivel') AS genero,
            COALESCE(c.tipo_renda, 'cadastro_nao_disponivel') AS tipo_renda,
            COALESCE(c.escolaridade, 'cadastro_nao_disponivel') AS escolaridade,
            COALESCE(c.estado_civil, 'cadastro_nao_disponivel') AS estado_civil,
            COALESCE(c.tipo_moradia, 'cadastro_nao_disponivel') AS tipo_moradia,
            COALESCE(c.ocupacao, 'cadastro_nao_disponivel') AS ocupacao,

            c.idade_anos,
            c.renda_total,
            c.valor_credito,
            c.valor_anuidade,
            c.valor_bens,
            c.razao_credito_renda,
            c.razao_anuidade_renda,
            c.qtd_filhos,
            c.qtd_membros_familia,

            COALESCE(c.flg_inadimplencia_historica, 0) AS flg_inadimplencia_historica,
            COALESCE(c.flg_possui_carro, 0) AS flg_possui_carro,
            COALESCE(c.flg_possui_imovel, 0) AS flg_possui_imovel,
            COALESCE(c.flg_possui_celular, 0) AS flg_possui_celular,
            COALESCE(c.flg_celular_contatavel, 0) AS flg_celular_contatavel,
            COALESCE(c.flg_possui_telefone, 0) AS flg_possui_telefone,
            COALESCE(c.flg_possui_email, 0) AS flg_possui_email,

            -- Faixa etária para análise no Power BI
            CASE
                WHEN c.idade_anos IS NULL THEN 'idade_nao_informada'
                WHEN c.idade_anos < 25 THEN 'ate_24_anos'
                WHEN c.idade_anos >= 25 AND c.idade_anos < 35 THEN '25_a_34_anos'
                WHEN c.idade_anos >= 35 AND c.idade_anos < 45 THEN '35_a_44_anos'
                WHEN c.idade_anos >= 45 AND c.idade_anos < 60 THEN '45_a_59_anos'
                WHEN c.idade_anos >= 60 THEN '60_anos_ou_mais'
                ELSE 'idade_nao_informada'
            END AS faixa_idade,

            -- Faixa de renda para análise no Power BI
            CASE
                WHEN c.renda_total IS NULL THEN 'renda_nao_informada'
                WHEN c.renda_total <= 30000 THEN 'ate_30_mil'
                WHEN c.renda_total > 30000 AND c.renda_total <= 60000 THEN '30_a_60_mil'
                WHEN c.renda_total > 60000 AND c.renda_total <= 120000 THEN '60_a_120_mil'
                WHEN c.renda_total > 120000 AND c.renda_total <= 240000 THEN '120_a_240_mil'
                WHEN c.renda_total > 240000 THEN 'acima_240_mil'
                ELSE 'renda_nao_informada'
            END AS faixa_renda,

            -- Canal sugerido com base no cadastro disponível
            CASE
                WHEN c.id_cliente IS NULL THEN 'cadastro_nao_disponivel'
                WHEN c.flg_possui_email = 1 THEN 'email'
                WHEN c.flg_celular_contatavel = 1 THEN 'celular'
                WHEN c.flg_possui_celular = 1 THEN 'celular'
                WHEN c.flg_possui_telefone = 1 THEN 'telefone'
                ELSE 'canal_nao_identificado'
            END AS canal_sugerido,

            -- Prioridade para contato preventivo
            CASE
                WHEN b.nivel_risco = 'alto_risco'
                 AND b.maior_atraso_dias >= 30
                THEN 'prioridade_maxima'

                WHEN b.nivel_risco = 'alto_risco'
                THEN 'prioridade_alta'

                WHEN b.nivel_risco = 'medio_risco'
                THEN 'prioridade_media'

                WHEN b.nivel_risco = 'risco_desconhecido'
                THEN 'prioridade_revisao'

                ELSE 'prioridade_baixa'
            END AS prioridade_contato,

            -- Flag simples para segmentação no Power BI
            CASE
                WHEN b.nivel_risco IN ('alto_risco', 'medio_risco') THEN 1
                WHEN b.nivel_risco = 'risco_desconhecido' THEN 1
                ELSE 0
            END AS flg_priorizar_contato,

            -- Ação recomendada
            CASE
                WHEN b.nivel_risco = 'alto_risco'
                THEN 'lembrete_preventivo_reforcado'

                WHEN b.nivel_risco = 'medio_risco'
                THEN 'lembrete_preventivo_padrao'

                WHEN b.nivel_risco = 'baixo_risco'
                 AND b.perfil_pagamento = 'pagador_antecipado'
                THEN 'comunicacao_relacionamento'

                WHEN b.nivel_risco = 'baixo_risco'
                THEN 'lembrete_suave'

                WHEN b.nivel_risco = 'risco_desconhecido'
                THEN 'revisar_dados_pagamento'

                ELSE 'acao_nao_classificada'
            END AS acao_recomendada,

            -- Grupo de negócio para filtros simples
            CASE
                WHEN b.nivel_risco IN ('alto_risco', 'medio_risco')
                THEN 'clientes_prioritarios'

                WHEN b.nivel_risco = 'risco_desconhecido'
                THEN 'clientes_para_revisao'

                ELSE 'clientes_monitoramento'
            END AS grupo_negocio,

            -- Valor histórico associado aos clientes priorizados
            CASE
                WHEN b.nivel_risco IN ('alto_risco', 'medio_risco')
                THEN b.valor_previsto_total
                ELSE 0
            END AS valor_previsto_total_priorizado,

            current_timestamp AS dt_processamento_gold

        FROM read_parquet('{arquivo_silver_comportamento.as_posix()}') b
        LEFT JOIN read_parquet('{arquivo_silver_clientes.as_posix()}') c
            ON b.id_cliente = c.id_cliente
    )
    TO '{arquivo_gold_tmp.as_posix()}'
    (FORMAT PARQUET);
""")


# =============================================================================
# 5. SUBSTITUIÇÃO SEGURA DO ARQUIVO GOLD OFICIAL
# =============================================================================

if arquivo_gold.exists():
    arquivo_gold.unlink()
    print(f"Arquivo Gold anterior removido: {arquivo_gold}")

arquivo_gold_tmp.replace(arquivo_gold)

print(f"Gold de indicadores por cliente criada com sucesso: {arquivo_gold}")


# =============================================================================
# 6. VALIDAÇÃO RÁPIDA
# =============================================================================

resumo = con.execute(f"""
    SELECT
        COUNT(*) AS total_clientes,
        SUM(flg_cliente_com_cadastro) AS clientes_com_cadastro,
        COUNT(*) - SUM(flg_cliente_com_cadastro) AS clientes_sem_cadastro,
        ROUND(100.0 * SUM(flg_cliente_com_cadastro) / COUNT(*), 2) AS pct_clientes_com_cadastro,
        SUM(flg_priorizar_contato) AS clientes_priorizados,
        ROUND(SUM(valor_previsto_total_priorizado), 2) AS valor_previsto_total_priorizado
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nResumo da Gold:")
print(resumo)


resumo_risco = con.execute(f"""
    SELECT
        nivel_risco,
        COUNT(*) AS qtd_clientes,
        SUM(flg_priorizar_contato) AS qtd_priorizados,
        ROUND(SUM(valor_previsto_total), 2) AS valor_previsto_total
    FROM read_parquet('{arquivo_gold.as_posix()}')
    GROUP BY nivel_risco
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por nível de risco:")
print(resumo_risco)


resumo_prioridade = con.execute(f"""
    SELECT
        prioridade_contato,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_gold.as_posix()}')
    GROUP BY prioridade_contato
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por prioridade de contato:")
print(resumo_prioridade)


resumo_acao = con.execute(f"""
    SELECT
        acao_recomendada,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_gold.as_posix()}')
    GROUP BY acao_recomendada
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por ação recomendada:")
print(resumo_acao)


amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_gold.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Gold:")
print(amostra)

print("\nCriação da Gold de indicadores por cliente concluída com sucesso.")