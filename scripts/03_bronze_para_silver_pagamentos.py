"""
Script: 03_bronze_to_silver.py

Objetivo:
    Transformar a tabela bronze_installments_payments.parquet em uma tabela Silver.

Contexto do projeto:
    AI-Powered Payment Reminder & Delinquency Prevention Platform

    A tabela installments_payments contém o histórico de pagamentos dos clientes.
    A partir dela, vamos criar variáveis de negócio para entender o comportamento
    de pagamento e futuramente prever/identificar clientes com maior risco de atraso.

Camada Bronze:
    - Dados quase brutos.
    - Mantém estrutura próxima do arquivo original.
    - Pouca ou nenhuma regra de negócio.

Camada Silver:
    - Dados tratados e padronizados.
    - Colunas renomeadas para melhor entendimento.
    - Criação de regras de negócio.
    - Criação de campos de qualidade dos dados.

Principais regras criadas:
    days_delay = actual_payment_day_offset - scheduled_payment_day_offset

    Se days_delay < 0:
        Cliente pagou antes do vencimento.

    Se days_delay = 0:
        Cliente pagou exatamente no vencimento.

    Se days_delay > 0:
        Cliente pagou atrasado.

Observação importante:
    Os campos DAYS_INSTALMENT e DAYS_ENTRY_PAYMENT não são datas reais.
    Eles representam deslocamentos em dias em relação a uma data de referência
    do dataset. Por isso usamos o sufixo "day_offset".
"""

# pathlib é usado para montar caminhos de arquivos de forma segura.
# duckdb é usado para ler, transformar e gravar arquivos Parquet usando SQL.
from pathlib import Path
import duckdb

# 1. DEFINIÇÃO DOS CAMINHOS DO PROJETO

# __file__ representa o caminho deste script.
# .resolve() transforma em caminho absoluto.
# .parents[1] sobe um nível acima da pasta scripts, chegando na raiz do projeto.
raiz_projeto = Path(__file__).resolve().parents[1]

# Pasta onde estão os arquivos da camada Bronze.
caminho_bronze = raiz_projeto / "data" / "bronze"

# Pasta onde serão salvos os arquivos da camada Silver.
caminho_silver = raiz_projeto / "data" / "silver"

# Garante que a pasta Silver exista.
# Se não existir, ela será criada automaticamente.
caminho_silver.mkdir(parents=True, exist_ok=True)


# =============================================================================
# 2. DEFINIÇÃO DOS ARQUIVOS DE ENTRADA E SAÍDA
# =============================================================================

# Arquivo de entrada vindo da Bronze.
arquivo_bronze = caminho_bronze / "bronze_pagamentos_parcelas.parquet"

# Arquivo oficial de saída da Silver.
arquivo_silver = caminho_silver / "silver_pagamentos_parcelas.parquet"

# Arquivo temporário usado para gravação segura.
arquivo_silver_temporario = caminho_silver / "silver_pagamentos_parcelas_tmp.parquet"

# =============================================================================
# 3. LIMPEZA CONTROLADA DE ARQUIVOS ANTIGOS DA SILVER
# =============================================================================

# Remove apenas arquivos controlados por este script.
# Não apagamos a pasta Silver inteira para evitar excluir outras tabelas,
# arquivos históricos ou dados de outras etapas do pipeline.
arquivos_para_remover = [
    # Arquivo temporário novo
    caminho_silver / "silver_pagamentos_parcelas_tmp.parquet",

    # Arquivos antigos antes da padronização dos nomes
    caminho_silver / "silver_installments_payments.parquet",
    caminho_silver / "silver_installments_payments_tmp.parquet",
]

for arquivo in arquivos_para_remover:
    if arquivo.exists():
        arquivo.unlink()
        print(f"Arquivo removido da Silver: {arquivo}")



# 4. VALIDAÇÃO SIMPLES DO ARQUIVO DE ENTRADA

# Antes de tentar transformar, verificamos se o arquivo Bronze existe.
# Isso evita erro confuso caso o arquivo ainda não tenha sido criado.
if not arquivo_bronze.exists():
    raise FileNotFoundError(f"Arquivo Bronze não encontrado: {arquivo_bronze}")

# 5. CONEXÃO COM DUCKDB

# DuckDB será usado para ler o Parquet, aplicar SQL e gravar outro Parquet.
con = duckdb.connect()


# 6. ********************TRANSFORMAÇÃO BRONZE -> SILVER****************************

print("Iniciando transformação Bronze -> Silver...")

