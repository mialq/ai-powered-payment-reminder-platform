# Entendimento de Negócio

Este documento descreve o entendimento de negócio do projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

O projeto simula uma solução analítica para identificar clientes com maior risco de atraso e apoiar estratégias de lembrete preventivo antes do vencimento.

---

## 1. Contexto do Problema

Empresas que trabalham com crédito, parcelamento, financiamento ou cobrança precisam acompanhar o comportamento de pagamento dos clientes.

Quando um cliente atrasa o pagamento, a empresa pode ter impactos como:

* aumento da inadimplência;
* piora no fluxo de caixa;
* aumento de custos operacionais de cobrança;
* necessidade de ações reativas;
* pior experiência para o cliente;
* perda de oportunidade de prevenção.

Em muitos cenários, a empresa só age depois que o atraso já aconteceu.

Este projeto propõe uma abordagem preventiva: usar dados históricos de pagamento para identificar clientes com maior risco e priorizar ações antes do vencimento.

---

## 2. Pergunta Central de Negócio

A pergunta principal do projeto é:

> Como identificar clientes com maior risco de atraso e priorizar ações de lembrete preventivo antes do vencimento?

Essa pergunta foi quebrada em perguntas menores:

| Pergunta                                                   | Objetivo                            |
| ---------------------------------------------------------- | ----------------------------------- |
| O cliente costuma pagar antecipado, no prazo ou em atraso? | Entender o comportamento histórico  |
| Qual é a taxa de atraso do cliente?                        | Medir frequência de atraso          |
| Qual foi o maior atraso histórico do cliente?              | Medir severidade do atraso          |
| O cliente deve ser priorizado para contato?                | Apoiar decisão operacional          |
| Qual ação deve ser recomendada?                            | Definir estratégia de comunicação   |
| Qual canal pode ser usado?                                 | Apoiar contato com base no cadastro |
| O cliente possui cadastro disponível?                      | Medir cobertura cadastral           |
| Qual valor está associado aos clientes priorizados?        | Apoiar visão de impacto financeiro  |

---

## 3. Objetivo do Projeto

O objetivo do projeto é construir um pipeline de dados em camadas para transformar dados brutos de pagamentos e cadastro em uma visão final de negócio.

A saída final do projeto é a tabela:

```text
data/gold/gold_indicadores_cliente.parquet
```

Essa tabela permite analisar clientes por:

* nível de risco;
* perfil de pagamento;
* prioridade de contato;
* ação recomendada;
* canal sugerido;
* cobertura cadastral;
* valor previsto associado aos clientes priorizados.

---

## 4. Escopo do Projeto

O projeto contempla:

| Área                | O que foi feito                                          |
| ------------------- | -------------------------------------------------------- |
| Engenharia de Dados | Criação de pipeline Raw, Bronze, Silver e Gold           |
| Qualidade de Dados  | Validações de schema, nulos, duplicidade, flags e regras |
| Modelagem Analítica | Criação de métricas por cliente                          |
| Regra de Negócio    | Classificação de risco e priorização de contato          |
| Documentação        | Explicação das camadas, campos, métricas e regras        |
| Power BI            | Preparação da Gold para consumo em dashboard             |
| IA/RAG              | Desenho conceitual de futura camada de agente de IA      |

---

## 5. O Que o Projeto Não Faz Nesta Versão

Nesta versão, o projeto ainda não realiza:

* envio real de mensagens para clientes;
* integração com canais como WhatsApp, SMS ou e-mail;
* modelo preditivo supervisionado de inadimplência;
* score estatístico treinado com machine learning;
* atualização automática em produção;
* tratamento jurídico ou regulatório de comunicação com clientes;
* uso de dados reais de clientes de uma instituição financeira.

A classificação atual é baseada em regras de negócio aplicadas ao histórico de pagamento disponível.

---

## 6. Fontes de Dados

O projeto utiliza dados públicos do dataset Home Credit.

Arquivos principais:

```text
data/raw/application_train.csv
data/raw/installments_payments.csv
```

### `application_train.csv`

Contém dados cadastrais e características dos clientes, como:

* identificador do cliente;
* renda;
* idade;
* escolaridade;
* tipo de moradia;
* tipo de contrato;
* ocupação;
* histórico de inadimplência;
* informações de contato.

### `installments_payments.csv`

Contém histórico de parcelas e pagamentos, como:

* identificador do cliente;
* identificador do contrato;
* número da parcela;
* data prevista de pagamento;
* data real de pagamento;
* valor previsto;
* valor pago.

---

## 7. Arquitetura de Dados

O projeto utiliza arquitetura medalhão:

```text
raw
↓
bronze
↓
silver
↓
gold
```

| Camada | Função                                                            |
| ------ | ----------------------------------------------------------------- |
| Raw    | Armazena os dados originais                                       |
| Bronze | Converte os dados para Parquet, mantendo proximidade com a origem |
| Silver | Trata, traduz, padroniza e cria regras reutilizáveis              |
| Gold   | Entrega indicadores finais para negócio, Power BI e futura IA     |

---

## 8. Principais Transformações de Negócio

A principal transformação do projeto é calcular se o pagamento foi antecipado, no prazo ou atrasado.

Regra:

```text
dif_dias_vencimento = dias_pagamento_ref - dias_previsto_ref
```

Interpretação:

|   Resultado | Significado            |
| ----------: | ---------------------- |
| Menor que 0 | Pagamento antecipado   |
|   Igual a 0 | Pagamento no prazo     |
| Maior que 0 | Pagamento em atraso    |
|        Nulo | Pagamento sem registro |

