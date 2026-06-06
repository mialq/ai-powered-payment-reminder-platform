# Data Dictionary

## Informações do Documento

| Item            | Descrição                                                     |
| --------------- | ------------------------------------------------------------- |
| Projeto         | AI-Powered Payment Reminder & Delinquency Prevention Platform |
| Autor           | Michele Alves Queiroz Potenza Teixeira                        |
| Dataset         | Home Credit Default Risk                                      |
| Fonte dos Dados | Kaggle                                                        |
| Domínio         | Serviços Financeiros / Crédito                                |
| Documento       | Data Dictionary                                               |
| Versão          | 1.0                                                           |
| Status          | Em Desenvolvimento                                            |

---

## Objetivo

Documentar os principais campos utilizados na construção da solução analítica.

Este documento será atualizado conforme novas colunas forem incorporadas às camadas Silver e Gold.

---

# application_train.csv

## Descrição

Tabela principal contendo informações cadastrais, financeiras e demográficas dos clientes.

### Campos Utilizados no MVP

| Campo               | Tipo    | Descrição                                   | Utilização               |
| ------------------- | ------- | ------------------------------------------- | ------------------------ |
| SK_ID_CURR          | ID      | Identificador único do cliente              | Chave principal          |
| TARGET              | Integer | Cliente apresentou dificuldade de pagamento | Variável alvo            |
| AMT_CREDIT          | Decimal | Valor do crédito solicitado                 | Perfil financeiro        |
| AMT_INCOME_TOTAL    | Decimal | Renda total do cliente                      | Capacidade financeira    |
| AMT_ANNUITY         | Decimal | Valor da parcela/anuidade                   | Comprometimento de renda |
| DAYS_BIRTH          | Integer | Idade do cliente em dias                    | Perfil demográfico       |
| DAYS_EMPLOYED       | Integer | Tempo de emprego em dias                    | Estabilidade financeira  |
| CODE_GENDER         | String  | Sexo do cliente                             | Segmentação              |
| NAME_EDUCATION_TYPE | String  | Escolaridade                                | Perfil do cliente        |
| NAME_FAMILY_STATUS  | String  | Estado civil                                | Perfil do cliente        |
| CNT_CHILDREN        | Integer | Quantidade de filhos                        | Perfil familiar          |
| FLAG_OWN_CAR        | Boolean | Possui veículo                              | Perfil patrimonial       |
| FLAG_OWN_REALTY     | Boolean | Possui imóvel                               | Perfil patrimonial       |

---

# installments_payments.csv

## Descrição

Tabela contendo histórico de pagamento das parcelas dos contratos.

### Campos Utilizados no MVP

| Campo                 | Tipo    | Descrição                 | Utilização            |
| --------------------- | ------- | ------------------------- | --------------------- |
| SK_ID_CURR            | ID      | Identificador do cliente  | Relacionamento        |
| SK_ID_PREV            | ID      | Identificador do contrato | Relacionamento        |
| NUM_INSTALMENT_NUMBER | Integer | Número da parcela         | Controle              |
| DAYS_INSTALMENT       | Integer | Data prevista da parcela  | Cálculo de vencimento |
| DAYS_ENTRY_PAYMENT    | Integer | Data efetiva do pagamento | Cálculo de atraso     |
| AMT_INSTALMENT        | Decimal | Valor previsto da parcela | Métricas financeiras  |
| AMT_PAYMENT           | Decimal | Valor efetivamente pago   | Métricas financeiras  |

---

# Campos Derivados (Silver)

Os campos abaixo serão criados durante o processamento da camada Silver.

| Campo              | Descrição                                   |
| ------------------ | ------------------------------------------- |
| DAYS_DELAY         | Quantidade de dias de atraso                |
| PAYMENT_STATUS     | Pago em dia, atrasado ou adiantado          |
| PAYMENT_DIFFERENCE | Diferença entre valor previsto e valor pago |
| CUSTOMER_DELAY_AVG | Média histórica de atraso do cliente        |

---

# Campos Analíticos (Gold)

Os campos abaixo serão utilizados pela camada Gold.

| Campo               | Descrição                           |
| ------------------- | ----------------------------------- |
| CUSTOMER_RISK_SCORE | Score de risco do cliente           |
| REMINDER_PRIORITY   | Prioridade para envio de lembrete   |
| NEXT_PAYMENT_DUE    | Próximo vencimento                  |
| CUSTOMER_SEGMENT    | Segmentação do cliente              |
| DELINQUENCY_FLAG    | Indicador de risco de inadimplência |
