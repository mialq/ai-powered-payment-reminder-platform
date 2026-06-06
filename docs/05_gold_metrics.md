# 05 - Gold Metrics

## Projeto

AI-Powered Payment Reminder & Delinquency Prevention Platform

## Objetivo da camada Gold

A camada Gold tem como objetivo consolidar o comportamento de pagamento dos clientes a partir da tabela tratada na camada Silver.

Enquanto a Silver analisa cada pagamento individualmente, a Gold agrega os dados por cliente, permitindo identificar padrões de atraso, comportamento financeiro e nível de risco.

Essa camada será usada como base para:

* análise no Power BI;
* segmentação de clientes;
* criação de indicadores de inadimplência;
* apoio ao agente de IA para recomendação de lembretes preventivos.

---

## Fonte de dados

Arquivo de entrada:

```text
data/silver/silver_installments_payments.parquet
```

Arquivo de saída:

```text
data/gold/gold_customer_payment_behavior.parquet
```

---

## Granularidade da tabela Gold

A tabela Gold possui uma linha por cliente.

Chave principal analítica:

```text
customer_id
```

Cada registro representa o histórico consolidado de pagamentos de um cliente.

---

## Métricas criadas

### total_installments

Quantidade total de parcelas encontradas para o cliente.

### valid_installments

Quantidade de parcelas com informação válida de pagamento.

### total_late_payments

Quantidade de pagamentos realizados após o vencimento.

### total_paid_early

Quantidade de pagamentos realizados antes do vencimento.

### total_paid_on_time

Quantidade de pagamentos realizados exatamente no vencimento.

### late_payment_rate_percent

Percentual de pagamentos atrasados do cliente.

Regra:

```text
late_payment_rate_percent = total_late_payments / valid_installments * 100
```

### average_delay_days

Média geral de dias de atraso ou antecipação.

Valores negativos indicam pagamento antecipado.

### average_late_delay_days

Média de dias de atraso considerando apenas pagamentos atrasados.

### max_delay_days

Maior atraso registrado para o cliente.

### total_expected_payment_amount

Valor total previsto das parcelas.

### total_actual_payment_amount

Valor total efetivamente pago.

### total_payment_difference

Diferença entre o valor pago e o valor previsto.

Regra:

```text
total_payment_difference = total_actual_payment_amount - total_expected_payment_amount
```

### total_partial_payments

Quantidade de pagamentos com valor menor que o previsto.

### total_overpayments

Quantidade de pagamentos com valor maior que o previsto.

### total_rows_with_null_critical_fields

Quantidade de registros do cliente com campos críticos nulos.

---

## Classificação de comportamento de pagamento

A coluna `payment_behavior_profile` classifica o comportamento histórico do cliente.

Regras utilizadas:

| Perfil                  | Regra                                                             |
| ----------------------- | ----------------------------------------------------------------- |
| UNKNOWN_BEHAVIOR        | Cliente sem parcelas válidas                                      |
| EARLY_PAYER             | Cliente sem atrasos e com predominância de pagamentos antecipados |
| ON_TIME_PAYER           | Cliente sem atrasos                                               |
| LOW_DELAY_BEHAVIOR      | Cliente com taxa de atraso menor que 10%                          |
| MODERATE_DELAY_BEHAVIOR | Cliente com taxa de atraso entre 10% e 30%                        |
| HIGH_DELAY_BEHAVIOR     | Cliente com taxa de atraso maior ou igual a 30%                   |

---

## Classificação de risco

A coluna `risk_level` classifica o risco de atraso do cliente.

Regras utilizadas:

| Risco        | Regra                                                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------------------------------- |
| UNKNOWN_RISK | Cliente sem parcelas válidas                                                                                               |
| HIGH_RISK    | Taxa de atraso maior ou igual a 30% ou atraso máximo maior ou igual a 30 dias                                              |
| MEDIUM_RISK  | Taxa de atraso maior ou igual a 10%, ou média de atraso maior ou igual a 5 dias, ou atraso máximo maior ou igual a 10 dias |
| LOW_RISK     | Cliente com baixo histórico de atraso                                                                                      |

---

## Resultado da Gold

Após a criação da camada Gold, foram encontrados os seguintes volumes por nível de risco:

| risk_level   | total_customers |
| ------------ | --------------: |
| LOW_RISK     |         210.109 |
| MEDIUM_RISK  |          92.276 |
| HIGH_RISK    |          37.193 |
| UNKNOWN_RISK |               9 |

Total de clientes na Gold:

```text
339.587
```

---

## Interpretação de negócio

A maior parte dos clientes está classificada como `LOW_RISK`, indicando bom comportamento histórico de pagamento.

Clientes `MEDIUM_RISK` e `HIGH_RISK` devem ser priorizados em estratégias de lembrete preventivo, pois apresentam maior histórico de atraso ou atrasos mais severos.

A classificação de risco poderá ser utilizada para personalizar a régua de comunicação:

| Risco       | Estratégia sugerida                                     |
| ----------- | ------------------------------------------------------- |
| LOW_RISK    | lembrete simples próximo ao vencimento                  |
| MEDIUM_RISK | lembrete antecipado com reforço de vencimento           |
| HIGH_RISK   | comunicação mais antecipada, recorrente e personalizada |

---

## Uso futuro no projeto

A tabela `gold_customer_payment_behavior.parquet` será utilizada em três frentes principais:

1. Power BI
   Criação de dashboards com indicadores de atraso, perfil de clientes e distribuição de risco.

2. IA Generativa
   Apoio ao agente de IA para explicar o comportamento de pagamento do cliente.

3. RAG
   Recuperação de contexto de negócio e regras de classificação para justificar recomendações de lembrete.

---

## Status

Camada Gold criada e validada com sucesso.