A partir dessa regra, o projeto cria métricas por cliente, como:

* quantidade de parcelas;
* quantidade de atrasos;
* quantidade de pagamentos antecipados;
* taxa de atraso;
* média de dias de atraso;
* maior atraso histórico;
* perfil de pagamento;
* nível de risco.

---

## 9. Classificação de Risco

O campo `nivel_risco` classifica o cliente em quatro grupos:

| Nível de risco       | Interpretação                                           |
| -------------------- | ------------------------------------------------------- |
| `baixo_risco`        | Cliente com bom comportamento histórico de pagamento    |
| `medio_risco`        | Cliente com sinais relevantes de atraso                 |
| `alto_risco`         | Cliente com atraso frequente ou severo                  |
| `risco_desconhecido` | Cliente sem dados suficientes para classificação segura |

Essa classificação considera tanto frequência quanto severidade do atraso.

---

## 10. Priorização de Contato

A Gold cria o campo:

```text
flg_priorizar_contato
```

Esse campo indica se o cliente deve ser priorizado para uma ação preventiva.

Regra geral:

| Condição                                                 | Valor |
| -------------------------------------------------------- | ----: |
| Cliente de alto risco, médio risco ou risco desconhecido |     1 |
| Cliente de baixo risco                                   |     0 |

Resultado validado:

```text
129.478 clientes priorizados
```

---

## 11. Ação Recomendada

A Gold também cria o campo:

```text
acao_recomendada
```

Esse campo sugere uma ação de negócio para cada grupo de cliente.

| Situação                                    | Ação recomendada                |
| ------------------------------------------- | ------------------------------- |
| Cliente de alto risco                       | `lembrete_preventivo_reforcado` |
| Cliente de médio risco                      | `lembrete_preventivo_padrao`    |
| Cliente de baixo risco e pagador antecipado | `comunicacao_relacionamento`    |
| Cliente de baixo risco                      | `lembrete_suave`                |
| Cliente com risco desconhecido              | `revisar_dados_pagamento`       |

---

## 12. Canal Sugerido

O campo `canal_sugerido` indica o canal disponível para contato, com base nos dados cadastrais.

Valores possíveis:

| Canal                     | Interpretação                                   |
| ------------------------- | ----------------------------------------------- |
| `email`                   | Cliente possui e-mail disponível                |
| `celular`                 | Cliente possui celular disponível ou contatável |
| `telefone`                | Cliente possui telefone disponível              |
| `canal_nao_identificado`  | Não foi possível identificar canal              |
| `cadastro_nao_disponivel` | Cliente não possui cadastro disponível          |

Essa regra não envia mensagens. Ela apenas sugere o canal mais adequado de acordo com os dados disponíveis.

---

## 13. Cobertura Cadastral

A Gold mantém todos os clientes com histórico de pagamento, mesmo quando não há cadastro disponível.

Resultado validado:

| Indicador                           |   Valor |
| ----------------------------------- | ------: |
| Clientes com histórico de pagamento | 339.587 |
| Clientes com cadastro               | 291.643 |
| Clientes sem cadastro               |  47.944 |
| Percentual com cadastro             |  85,88% |

Essa decisão evita perder clientes importantes na análise de comportamento.

---

## 14. Resultado Final Esperado

A saída final do projeto deve permitir que uma área de negócio responda:

* quantos clientes estão em cada nível de risco;
* quais clientes devem ser priorizados;
* qual ação deve ser recomendada;
* qual canal pode ser utilizado;
* quantos clientes possuem ou não cadastro;
* qual valor previsto está associado à carteira priorizada;
* como as regras de risco e priorização foram calculadas.

---

## 15. Uso no Power BI

A tabela Gold será a fonte principal do dashboard:

```text
data/gold/gold_indicadores_cliente.parquet
```

Visões sugeridas:

* clientes por nível de risco;
* clientes por prioridade de contato;
* clientes por ação recomendada;
* clientes por perfil de pagamento;
* clientes com e sem cadastro;
* valor previsto total priorizado;
* clientes por faixa de renda;
* clientes por faixa etária;
* canal sugerido para contato.

---

## 16. Uso Futuro com IA

Em uma evolução futura, o projeto poderá ter um agente de IA/RAG capaz de responder perguntas como:

```text
Por que este cliente foi classificado como alto_risco?
```

```text
Quais clientes devem receber lembrete preventivo reforçado?
```

```text
Quantos clientes priorizados não possuem cadastro?
```

```text
Quais regras foram usadas para definir prioridade_contato?
```

Esse agente poderia consultar a Gold e a documentação do projeto para gerar respostas explicáveis em linguagem de negócio.

---

## 17. Limitações

O projeto possui algumas limitações importantes:

* os dados são públicos e não representam uma operação real em produção;
* as datas são relativas, não datas reais de calendário;
* a classificação de risco é baseada em regras de negócio;
* ainda não existe modelo preditivo supervisionado;
* clientes sem cadastro foram mantidos para preservar o histórico de pagamento;
* antes de uso real, seria necessário validar regras com negócio, jurídico, privacidade e canais de comunicação.

---

## 18. Conclusão

Este projeto transforma dados brutos de pagamento e cadastro em uma solução analítica para prevenção de atraso.

A solução permite sair de uma abordagem genérica de cobrança para uma visão mais segmentada, onde clientes são classificados por comportamento, risco e prioridade.

A camada Gold entrega uma base pronta para Power BI e também serve como fundação para uma futura camada de IA explicável.
