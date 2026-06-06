# Architecture

## Informações do Documento

| Item            | Descrição                                                     |
| --------------- | ------------------------------------------------------------- |
| Projeto         | AI-Powered Payment Reminder & Delinquency Prevention Platform |
| Autor           | Michele Alves Queiroz Potenza Teixeira                        |
| Dataset         | Home Credit Default Risk                                      |
| Fonte dos Dados | Kaggle                                                        |
| Domínio         | Serviços Financeiros / Crédito                                |
| Documento       | Architecture                                                  |
| Versão          | 1.0                                                           |
| Status          | Em Desenvolvimento                                            |

---

# Objetivo

Documentar a arquitetura de dados da solução, incluindo fluxo de ingestão, processamento, disponibilização de métricas e integração com Inteligência Artificial.

---

# Arquitetura Conceitual

```text
Home Credit Dataset
        ↓
       Raw
        ↓
     Bronze
        ↓
     Silver
        ↓
      Gold
        ↓
 ┌─────────────┐
 │ Dashboard   │
 └─────────────┘
        ↓
 ┌─────────────┐
 │ AI Agent    │
 └─────────────┘
```

---

# Camada Raw

## Objetivo

Armazenar os arquivos originais recebidos da fonte sem qualquer modificação.

## Arquivos

* application_train.csv
* installments_payments.csv
* previous_application.csv
* bureau.csv
* credit_card_balance.csv
* POS_CASH_balance.csv

---

# Camada Bronze

## Objetivo

Realizar a ingestão dos dados mantendo sua estrutura original.

## Características

* Sem regras de negócio.
* Sem remoção de registros.
* Sem agregações.
* Conversão para formato analítico.

## Saídas Esperadas

* bronze_application_train
* bronze_installments_payments

---

# Camada Silver

## Objetivo

Padronizar e enriquecer os dados.

## Processamentos

* Tratamento de valores nulos.
* Padronização de tipos.
* Cálculo de atraso.
* Criação de indicadores operacionais.
* Enriquecimento do perfil do cliente.

## Principais Entidades

* customers
* contracts
* installments

---

# Camada Gold

## Objetivo

Disponibilizar dados prontos para consumo analítico.

## Principais Tabelas

### gold_customer_risk

Contém score de risco e perfil consolidado do cliente.

### gold_payment_reminders

Contém clientes com parcelas próximas do vencimento.

### gold_collection_priority

Contém clientes priorizados para comunicação preventiva.

---

# Dashboard

## Objetivo

Disponibilizar visão executiva para gestores.

## Indicadores

* Clientes com vencimento próximo.
* Clientes prioritários.
* Distribuição de risco.
* Histórico de atrasos.

---

# AI Agent

## Objetivo

Permitir consultas em linguagem natural.

## Exemplos

* Quais clientes devo priorizar hoje?
* Quais contratos vencem amanhã?
* Quem possui maior risco de atraso?
* Explique por que este cliente foi priorizado.

---

# Evolução Futura

* dbt
* DuckDB
* LangGraph
* OpenAI
* RAG
* WhatsApp
* Power BI
* Machine Learning
