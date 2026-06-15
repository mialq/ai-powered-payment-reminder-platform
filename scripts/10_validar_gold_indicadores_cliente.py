"""
Script: 10_validar_gold_indicadores_cliente.py

Objetivo:
    Validar a camada Gold de indicadores por cliente.

Entrada:
    data/gold/gold_indicadores_cliente.parquet

Responsabilidade desta validação:
    - Confirmar se o arquivo Gold existe.
    - Validar volume e duplicidade de clientes.
    - Validar colunas esperadas.
    - Validar padrão de nomes em português, caixa baixa e snake_case.
    - Validar campos categóricos e flags.
    - Validar regras de negócio da priorização.
    - Validar cobertura cadastral.
    - Comparar volume com a Silver de comportamento, quando disponível.
"""

from pathlib import Path
import re
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_gold = raiz_projeto / "data" / "gold"
caminho_silver = raiz_projeto / "data" / "silver"

arquivo_gold = caminho_gold / "gold_indicadores_cliente.parquet"
arquivo_silver_comportamento = caminho_silver / "silver_comportamento_pagamento_cliente.parquet"


# =============================================================================
# 2. VALIDAÇÃO DE EXISTÊNCIA
# =============================================================================

if not arquivo_gold.exists():
    raise FileNotFoundError(f"Arquivo Gold não encontrado: {arquivo_gold}")

print("Arquivo Gold encontrado:")
print(arquivo_gold)


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
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nResumo de volume:")
print(resumo_volume)


# =============================================================================
# 5. ESTRUTURA DA TABELA
# =============================================================================

