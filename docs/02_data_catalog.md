# Data Catalog

## Informações do Documento

| Item            | Descrição                                                     |
| --------------- | ------------------------------------------------------------- |
| Projeto         | AI-Powered Payment Reminder & Delinquency Prevention Platform |
| Autor           | Michele Alves Queiroz Potenza Teixeira                        |
| Dataset         | Home Credit Default Risk                                      |
| Fonte dos Dados | Kaggle                                                        |
| Domínio         | Serviços Financeiros / Crédito                                |
| Documento       | Data Catalog                                                  |
| Versão          | 1.0                                                           |
| Status          | Em Desenvolvimento                                            |

---

## Visão Geral

Este documento descreve as tabelas utilizadas no projeto AI-Powered Payment Reminder & Delinquency Prevention Platform.

O objetivo do catálogo é fornecer uma visão centralizada dos ativos de dados disponíveis, sua finalidade de negócio, granularidade, relacionamentos e utilização dentro da solução.

---

## Resumo das Tabelas

| Tabela                    | Descrição                                   | Prioridade |
| ------------------------- | ------------------------------------------- | ---------- |
| application_train.csv     | Perfil do cliente e solicitação de crédito  | Alta       |
| installments_payments.csv | Histórico de pagamento das parcelas         | Altíssima  |
| previous_application.csv  | Solicitações anteriores de crédito          | Média      |
| bureau.csv                | Histórico de crédito em outras instituições | Média      |
| credit_card_balance.csv   | Histórico de cartão de crédito              | Baixa      |
| POS_CASH_balance.csv      | Histórico de financiamentos parcelados      | Baixa      |

---

# application_train.csv

## Objetivo

Armazenar informações cadastrais, financeiras e demográficas dos clientes que solicitaram crédito.

## Granularidade

Uma linha por solicitação de crédito.

## Chave Principal

SK_ID_CURR

## Principais Informações

* Perfil do cliente
* Informações financeiras
* Informações familiares
* Informações profissionais
* Valor do crédito
* Variável alvo de inadimplência (TARGET)

## Utilização no Projeto

* Construção do perfil do cliente
* Segmentação
* Classificação de risco
* Enriquecimento das análises de negócio

---

# installments_payments.csv

## Objetivo

Armazenar o histórico de pagamento das parcelas dos contratos.

## Granularidade

Uma linha por parcela.

## Chaves Principais

* SK_ID_CURR
* SK_ID_PREV

## Principais Informações

* Valor previsto da parcela
* Valor efetivamente pago
* Data prevista de pagamento
* Data efetiva de pagamento

## Utilização no Projeto

* Cálculo de atraso
* Comportamento histórico de pagamento
* Construção do score de risco
* Priorização de clientes
* Definição de lembretes preventivos

---

# previous_application.csv

## Objetivo

Armazenar histórico de solicitações anteriores de crédito.

## Granularidade

Uma linha por solicitação anterior.

## Chaves Principais

* SK_ID_PREV
* SK_ID_CURR

## Utilização no Projeto

* Histórico de relacionamento
* Perfil de contratação
* Evolução futura da solução

---

# bureau.csv

## Objetivo

Armazenar histórico de crédito do cliente em outras instituições financeiras.

## Granularidade

Uma linha por operação reportada ao bureau.

## Chaves Principais

* SK_ID_BUREAU
* SK_ID_CURR

## Utilização no Projeto

* Enriquecimento de risco
* Visão externa do cliente
* Evolução futura do score

---

# credit_card_balance.csv

## Objetivo

Armazenar histórico mensal de utilização de cartão de crédito.

## Granularidade

Uma linha por cartão e mês.

## Utilização no Projeto

Não será utilizado no MVP.

Poderá ser incorporado em versões futuras para enriquecer o perfil financeiro do cliente.

---

# POS_CASH_balance.csv

## Objetivo

Armazenar histórico mensal de financiamentos parcelados.

## Granularidade

Uma linha por contrato e mês.

## Utilização no Projeto

Não será utilizado no MVP.

Poderá ser incorporado em versões futuras para enriquecer análises de comportamento financeiro.

---

## Tabelas Utilizadas no MVP

A primeira versão da solução utilizará prioritariamente:

* application_train.csv
* installments_payments.csv

Estas tabelas são suficientes para construção da solução inicial de prevenção de inadimplência e comunicação preventiva.


