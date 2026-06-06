# AI-Powered Payment Reminder & Delinquency Prevention Platform

## Informações do Projeto

| Item            | Descrição                                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| Projeto         | AI-Powered Payment Reminder & Delinquency Prevention Platform                                                    |
| Autor           | Michele Alves Queiroz Potenza Teixeira                                                                           |
| Objetivo        | Plataforma analítica para prevenção de inadimplência através de comunicação preventiva e Inteligência Artificial |
| Dataset         | Home Credit Default Risk                                                                                         |
| Fonte dos Dados | Kaggle                                                                                                           |
| Domínio         | Serviços Financeiros / Crédito                                                                                   |
| Status          | Em Desenvolvimento                                                                                               |
| Versão          | MVP 1.0                                                                                                          |

---

# 1. Visão Geral

Este projeto tem como objetivo desenvolver uma plataforma analítica capaz de identificar clientes com maior probabilidade de atraso em pagamentos e apoiar ações preventivas de comunicação antes do vencimento das parcelas.

A solução utiliza conceitos modernos de Engenharia de Dados, Analytics Engineering, Inteligência Artificial Generativa, Agentes de IA e arquitetura Medalhão (Raw, Bronze, Silver e Gold).

O projeto foi inspirado em um cenário real de negócio proposto durante um processo seletivo para uma posição de Engenharia de Dados e Analytics no setor financeiro.

---

# 2. Contexto de Negócio

Instituições financeiras possuem milhões de clientes com contratos, financiamentos, cartões e empréstimos ativos.

Uma parcela significativa dos atrasos ocorre não necessariamente por incapacidade financeira, mas por esquecimento, desorganização ou falta de comunicação adequada.

Atualmente muitas operações realizam ações reativas de cobrança somente após o vencimento.

Uma abordagem mais eficiente consiste em identificar clientes com maior risco de atraso antes do vencimento e executar ações preventivas de relacionamento.

---

# 3. Problema de Negócio

Como identificar clientes que devem receber lembretes preventivos antes do vencimento de suas parcelas, priorizando aqueles com maior risco de atraso e reduzindo a inadimplência da carteira?

---

# 4. Objetivos da Solução

A solução deverá ser capaz de:

* Identificar clientes com parcelas próximas do vencimento.
* Calcular indicadores de comportamento de pagamento.
* Classificar clientes por risco de atraso.
* Priorizar clientes para comunicação preventiva.
* Disponibilizar informações para gestores através de dashboards.
* Permitir consultas em linguagem natural através de agentes de IA.

---

# 5. Perguntas de Negócio

A solução deverá responder perguntas como:

* Quais clientes possuem parcelas vencendo nos próximos dias?
* Quais clientes apresentam maior risco de atraso?
* Quais clientes devem ser priorizados hoje?
* Quais contratos possuem histórico recorrente de atraso?
* Como justificar a priorização de um cliente?
* Quais fatores influenciam o comportamento de pagamento?

---

# 6. Escopo do MVP

A primeira versão da solução utilizará principalmente as tabelas:

* application_train.csv
* installments_payments.csv

Objetivos do MVP:

* Construção da arquitetura Medalhão.
* Desenvolvimento das camadas Bronze, Silver e Gold.
* Criação de métricas de risco.
* Construção de dashboard executivo.
* Desenvolvimento de agente de IA para consultas em linguagem natural.

---

# 7. Escopo Futuro

Evoluções previstas:

* Integração com bureau.csv
* Integração com previous_application.csv
* Integração com credit_card_balance.csv
* Integração com POS_CASH_balance.csv
* Modelo preditivo de Machine Learning
* Integração com WhatsApp
* Integração com SMS
* Sistema de recomendação de ações de cobrança

---

# 8. Benefícios Esperados

* Redução da inadimplência.
* Aumento da taxa de pagamento em dia.
* Melhor experiência do cliente.
* Priorização inteligente da operação.
* Redução de custos operacionais.
* Apoio à tomada de decisão baseada em dados.

---

# 9. Indicadores de Sucesso

Os principais indicadores monitorados serão:

* Taxa de pagamento em dia.
* Taxa de atraso.
* Clientes priorizados.
* Clientes recuperados após comunicação preventiva.
* Efetividade das ações de relacionamento.
* Redução da inadimplência da carteira.

---

# 10. Visão Geral da Solução

Fonte de Dados
↓
Raw
↓
Bronze
↓
Silver
↓
Gold
↓
Dashboard
↓
AI Agent

A camada Gold será consumida tanto pelo dashboard quanto pelo agente de IA, permitindo que gestores realizem consultas em linguagem natural sobre risco, vencimentos e priorização de clientes.
