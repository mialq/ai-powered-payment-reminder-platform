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

from pathlib import Path
import duckdb


# 1. DEFINIÇÃO DOS CAMINHOS DO PROJETO

# __file__ representa o caminho deste script.
# .resolve() transforma em caminho absoluto.
# .parents[1] sobe um nível acima da pasta scripts, chegando na raiz do projeto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Pasta onde estão os arquivos da camada Bronze.
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze"

# Pasta onde serão salvos os arquivos da camada Silver.
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

# Garante que a pasta Silver exista.
# Se não existir, ela será criada automaticamente.
SILVER_PATH.mkdir(parents=True, exist_ok=True)


# 2. DEFINIÇÃO DOS ARQUIVOS DE ENTRADA E SAÍDA

# Arquivo de entrada vindo da Bronze.
bronze_file = BRONZE_PATH / "bronze_installments_payments.parquet"

# Arquivo de saída que será criado na Silver.
silver_file = SILVER_PATH / "silver_installments_payments.parquet"

# 3. VALIDAÇÃO SIMPLES DO ARQUIVO DE ENTRADA

# Antes de tentar transformar, verificamos se o arquivo Bronze existe.
# Isso evita erro confuso caso o arquivo ainda não tenha sido criado.
if not bronze_file.exists():
    raise FileNotFoundError(f"Arquivo Bronze não encontrado: {bronze_file}")

# 4. CONEXÃO COM DUCKDB

# DuckDB será usado para ler o Parquet, aplicar SQL e gravar outro Parquet.
con = duckdb.connect()


# 5. TRANSFORMAÇÃO BRONZE -> SILVER

print("Iniciando transformação Bronze -> Silver...")
# Se o arquivo Silver já existir, apaga antes de recriar;
#Isso evita erro ao rodar o script mais de uma vez;

if silver_file.existis():
    silver_file.unlink()
    print(f'Arquivo Silver anterior removido: { silver_file}')