# DIAGNOSTICO DE NULOS NA BRONZE...
# Este diagnóstico mostra onde existem campos vazios na origem.
# No dataset atual, os nulos aparecem principalmente em:
# - DAYS_ENTRY_PAYMENT: dia real do pagamento ausente
# - AMT_PAYMENT: valor pago ausente
#
# Quando esses dois campos estão nulos, interpretamos como pagamento não registrado
# na origem, e não como pagamento no prazo ou pagamento zerado.

print("Diagnosticando nulos na Bronze...")

null_profile_df = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        SUM(CASE WHEN SK_ID_CURR IS NULL THEN 1 ELSE 0 END) AS nulos_id_cliente,
        SUM(CASE WHEN SK_ID_PREV IS NULL THEN 1 ELSE 0 END) AS nulos_id_contrato,
        SUM(CASE WHEN DAYS_INSTALMENT IS NULL THEN 1 ELSE 0 END) AS nulos_dia_previsto,
        SUM(CASE WHEN DAYS_ENTRY_PAYMENT IS NULL THEN 1 ELSE 0 END) AS nulos_dia_pagamento,
        SUM(CASE WHEN AMT_INSTALMENT IS NULL THEN 1 ELSE 0 END) AS nulos_valor_previsto,
        SUM(CASE WHEN AMT_PAYMENT IS NULL THEN 1 ELSE 0 END) AS nulos_valor_pago
    FROM read_parquet('{arquivo_bronze.as_posix()}')
