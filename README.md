# AI-Powered Payment Reminder & Delinquency Prevention Platform

## Visão Geral

Este projeto tem como objetivo criar uma solução de Engenharia de Dados e Analytics para identificar clientes com maior risco de atraso no pagamento e apoiar estratégias de lembrete preventivo antes do vencimento.

A proposta é transformar dados brutos de pagamentos em uma base analítica confiável, capaz de alimentar dashboards no Power BI e, futuramente, um agente de IA com RAG para recomendar ações personalizadas de comunicação.

---

## Problema de Negócio

Empresas financeiras precisam reduzir atrasos de pagamento e prevenir inadimplência. Enviar o mesmo lembrete para todos os clientes pode ser pouco eficiente, pois clientes possuem comportamentos de pagamento diferentes.

A pergunta central do projeto é:

> Como identificar clientes com maior risco de atraso e acionar lembretes preventivos antes do vencimento?

---

## Arquitetura do Projeto

O projeto foi estruturado em camadas:

```text
data/
├── raw
├── bronze
├── silver
└── gold
```

### Raw

Camada com os arquivos originais em CSV.

### Bronze

Camada com os dados convertidos para Parquet, preservando a estrutura original.

### Silver

Camada com dados tratados, padronizados e enriquecidos com regras de negócio.

### Gold

Camada analítica consolidada por cliente, com métricas de comportamento de pagamento e classificação de risco.

---

## Stack Utilizada

* Python
* DuckDB
* Parquet
* VS Code
* Power BI
* OpenAI
* RAG
* GitHub

---

## Principal Regra de Negócio

A principal métrica criada foi `days_delay`.

```text
days_delay = actual_payment_day_offset - scheduled_payment_day_offset
```

Interpretação:

|      Resultado | Significado             |
| -------------: | ----------------------- |
| days_delay < 0 | Pagamento antecipado    |
| days_delay = 0 | Pagamento no vencimento |
| days_delay > 0 | Pagamento atrasado      |

---

## Resultado da Camada Silver

A camada Silver classificou os pagamentos em:

| Status               |     Total |
| -------------------- | --------: |
| PAID_EARLY           | 9.309.477 |
| PAID_ON_TIME         | 3.146.350 |
| PAID_LATE            | 1.146.669 |
| UNKNOWN_PAYMENT_DATE |     2.905 |

Taxa geral de atraso encontrada:

```text
8,43%
```

---

## Resultado da Camada Gold

A camada Gold consolidou o comportamento de pagamento por cliente.

Total de clientes analisados:

```text
339.587
```

Distribuição por nível de risco:

| Risk Level   | Total de Clientes |
| ------------ | ----------------: |
| LOW_RISK     |           210.109 |
| MEDIUM_RISK  |            92.276 |
| HIGH_RISK    |            37.193 |
| UNKNOWN_RISK |                 9 |

---

## Tabela Analítica Final

Arquivo final da camada Gold:

```text
data/gold/gold_customer_payment_behavior.parquet
```

Essa tabela possui uma linha por cliente e contém métricas como:

* total de parcelas;
* total de pagamentos atrasados;
* taxa de atraso;
* média de dias de atraso;
* maior atraso registrado;
* perfil de comportamento de pagamento;
* nível de risco.

---

## Possíveis Usos

A solução pode ser utilizada para:

* criar dashboards no Power BI;
* segmentar clientes por risco;
* apoiar estratégias de lembrete preventivo;
* priorizar clientes com maior probabilidade de atraso;
* alimentar um agente de IA com contexto de negócio e dados tratados.

---

## Próximos Passos

* Criar dashboard no Power BI.
* Criar indicadores visuais por nível de risco.
* Desenvolver documentação do agente de IA.
* Implementar RAG para responder perguntas com base nas regras do projeto.
* Publicar o projeto no GitHub.
