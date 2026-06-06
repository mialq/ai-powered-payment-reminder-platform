# 07 - Business Question Mapping

## Projeto

AI-Powered Payment Reminder & Delinquency Prevention Platform

## Objetivo deste documento

Este documento apresenta o raciocínio utilizado para conectar a dor de negócio às decisões técnicas do projeto.

A proposta é mostrar como uma pergunta de negócio foi transformada em:

* entendimento dos dados;
* criação de métricas;
* organização em camadas;
* tabela analítica;
* consumo por Power BI;
* possibilidade de uso com IA/RAG.

---

## 1. Qual é a dor do negócio?

A dor do negócio é reduzir atrasos de pagamento e prevenir inadimplência por meio de lembretes mais inteligentes antes do vencimento.

Em vez de enviar o mesmo lembrete para todos os clientes, a solução busca identificar quais clientes possuem maior chance de atrasar com base no histórico de pagamento.

Pergunta central do projeto:

```text
Como identificar clientes com maior risco de atraso e acionar lembretes preventivos antes do vencimento?
```

---

## 2. Quais dados respondem essa dor?

A principal fonte utilizada foi a tabela `installments_payments`, que contém o histórico de pagamentos dos clientes.

Campos principais utilizados:

| Campo original     | Significado no projeto                    |
| ------------------ | ----------------------------------------- |
| SK_ID_CURR         | Identificador do cliente                  |
| SK_ID_PREV         | Identificador do contrato anterior        |
| DAYS_INSTALMENT    | Dia previsto para pagamento               |
| DAYS_ENTRY_PAYMENT | Dia real em que o pagamento foi realizado |
| AMT_INSTALMENT     | Valor previsto da parcela                 |
| AMT_PAYMENT        | Valor efetivamente pago                   |

Esses campos permitem comparar o vencimento previsto com o pagamento real, identificando se o cliente pagou antes, no vencimento ou em atraso.

---

## 3. Qual métrica representa o problema?

A principal métrica criada foi `days_delay`.

Regra:

```text
days_delay = actual_payment_day_offset - scheduled_payment_day_offset
```

Equivalente aos campos originais:

```text
DAYS_DELAY = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT
```

Interpretação:

|      Resultado | Interpretação                          |
| -------------: | -------------------------------------- |
| days_delay < 0 | Cliente pagou antes do vencimento      |
| days_delay = 0 | Cliente pagou exatamente no vencimento |
| days_delay > 0 | Cliente pagou em atraso                |

A partir dessa métrica, foram criadas outras métricas analíticas:

| Métrica                   | Descrição                                           |
| ------------------------- | --------------------------------------------------- |
| total_late_payments       | Quantidade de pagamentos atrasados                  |
| late_payment_rate_percent | Percentual de pagamentos atrasados                  |
| average_delay_days        | Média geral de atraso ou antecipação                |
| average_late_delay_days   | Média de dias de atraso considerando apenas atrasos |
| max_delay_days            | Maior atraso registrado                             |
| risk_level                | Classificação de risco do cliente                   |

A métrica mais importante para o negócio é `late_payment_rate_percent`, pois indica a proporção de atrasos no histórico do cliente.

---

## 4. Qual tabela analítica entrega essa resposta?

A tabela analítica que entrega essa resposta está na camada Gold:

```text
data/gold/gold_customer_payment_behavior.parquet
```

Essa tabela possui uma linha por cliente e consolida o comportamento histórico de pagamento.

Principais colunas da Gold:

| Coluna                    | Descrição                                       |
| ------------------------- | ----------------------------------------------- |
| customer_id               | Identificador do cliente                        |
| total_installments        | Total de parcelas do cliente                    |
| valid_installments        | Total de parcelas válidas para análise          |
| total_late_payments       | Total de pagamentos atrasados                   |
| total_paid_early          | Total de pagamentos antecipados                 |
| total_paid_on_time        | Total de pagamentos no vencimento               |
| late_payment_rate_percent | Percentual de atraso do cliente                 |
| average_delay_days        | Média geral de dias de atraso ou antecipação    |
| average_late_delay_days   | Média de atraso apenas dos pagamentos atrasados |
| max_delay_days            | Maior atraso registrado                         |
| payment_behavior_profile  | Perfil histórico de pagamento                   |
| risk_level                | Nível de risco do cliente                       |

Com essa tabela, a área de negócio consegue responder:

```text
Quais clientes possuem maior risco de atraso?
```

---

## 5. Como a área de negócio vai consumir isso?

A área de negócio pode consumir a Gold de três formas principais.

### 5.1 Power BI

A tabela Gold pode alimentar um dashboard com indicadores como:

* total de clientes;
* clientes por nível de risco;
* percentual de clientes de alto risco;
* distribuição de comportamento de pagamento;
* média de dias de atraso;
* clientes com maior histórico de atraso.

### 5.2 Régua de comunicação

A classificação de risco pode apoiar uma régua de lembretes preventivos.

| Risco        | Estratégia sugerida                                     |
| ------------ | ------------------------------------------------------- |
| LOW_RISK     | Lembrete simples próximo ao vencimento                  |
| MEDIUM_RISK  | Lembrete antecipado com reforço de vencimento           |
| HIGH_RISK    | Comunicação mais antecipada, recorrente e personalizada |
| UNKNOWN_RISK | Necessita análise adicional antes de acionar            |

### 5.3 IA/RAG

A IA pode ser usada para apoiar a explicação e recomendação da estratégia de contato.

Exemplos de perguntas que o agente poderia responder:

```text
Por que esse cliente foi classificado como HIGH_RISK?
```

```text
Qual histórico justifica o envio de lembrete antecipado?
```

```text
Qual tipo de comunicação é mais adequada para esse perfil de cliente?
```

O RAG pode recuperar a documentação do projeto, as regras de classificação e os dados tratados para gerar respostas mais contextualizadas e rastreáveis.

---

## Conclusão

Este projeto parte de uma dor real de negócio: reduzir atrasos e prevenir inadimplência.

A solução construída organiza os dados em camadas, cria métricas de comportamento de pagamento e entrega uma visão analítica por cliente.

Com isso, a empresa pode deixar de enviar lembretes genéricos para todos os clientes e passar a priorizar clientes com maior risco, aumentando a efetividade das ações preventivas.

Resumo do raciocínio:

```text
Dor do negócio
    ↓
Histórico de pagamentos
    ↓
Cálculo de atraso
    ↓
Classificação do comportamento
    ↓
Classificação de risco
    ↓
Power BI e IA para apoiar decisão
```