""").df()

print("Diagnóstico de nulos na Bronze:")
print(null_profile_df)

# A transformação abaixo cria a camada Silver.
# Nesta etapa, os dados ainda estão em nível de parcela/pagamento.
#
# Regras aplicadas:
# - Colunas são renomeadas para português e snake_case.
# - Status são traduzidos para português e caixa baixa.
# - Diferença entre pagamento real e vencimento é calculada.
# - Atraso e antecipação são separados em campos diferentes.
# - Campos nulos críticos recebem flags específicas.
# - Valores ausentes não são escondidos: eles são sinalizados por status e flags.

con.execute(f"""
    COPY (
        WITH base AS (
            SELECT
                SK_ID_CURR,
                SK_ID_PREV,
                NUM_INSTALMENT_VERSION,
                NUM_INSTALMENT_NUMBER,
                DAYS_INSTALMENT,
                DAYS_ENTRY_PAYMENT,
                AMT_INSTALMENT,
                AMT_PAYMENT,

                CASE
                    WHEN DAYS_ENTRY_PAYMENT IS NULL OR DAYS_INSTALMENT IS NULL THEN NULL
                    ELSE CAST(DAYS_ENTRY_PAYMENT AS DOUBLE) - CAST(DAYS_INSTALMENT AS DOUBLE)
                END AS dif_dias_vencimento_raw,

                CASE
                    WHEN AMT_PAYMENT IS NULL OR AMT_INSTALMENT IS NULL THEN NULL
                    ELSE CAST(AMT_PAYMENT AS DOUBLE) - CAST(AMT_INSTALMENT AS DOUBLE)
                END AS dif_valor_raw

            FROM read_parquet('{arquivo_bronze.as_posix()}')
        )

        SELECT
            -- identificadores
            COALESCE(CAST(SK_ID_CURR AS BIGINT), -1) AS id_cliente,
            COALESCE(CAST(SK_ID_PREV AS BIGINT), -1) AS id_contrato_anterior,

            -- parcela
            COALESCE(CAST(NUM_INSTALMENT_VERSION AS DOUBLE), 0) AS versao_parcela,
            COALESCE(CAST(NUM_INSTALMENT_NUMBER AS INTEGER), 0) AS numero_parcela,

            -- campos de tempo
            -- esses campos representam deslocamento em dias em relacao a uma data de referencia
            COALESCE(CAST(DAYS_INSTALMENT AS DOUBLE), 0) AS dias_previsto_ref,
            COALESCE(CAST(DAYS_ENTRY_PAYMENT AS DOUBLE), 0) AS dias_pagamento_ref,

            -- diferenca geral:
            -- negativo = pagou antes
            -- zero = pagou no prazo ou dado desconhecido tratado
            -- positivo = pagou atrasado
            CAST(dif_dias_vencimento_raw AS DOUBLE) AS dif_dias_vencimento,

            -- atraso tratado: nunca fica negativo
            CASE
                WHEN dif_dias_vencimento_raw IS NULL THEN 0
                WHEN dif_dias_vencimento_raw > 0 THEN CAST(dif_dias_vencimento_raw AS DOUBLE)
                ELSE 0
            END AS dias_atraso,

            -- antecipacao tratada: nunca fica negativa
            CASE
                WHEN dif_dias_vencimento_raw IS NULL THEN 0
                WHEN dif_dias_vencimento_raw < 0 THEN ABS(CAST(dif_dias_vencimento_raw AS DOUBLE))
                ELSE 0
            END AS dias_antecipacao,

            -- campos financeiros
            COALESCE(CAST(AMT_INSTALMENT AS DOUBLE), 0) AS valor_previsto,
            COALESCE(CAST(AMT_PAYMENT AS DOUBLE), 0) AS valor_pago,
            COALESCE(CAST(dif_valor_raw AS DOUBLE), 0) AS dif_valor_pago_previsto,

            -- status do pagamento em portugues, minusculo e snake_case
            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NULL AND AMT_PAYMENT IS NULL THEN 'sem_pagamento_registrado'
                WHEN DAYS_ENTRY_PAYMENT IS NULL THEN 'data_pagamento_desconhecida'
                WHEN DAYS_INSTALMENT IS NULL THEN 'data_prevista_desconhecida'
                WHEN dif_dias_vencimento_raw < 0 THEN 'pago_antecipado'
                WHEN dif_dias_vencimento_raw = 0 THEN 'pago_no_prazo'
                WHEN dif_dias_vencimento_raw > 0 THEN 'pago_em_atraso'
                ELSE 'desconhecido'
            END AS status_pagamento,

            -- status do valor pago em portugues, minusculo e snake_case
            CASE
                WHEN AMT_PAYMENT IS NULL THEN 'valor_pago_nao_registrado'
                WHEN AMT_INSTALMENT IS NULL THEN 'valor_previsto_nao_registrado'
                WHEN AMT_PAYMENT < AMT_INSTALMENT THEN 'pagamento_parcial'
                WHEN AMT_PAYMENT = AMT_INSTALMENT THEN 'pagamento_integral'
                WHEN AMT_PAYMENT > AMT_INSTALMENT THEN 'pagamento_acima_previsto'
                ELSE 'valor_pagamento_nao_classificado'
            END AS status_valor_pagamento,

            -- flags de comportamento
            CASE
                WHEN dif_dias_vencimento_raw > 0 THEN 1
                ELSE 0
            END AS flg_pagamento_atrasado,

            CASE
                WHEN dif_dias_vencimento_raw < 0 THEN 1
                ELSE 0
            END AS flg_pagamento_antecipado,

            CASE
                WHEN dif_dias_vencimento_raw = 0 THEN 1
                ELSE 0
            END AS flg_pagamento_no_prazo,

            -- flags financeiras
            CASE
                WHEN AMT_PAYMENT < AMT_INSTALMENT THEN 1
                ELSE 0
            END AS flg_pagamento_parcial,

            CASE
                WHEN AMT_PAYMENT > AMT_INSTALMENT THEN 1
                ELSE 0
            END AS flg_pagamento_acima_previsto,

            CASE
                WHEN AMT_INSTALMENT < 0 OR AMT_PAYMENT < 0 THEN 1
                ELSE 0
            END AS flg_valor_negativo,

            -- flags especificas de nulos
            CASE WHEN SK_ID_CURR IS NULL THEN 1 ELSE 0 END AS flg_id_cliente_nulo,
            CASE WHEN SK_ID_PREV IS NULL THEN 1 ELSE 0 END AS flg_id_contrato_nulo,
            CASE WHEN DAYS_INSTALMENT IS NULL THEN 1 ELSE 0 END AS flg_dia_previsto_nulo,
            CASE WHEN DAYS_ENTRY_PAYMENT IS NULL THEN 1 ELSE 0 END AS flg_dia_pagamento_nulo,
            CASE WHEN AMT_INSTALMENT IS NULL THEN 1 ELSE 0 END AS flg_valor_previsto_nulo,
            CASE WHEN AMT_PAYMENT IS NULL THEN 1 ELSE 0 END AS flg_valor_pago_nulo,

            -- flag consolidada de qualidade
            CASE
                WHEN SK_ID_CURR IS NULL
                  OR SK_ID_PREV IS NULL
                  OR DAYS_INSTALMENT IS NULL
                  OR DAYS_ENTRY_PAYMENT IS NULL
                  OR AMT_INSTALMENT IS NULL
                  OR AMT_PAYMENT IS NULL
                THEN 1
                ELSE 0
            END AS flg_nulo_critico,

            -- quantidade de campos criticos nulos na linha
            (
                CASE WHEN SK_ID_CURR IS NULL THEN 1 ELSE 0 END +
                CASE WHEN SK_ID_PREV IS NULL THEN 1 ELSE 0 END +
                CASE WHEN DAYS_INSTALMENT IS NULL THEN 1 ELSE 0 END +
                CASE WHEN DAYS_ENTRY_PAYMENT IS NULL THEN 1 ELSE 0 END +
                CASE WHEN AMT_INSTALMENT IS NULL THEN 1 ELSE 0 END +
                CASE WHEN AMT_PAYMENT IS NULL THEN 1 ELSE 0 END
            ) AS qtd_nulos_criticos,

            -- metadados
            'installments_payments.csv' AS arquivo_origem,
            'bronze_pagamentos_parcelas.parquet' AS arquivo_bronze,
            current_timestamp AS dt_processamento_silver

        FROM base
    )
    TO '{arquivo_silver_temporario.as_posix()}'
    (FORMAT PARQUET);