schema = con.execute(f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nColunas da Gold:")
print(schema)


# =============================================================================
# 6. VALIDAÇÃO DE COLUNAS ESPERADAS
# =============================================================================

colunas_esperadas = {
    "id_cliente",
    "nivel_risco",
    "perfil_pagamento",
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
    "flg_cliente_com_cadastro",
    "status_cadastro",
    "genero",
    "tipo_renda",
    "escolaridade",
    "estado_civil",
    "tipo_moradia",
    "ocupacao",
    "idade_anos",
    "renda_total",
    "valor_credito",
    "valor_anuidade",
    "valor_bens",
    "razao_credito_renda",
    "razao_anuidade_renda",
    "qtd_filhos",
    "qtd_membros_familia",
    "flg_inadimplencia_historica",
    "flg_possui_carro",
    "flg_possui_imovel",
    "flg_possui_celular",
    "flg_celular_contatavel",
    "flg_possui_telefone",
    "flg_possui_email",
    "faixa_idade",
    "faixa_renda",
    "canal_sugerido",
    "prioridade_contato",
    "flg_priorizar_contato",
    "acao_recomendada",
    "grupo_negocio",
    "valor_previsto_total_priorizado",
    "dt_processamento_gold",
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
# 7. VALIDAÇÃO DE PADRÃO DOS NOMES DAS COLUNAS
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
    FROM read_parquet('{arquivo_gold.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Gold:")
print(amostra)


# =============================================================================
# 9. RESUMOS PRINCIPAIS DE NEGÓCIO
# =============================================================================

resumo_risco = con.execute(f"""
    SELECT
        nivel_risco,
        COUNT(*) AS qtd_clientes,
        SUM(flg_priorizar_contato) AS qtd_priorizados,
        ROUND(SUM(valor_previsto_total), 2) AS valor_previsto_total,
        ROUND(SUM(valor_previsto_total_priorizado), 2) AS valor_previsto_total_priorizado
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


resumo_cadastro = con.execute(f"""
    SELECT
        status_cadastro,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_gold.as_posix()}')
    GROUP BY status_cadastro
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por status de cadastro:")
print(resumo_cadastro)


# =============================================================================
# 10. VALIDAÇÃO DE VALORES CATEGÓRICOS PERMITIDOS
# =============================================================================

validacao_categorias = con.execute(f"""
    SELECT
        SUM(CASE WHEN nivel_risco NOT IN (
            'baixo_risco',
            'medio_risco',
            'alto_risco',
            'risco_desconhecido'
        ) THEN 1 ELSE 0 END) AS nivel_risco_invalido,

        SUM(CASE WHEN perfil_pagamento NOT IN (
            'pagador_antecipado',
            'pagador_no_prazo',
            'baixo_atraso',
            'atraso_moderado',
            'alto_atraso',
            'comportamento_desconhecido'
        ) THEN 1 ELSE 0 END) AS perfil_pagamento_invalido,

        SUM(CASE WHEN status_cadastro NOT IN (
            'cliente_com_cadastro',
            'cliente_sem_cadastro'
        ) THEN 1 ELSE 0 END) AS status_cadastro_invalido,

        SUM(CASE WHEN prioridade_contato NOT IN (
            'prioridade_baixa',
            'prioridade_media',
            'prioridade_alta',
            'prioridade_maxima',
            'prioridade_revisao'
        ) THEN 1 ELSE 0 END) AS prioridade_contato_invalida,

        SUM(CASE WHEN acao_recomendada NOT IN (
            'lembrete_preventivo_reforcado',
            'lembrete_preventivo_padrao',
            'comunicacao_relacionamento',
            'lembrete_suave',
            'revisar_dados_pagamento',
            'acao_nao_classificada'
        ) THEN 1 ELSE 0 END) AS acao_recomendada_invalida,

        SUM(CASE WHEN grupo_negocio NOT IN (
            'clientes_prioritarios',
            'clientes_para_revisao',
            'clientes_monitoramento'
        ) THEN 1 ELSE 0 END) AS grupo_negocio_invalido

    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação de valores categóricos permitidos:")
print(validacao_categorias)


# =============================================================================
# 11. VALIDAÇÃO DE CAIXA BAIXA EM CATEGÓRICOS
# =============================================================================

validacao_caixa_baixa = con.execute(f"""
    SELECT
        SUM(CASE WHEN nivel_risco <> LOWER(nivel_risco) THEN 1 ELSE 0 END) AS nivel_risco_com_maiuscula,
        SUM(CASE WHEN perfil_pagamento <> LOWER(perfil_pagamento) THEN 1 ELSE 0 END) AS perfil_pagamento_com_maiuscula,
        SUM(CASE WHEN status_cadastro <> LOWER(status_cadastro) THEN 1 ELSE 0 END) AS status_cadastro_com_maiuscula,
        SUM(CASE WHEN prioridade_contato <> LOWER(prioridade_contato) THEN 1 ELSE 0 END) AS prioridade_contato_com_maiuscula,
        SUM(CASE WHEN acao_recomendada <> LOWER(acao_recomendada) THEN 1 ELSE 0 END) AS acao_recomendada_com_maiuscula,
        SUM(CASE WHEN grupo_negocio <> LOWER(grupo_negocio) THEN 1 ELSE 0 END) AS grupo_negocio_com_maiuscula
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação de caixa baixa em campos categóricos:")
print(validacao_caixa_baixa)


# =============================================================================
# 12. VALIDAÇÃO DE FLAGS BINÁRIAS
# =============================================================================

validacao_flags = con.execute(f"""
    SELECT
        SUM(CASE WHEN flg_cliente_com_cadastro NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_cliente_com_cadastro_fora_padrao,
        SUM(CASE WHEN flg_inadimplencia_historica NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_inadimplencia_historica_fora_padrao,
        SUM(CASE WHEN flg_possui_carro NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_possui_carro_fora_padrao,
        SUM(CASE WHEN flg_possui_imovel NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_possui_imovel_fora_padrao,
        SUM(CASE WHEN flg_possui_celular NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_possui_celular_fora_padrao,
        SUM(CASE WHEN flg_celular_contatavel NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_celular_contatavel_fora_padrao,
        SUM(CASE WHEN flg_possui_telefone NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_possui_telefone_fora_padrao,
        SUM(CASE WHEN flg_possui_email NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_possui_email_fora_padrao,
        SUM(CASE WHEN flg_priorizar_contato NOT IN (0, 1) THEN 1 ELSE 0 END) AS flg_priorizar_contato_fora_padrao
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação de flags binárias:")
print(validacao_flags)


# =============================================================================
# 13. VALIDAÇÃO DAS REGRAS DE NEGÓCIO
# =============================================================================

validacao_regras_negocio = con.execute(f"""
    SELECT
        SUM(
            CASE
                WHEN nivel_risco IN ('alto_risco', 'medio_risco', 'risco_desconhecido')
                 AND flg_priorizar_contato <> 1
                THEN 1 ELSE 0
            END
        ) AS priorizacao_ausente_para_risco_relevante,

        SUM(
            CASE
                WHEN nivel_risco = 'baixo_risco'
                 AND flg_priorizar_contato <> 0
                THEN 1 ELSE 0
            END
        ) AS baixo_risco_priorizado_incorretamente,

        SUM(
            CASE
                WHEN nivel_risco IN ('alto_risco', 'medio_risco')
                 AND valor_previsto_total_priorizado <> valor_previsto_total
                THEN 1 ELSE 0
            END
        ) AS valor_priorizado_incorreto_para_risco,

        SUM(
            CASE
                WHEN nivel_risco NOT IN ('alto_risco', 'medio_risco')
                 AND valor_previsto_total_priorizado <> 0
                THEN 1 ELSE 0
            END
        ) AS valor_priorizado_incorreto_para_nao_priorizado,

        SUM(
            CASE
                WHEN flg_cliente_com_cadastro = 1
                 AND status_cadastro <> 'cliente_com_cadastro'
                THEN 1 ELSE 0
            END
        ) AS status_cadastro_incorreto_para_cliente_com_cadastro,

        SUM(
            CASE
                WHEN flg_cliente_com_cadastro = 0
                 AND status_cadastro <> 'cliente_sem_cadastro'
                THEN 1 ELSE 0
            END
        ) AS status_cadastro_incorreto_para_cliente_sem_cadastro

    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação das regras de negócio:")
print(validacao_regras_negocio)


# =============================================================================
# 14. VALIDAÇÃO NUMÉRICA
# =============================================================================

validacao_numerica = con.execute(f"""
    SELECT
        SUM(CASE WHEN qtd_parcelas_validas > qtd_parcelas_total THEN 1 ELSE 0 END) AS parcelas_validas_maior_que_total,
        SUM(CASE WHEN taxa_atraso_pct < 0 OR taxa_atraso_pct > 100 THEN 1 ELSE 0 END) AS taxa_atraso_fora_intervalo,
        SUM(CASE WHEN maior_atraso_dias < 0 THEN 1 ELSE 0 END) AS maior_atraso_negativo,
        SUM(CASE WHEN maior_antecipacao_dias < 0 THEN 1 ELSE 0 END) AS maior_antecipacao_negativa,
        SUM(CASE WHEN valor_previsto_total < 0 THEN 1 ELSE 0 END) AS valor_previsto_total_negativo,
        SUM(CASE WHEN valor_pago_total < 0 THEN 1 ELSE 0 END) AS valor_pago_total_negativo,
        SUM(CASE WHEN valor_previsto_total_priorizado < 0 THEN 1 ELSE 0 END) AS valor_priorizado_negativo
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação numérica:")
print(validacao_numerica)


# =============================================================================
# 15. COBERTURA CADASTRAL
# =============================================================================

cobertura = con.execute(f"""
    SELECT
        COUNT(*) AS total_clientes,
        SUM(flg_cliente_com_cadastro) AS clientes_com_cadastro,
        COUNT(*) - SUM(flg_cliente_com_cadastro) AS clientes_sem_cadastro,
        ROUND(100.0 * SUM(flg_cliente_com_cadastro) / COUNT(*), 2) AS pct_clientes_com_cadastro
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nCobertura cadastral:")
print(cobertura)


# =============================================================================
# 16. COMPARAÇÃO COM SILVER DE COMPORTAMENTO
# =============================================================================

if arquivo_silver_comportamento.exists():
    comparacao_silver = con.execute(f"""
        SELECT
            (
                SELECT COUNT(*)
                FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
            ) AS total_clientes_silver_comportamento,

            (
                SELECT COUNT(*)
                FROM read_parquet('{arquivo_gold.as_posix()}')
            ) AS total_clientes_gold,

            (
                SELECT COUNT(*)
                FROM read_parquet('{arquivo_silver_comportamento.as_posix()}')
            )
            -
            (
                SELECT COUNT(*)
                FROM read_parquet('{arquivo_gold.as_posix()}')
            ) AS diferenca_volume
    """).df()

    print("\nComparação de volume com a Silver de comportamento:")
    print(comparacao_silver)
else:
    print("\nSilver de comportamento não encontrada. Comparação de volume não executada.")


# =============================================================================
# 17. VALIDAÇÃO DE DATA DE PROCESSAMENTO
# =============================================================================

validacao_processamento = con.execute(f"""
    SELECT
        MIN(dt_processamento_gold) AS menor_dt_processamento,
        MAX(dt_processamento_gold) AS maior_dt_processamento,
        COUNT(DISTINCT dt_processamento_gold) AS qtd_datas_processamento
    FROM read_parquet('{arquivo_gold.as_posix()}')
""").df()

print("\nValidação da data de processamento:")
print(validacao_processamento)


print("\nValidação da Gold de indicadores por cliente concluída.")