con.execute(f"""
    COPY (
        SELECT
          
            -- IDENTIFICADORES PRINCIPAIS
          
            CAST(SK_ID_CURR AS BIGINT) AS customer_id,
            CAST(SK_ID_PREV AS BIGINT) AS previous_contract_id,

            -- Número da versão da parcela.
            -- Mantemos como número, pois pode ser usado em análises futuras.
            CAST(NUM_INSTALMENT_VERSION AS DOUBLE) AS installment_version,

            -- Número da parcela dentro do contrato.
            CAST(NUM_INSTALMENT_NUMBER AS INTEGER) AS installment_number,
   
            -- CAMPOS DE TEMPO
            
            -- Dia previsto para pagamento.
            -- Atenção: não é uma data real; é um deslocamento em dias.
            CAST(DAYS_INSTALMENT AS DOUBLE) AS scheduled_payment_day_offset,

            -- Dia real em que o pagamento entrou.
            -- Atenção: não é uma data real; é um deslocamento em dias.
            CAST(DAYS_ENTRY_PAYMENT AS DOUBLE) AS actual_payment_day_offset,

            -- CAMPOS FINANCEIROS
   
            -- Valor previsto da parcela.
            CAST(AMT_INSTALMENT AS DOUBLE) AS expected_payment_amount,

            -- Valor efetivamente pago.
            CAST(AMT_PAYMENT AS DOUBLE) AS actual_payment_amount,
         
            -- REGRA DE NEGÓCIO: ATRASO DO PAGAMENTO
         
            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NULL OR DAYS_INSTALMENT IS NULL THEN NULL
                ELSE CAST(DAYS_ENTRY_PAYMENT AS DOUBLE) - CAST(DAYS_INSTALMENT AS DOUBLE)
            END AS days_delay,
         
            -- STATUS DO PAGAMENTO
           
            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NULL THEN 'UNKNOWN_PAYMENT_DATE'
                WHEN DAYS_INSTALMENT IS NULL THEN 'UNKNOWN_SCHEDULED_DATE'
                WHEN DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT < 0 THEN 'PAID_EARLY'
                WHEN DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT = 0 THEN 'PAID_ON_TIME'
                WHEN DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT > 0 THEN 'PAID_LATE'
                ELSE 'UNKNOWN'
            END AS payment_status,


            -- FLAGS DE COMPORTAMENTO DE PAGAMENTO
          
            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NOT NULL
                 AND DAYS_INSTALMENT IS NOT NULL
                 AND DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT > 0
                THEN 1
                ELSE 0
            END AS is_late,

            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NOT NULL
                 AND DAYS_INSTALMENT IS NOT NULL
                 AND DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT < 0
                THEN 1
                ELSE 0
            END AS is_paid_early,

            CASE
                WHEN DAYS_ENTRY_PAYMENT IS NOT NULL
                 AND DAYS_INSTALMENT IS NOT NULL
                 AND DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT = 0
                THEN 1
                ELSE 0
            END AS is_paid_on_time,

            -- REGRA FINANCEIRA: DIFERENÇA ENTRE VALOR PAGO E VALOR PREVISTO
          
            CASE
                WHEN AMT_PAYMENT IS NULL OR AMT_INSTALMENT IS NULL THEN NULL
                ELSE CAST(AMT_PAYMENT AS DOUBLE) - CAST(AMT_INSTALMENT AS DOUBLE)
            END AS payment_amount_difference,


            -- STATUS DO VALOR PAGO
          
            CASE
                WHEN AMT_PAYMENT IS NULL THEN 'UNKNOWN_PAYMENT_AMOUNT'
                WHEN AMT_INSTALMENT IS NULL THEN 'UNKNOWN_EXPECTED_AMOUNT'
                WHEN AMT_PAYMENT < AMT_INSTALMENT THEN 'PARTIAL_PAYMENT'
                WHEN AMT_PAYMENT = AMT_INSTALMENT THEN 'FULL_PAYMENT'
                WHEN AMT_PAYMENT > AMT_INSTALMENT THEN 'OVERPAYMENT'
                ELSE 'UNKNOWN'
            END AS payment_amount_status,

            -- FLAGS DE QUALIDADE DOS DADOS
            
            CASE
                WHEN SK_ID_CURR IS NULL
                  OR SK_ID_PREV IS NULL
                  OR DAYS_INSTALMENT IS NULL
                  OR DAYS_ENTRY_PAYMENT IS NULL
                  OR AMT_INSTALMENT IS NULL
                  OR AMT_PAYMENT IS NULL
                THEN 1
                ELSE 0
            END AS has_null_critical_fields,

            CASE
                WHEN AMT_INSTALMENT < 0 OR AMT_PAYMENT < 0
                THEN 1
                ELSE 0
            END AS has_negative_amount,

            CASE
                WHEN AMT_PAYMENT < AMT_INSTALMENT
                THEN 1
                ELSE 0
            END AS has_partial_payment,

            CASE
                WHEN AMT_PAYMENT > AMT_INSTALMENT
                THEN 1
                ELSE 0
            END AS has_overpayment,


            -- METADADOS TÉCNICOS
     
            'installments_payments.csv' AS source_file,
            'bronze_installments_payments.parquet' AS bronze_file_name,
            current_timestamp AS silver_processed_at

        FROM read_parquet('{bronze_file.as_posix()}')
    )
    TO '{silver_file.as_posix()}'
    (FORMAT PARQUET);
""")

print(f"Silver criada com sucesso: {silver_file}")


# 6. VALIDAÇÃO RÁPIDA DA SILVER


total_rows = con.execute(f"""
    SELECT COUNT(*) 
    FROM read_parquet('{silver_file.as_posix()}')
""").fetchone()[0]

print(f"Total de registros na Silver: {total_rows}")


# 7. AMOSTRA DOS DADOS TRANSFORMADOS

sample_df = con.execute(f"""
    SELECT
        customer_id,
        previous_contract_id,
        scheduled_payment_day_offset,
        actual_payment_day_offset,
        expected_payment_amount,
        actual_payment_amount,
        days_delay,
        payment_status,
        payment_amount_status,
        is_late,
        has_null_critical_fields
    FROM read_parquet('{silver_file.as_posix()}')
    LIMIT 10
""").df()

print("Amostra da Silver:")
print(sample_df)


# 8. RESUMO DE QUALIDADE DOS DADOS

quality_df = con.execute(f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(has_null_critical_fields) AS rows_with_null_critical_fields,
        SUM(has_negative_amount) AS rows_with_negative_amount,
        SUM(has_partial_payment) AS rows_with_partial_payment,
        SUM(has_overpayment) AS rows_with_overpayment,
        SUM(is_late) AS total_late_payments,
        ROUND(100.0 * SUM(is_late) / COUNT(*), 2) AS late_payment_rate_percent
    FROM read_parquet('{silver_file.as_posix()}')
""").df()

print("Resumo de qualidade e atraso:")
print(quality_df)