""")


# Substituição segura do arquivo Silver oficial
# A transformação grava primeiro em um arquivo temporário.
# Somente após o processamento terminar com sucesso, o arquivo Silver antigo é removido
# e o arquivo temporário passa a ser o novo arquivo oficial da camada Silver.
# Isso evita deixar a Silver corrompida ou incompleta caso o processo seja interrompido.
if arquivo_silver.exists():
    arquivo_silver.unlink()
    print(f"Arquivo Silver anterior removido: {arquivo_silver}")

arquivo_silver_temporario.replace(arquivo_silver)

print(f"Silver criada com sucesso: {arquivo_silver}")


# 7. VALIDAÇÃO RÁPIDA DA SILVER
# Validação de volume da camada Silver
# Conta a quantidade total de registros gerados no arquivo Silver.
# O volume deve ser compatível com a camada Bronze, já que esta etapa trata e padroniza
# os dados, mas não deve remover registros sem uma regra explícita de descarte.

total_rows = con.execute(f"""
    SELECT COUNT(*) 
    FROM read_parquet('{arquivo_silver.as_posix()}')
""").fetchone()[0]

print(f"Total de registros na Silver: {total_rows}")


# 8. AMOSTRA DOS DADOS TRANSFORMADOS
# Exibe uma pequena amostra dos dados gerados na camada Silver.
# Essa conferência visual ajuda a validar se:
# - os nomes das colunas foram padronizados em português e snake_case;
# - os campos de atraso e antecipação foram calculados corretamente;
# - os status de pagamento estão em português e caixa baixa;
# - as flags de qualidade foram criadas corretamente.

sample_df = con.execute(f"""
    SELECT
        id_cliente,
        id_contrato_anterior,
        dias_previsto_ref,
        dias_pagamento_ref,
        valor_previsto,
        valor_pago,
        dif_dias_vencimento,
        dias_atraso,
        dias_antecipacao,
        status_pagamento,
        status_valor_pagamento,
        flg_pagamento_atrasado,
        flg_nulo_critico,
        qtd_nulos_criticos
    FROM read_parquet('{arquivo_silver.as_posix()}')
    LIMIT 10
""").df()

print("Amostra da Silver:")
print(sample_df)

# 9. RESUMO DE QUALIDADE DOS DADOS
# Consolida indicadores básicos para validar a qualidade da camada Silver.
# Essa etapa permite verificar:
# - quantidade total de registros processados;
# - registros com campos críticos nulos;
# - quantidade total de campos críticos nulos;
# - registros com valores financeiros negativos;
# - pagamentos parciais;
# - pagamentos acima do previsto;
# - volume e percentual de pagamentos em atraso.

quality_df = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        SUM(flg_nulo_critico) AS registros_com_nulo_critico,
        SUM(qtd_nulos_criticos) AS total_campos_criticos_nulos,
        SUM(flg_valor_negativo) AS registros_com_valor_negativo,
        SUM(flg_pagamento_parcial) AS total_pagamentos_parciais,
        SUM(flg_pagamento_acima_previsto) AS total_pagamentos_acima_previsto,
        SUM(flg_pagamento_atrasado) AS total_pagamentos_atrasados,
        ROUND(100.0 * SUM(flg_pagamento_atrasado) / COUNT(*), 2) AS taxa_atraso_pct
    FROM read_parquet('{arquivo_silver
                        .as_posix()}')
""").df()

print("Resumo de qualidade e atraso:")
print(quality_df)
