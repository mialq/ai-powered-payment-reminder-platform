"""
Script: 05_silver_to_gold_customer_behavior.py

Objetivo:
    Criar a camada Gold com o comportamento de pagamento por cliente.

Entrada:
    data/silver/silver_installments_payments.parquet

Saída:
    data/gold/gold_customer_payment_behavior.parquet

Esta Gold será usada para:
    - Power BI
    - análise de risco de atraso
    - futuro agente de IA/RAG
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_PATH = PROJECT_ROOT / "data" / "silver"
GOLD_PATH = PROJECT_ROOT / "data" / "gold"

GOLD_PATH.mkdir(parents=True, exist_ok=True)

silver_file = SILVER_PATH / "silver_installments_payments.parquet"
gold_file = GOLD_PATH / "gold_customer_payment_behavior.parquet"


# =============================================================================
# 2. VALIDAÇÕES INICIAIS
# =============================================================================

if not silver_file.exists():
    raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_file}")

# Se a Gold já existir, remove para recriar do zero
if gold_file.exists():
    gold_file.unlink()
    print(f"Arquivo Gold anterior removido: {gold_file}")


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()

print("Iniciando criação da Gold por cliente...")


# =============================================================================
# 4. CRIAÇÃO DA GOLD
# =============================================================================

con.execute(f"""
    COPY (
        WITH customer_metrics AS (
            SELECT
                customer_id,

                COUNT(*) AS total_installments,

                COUNT(*) FILTER (
                    WHERE payment_status != 'UNKNOWN_PAYMENT_DATE'
                ) AS valid_installments,

                SUM(is_late) AS total_late_payments,
                SUM(is_paid_early) AS total_paid_early,
                SUM(is_paid_on_time) AS total_paid_on_time,

                ROUND(
                    100.0 * SUM(is_late) 
                    / NULLIF(COUNT(*) FILTER (WHERE payment_status != 'UNKNOWN_PAYMENT_DATE'), 0),
                    2
                ) AS late_payment_rate_percent,

                ROUND(AVG(days_delay), 2) AS average_delay_days,

                ROUND(
                    AVG(CASE WHEN days_delay > 0 THEN days_delay END),
                    2
                ) AS average_late_delay_days,

                MAX(days_delay) AS max_delay_days,

                ROUND(SUM(expected_payment_amount), 2) AS total_expected_payment_amount,
                ROUND(SUM(actual_payment_amount), 2) AS total_actual_payment_amount,

                ROUND(
                    SUM(actual_payment_amount) - SUM(expected_payment_amount),
                    2
                ) AS total_payment_difference,

                SUM(has_null_critical_fields) AS total_rows_with_null_critical_fields,
                SUM(has_partial_payment) AS total_partial_payments,
                SUM(has_overpayment) AS total_overpayments

            FROM read_parquet('{silver_file.as_posix()}')
            GROUP BY customer_id
        )

        SELECT
            customer_id,
            total_installments,
            valid_installments,
            total_late_payments,
            total_paid_early,
            total_paid_on_time,
            late_payment_rate_percent,
            average_delay_days,
            average_late_delay_days,
            max_delay_days,
            total_expected_payment_amount,
            total_actual_payment_amount,
            total_payment_difference,
            total_rows_with_null_critical_fields,
            total_partial_payments,
            total_overpayments,

            CASE
                WHEN valid_installments = 0 THEN 'UNKNOWN_BEHAVIOR'

                WHEN total_late_payments = 0 
                 AND total_paid_early >= total_paid_on_time
                THEN 'EARLY_PAYER'

                WHEN total_late_payments = 0
                THEN 'ON_TIME_PAYER'

                WHEN late_payment_rate_percent < 10
                THEN 'LOW_DELAY_BEHAVIOR'

                WHEN late_payment_rate_percent >= 10
                 AND late_payment_rate_percent < 30
                THEN 'MODERATE_DELAY_BEHAVIOR'

                WHEN late_payment_rate_percent >= 30
                THEN 'HIGH_DELAY_BEHAVIOR'

                ELSE 'UNKNOWN_BEHAVIOR'
            END AS payment_behavior_profile,

            CASE
                WHEN valid_installments = 0 THEN 'UNKNOWN_RISK'

                WHEN late_payment_rate_percent >= 30
                  OR max_delay_days >= 30
                THEN 'HIGH_RISK'

                WHEN late_payment_rate_percent >= 10
                  OR average_late_delay_days >= 5
                  OR max_delay_days >= 10
                THEN 'MEDIUM_RISK'

                ELSE 'LOW_RISK'
            END AS risk_level,

            current_timestamp AS gold_processed_at

        FROM customer_metrics
    )
    TO '{gold_file.as_posix()}'
    (FORMAT PARQUET);
""")

print(f"Gold criada com sucesso: {gold_file}")


# =============================================================================
# 5. VALIDAÇÃO RÁPIDA
# =============================================================================

total_customers = con.execute(f"""
    SELECT COUNT(*)
    FROM read_parquet('{gold_file.as_posix()}')
""").fetchone()[0]

print(f"Total de clientes na Gold: {total_customers}")

risk_summary = con.execute(f"""
    SELECT
        risk_level,
        COUNT(*) AS total_customers
    FROM read_parquet('{gold_file.as_posix()}')
    GROUP BY risk_level
    ORDER BY total_customers DESC
""").df()

print("\nResumo por nível de risco:")
print(risk_summary)

sample = con.execute(f"""
    SELECT *
    FROM read_parquet('{gold_file.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Gold:")
print(sample)

print("\nGold por cliente concluída com sucesso.")