# Mapeamento das Perguntas de Negócio

Este documento conecta as perguntas de negócio do projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform** aos dados, métricas e indicadores criados nas camadas Silver e Gold.

O objetivo é mostrar como o pipeline de dados responde, de forma rastreável, à pergunta central do projeto:

> Como identificar clientes com maior risco de atraso e priorizar ações de lembrete preventivo antes do vencimento?

---

## 1. Pergunta Central do Projeto

A pergunta principal é:

> Como identificar clientes com maior risco de atraso e acionar lembretes preventivos antes do vencimento?

Para responder a essa pergunta, o projeto constrói um pipeline em camadas:

```text
raw
↓
bronze
↓
silver
↓
gold
```

A camada final utilizada para análise de negócio é:

```text
data/gold/gold_indicadores_cliente.parquet
```

Essa tabela possui uma linha por cliente com histórico de pagamento e contém informações de risco, comportamento, prioridade de contato, ação recomendada e cobertura cadastral.

---

## 2. Como o Projeto Responde à Pergunta de Negócio

A resposta é construída em etapas:

| Etapa                               | O que responde                                                                  |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| Silver de pagamentos                | Identifica se cada pagamento foi antecipado, no prazo, atrasado ou sem registro |
| Silver de comportamento por cliente | Consolida o histórico de pagamento por cliente                                  |
| Silver de clientes                  | Enriquece a análise com dados cadastrais                                        |
| Gold de indicadores por cliente     | Define risco, prioridade de contato, ação recomendada e canal sugerido          |

A camada Gold permite responder:

* quem são os clientes com maior risco;
* quantos clientes devem ser priorizados;
* qual ação preventiva é recomendada;
* qual canal pode ser utilizado;
* qual valor histórico está associado aos clientes priorizados;
* quantos clientes têm ou não cadastro disponível.

---

## 3. Pergunta: O Cliente Costuma Pagar em Atraso?

Essa pergunta é respondida a partir da Silver de pagamentos.

Arquivo:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

Campos principais:

| Campo                      | Descrição                                         |
| -------------------------- | ------------------------------------------------- |
| `dif_dias_vencimento`      | Diferença entre data de pagamento e data prevista |
| `dias_atraso`              | Quantidade de dias de atraso                      |
| `dias_antecipacao`         | Quantidade de dias de antecipação                 |
| `status_pagamento`         | Classificação do pagamento                        |
| `flg_pagamento_atrasado`   | Indica se o pagamento foi atrasado                |
| `flg_pagamento_antecipado` | Indica se o pagamento foi antecipado              |
| `flg_pagamento_no_prazo`   | Indica se o pagamento foi feito no prazo          |

Regra principal:

```text
dif_dias_vencimento = dias_pagamento_ref - dias_previsto_ref
```

Interpretação:

|                     Resultado | Significado            |
| ----------------------------: | ---------------------- |
|     `dif_dias_vencimento < 0` | Pagamento antecipado   |
|     `dif_dias_vencimento = 0` | Pagamento no prazo     |
|     `dif_dias_vencimento > 0` | Pagamento em atraso    |
| `dif_dias_vencimento IS NULL` | Pagamento sem registro |

Status possíveis:

| Status                     | Significado                             |
| -------------------------- | --------------------------------------- |
| `pago_antecipado`          | Pagamento realizado antes do vencimento |
| `pago_no_prazo`            | Pagamento realizado exatamente no prazo |
| `pago_em_atraso`           | Pagamento realizado após o vencimento   |
| `sem_pagamento_registrado` | Pagamento sem data ou valor registrado  |

---

## 4. Pergunta: Qual é o Comportamento Histórico do Cliente?

Essa pergunta é respondida pela Silver de comportamento de pagamento por cliente.

Arquivo:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Granularidade:

```text
1 linha = 1 cliente com histórico de pagamento
```

Campos principais:

| Campo                  | Descrição                               |
| ---------------------- | --------------------------------------- |
| `qtd_parcelas_total`   | Total de parcelas associadas ao cliente |
| `qtd_parcelas_validas` | Parcelas com pagamento registrado       |
| `qtd_parcelas_atraso`  | Parcelas pagas em atraso                |
| `qtd_pagas_antecipado` | Parcelas pagas antecipadamente          |
| `qtd_pagas_no_prazo`   | Parcelas pagas no prazo                 |
| `taxa_atraso_pct`      | Percentual de atraso do cliente         |
| `media_dias_atraso`    | Média de dias de atraso                 |
| `maior_atraso_dias`    | Maior atraso histórico                  |
| `perfil_pagamento`     | Perfil comportamental do cliente        |
| `nivel_risco`          | Classificação de risco do cliente       |

Essa camada transforma vários registros de pagamentos em uma visão consolidada por cliente.

---

## 5. Pergunta: Qual é o Perfil de Pagamento do Cliente?

O campo `perfil_pagamento` classifica o comportamento histórico do cliente.

| Perfil                       | Interpretação                                    |
| ---------------------------- | ------------------------------------------------ |
| `pagador_antecipado`         | Cliente costuma pagar antes do vencimento        |
| `pagador_no_prazo`           | Cliente não apresenta atrasos e paga no prazo    |
| `baixo_atraso`               | Cliente tem baixa taxa de atraso                 |
| `atraso_moderado`            | Cliente tem atraso em nível intermediário        |
| `alto_atraso`                | Cliente tem comportamento elevado de atraso      |
| `comportamento_desconhecido` | Cliente sem dados suficientes para classificação |

Essa informação ajuda a entender se o cliente precisa de lembrete, relacionamento, monitoramento ou revisão.

---

## 6. Pergunta: Qual é o Nível de Risco do Cliente?

O campo `nivel_risco` classifica o risco de atraso do cliente com base no histórico de pagamentos.

| Nível de risco       | Interpretação                                             |
| -------------------- | --------------------------------------------------------- |
| `baixo_risco`        | Cliente com bom comportamento histórico                   |
| `medio_risco`        | Cliente com sinais relevantes de atraso                   |
| `alto_risco`         | Cliente com atraso frequente ou severo                    |
| `risco_desconhecido` | Cliente com dados insuficientes para classificação segura |

Regra geral:

| Condição                                                                                                              | Classificação        |
| --------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Cliente sem parcelas válidas                                                                                          | `risco_desconhecido` |
| Taxa de atraso maior ou igual a 30% ou maior atraso maior ou igual a 30 dias                                          | `alto_risco`         |
| Taxa de atraso maior ou igual a 10%, média de atraso maior ou igual a 5 dias ou maior atraso maior ou igual a 10 dias | `medio_risco`        |
| Demais casos                                                                                                          | `baixo_risco`        |

Essa regra considera tanto a frequência quanto a severidade do atraso.

---

## 7. Pergunta: Quais Clientes Devem Ser Priorizados?

Essa pergunta é respondida na Gold pelo campo:

```text
flg_priorizar_contato
```

Arquivo:

```text
data/gold/gold_indicadores_cliente.parquet
```

Regra:

| Condição                                                             | Valor |
| -------------------------------------------------------------------- | ----: |
| `nivel_risco IN ('alto_risco', 'medio_risco', 'risco_desconhecido')` |     1 |
| `nivel_risco = baixo_risco`                                          |     0 |

Interpretação:

| Valor | Significado                 |
| ----: | --------------------------- |
|     1 | Cliente deve ser priorizado |
|     0 | Cliente pode ser monitorado |

Resultado validado:

```text
clientes_priorizados: 129.478
```

Distribuição:

| Nível de risco       | Priorizados |
| -------------------- | ----------: |
| `medio_risco`        |      92.276 |
| `alto_risco`         |      37.193 |
| `risco_desconhecido` |           9 |
| `baixo_risco`        |           0 |

---

## 8. Pergunta: Qual Prioridade de Contato Cada Cliente Deve Receber?

Essa pergunta é respondida pelo campo:

```text
prioridade_contato
```

Valores possíveis:

| Prioridade           | Interpretação                                                      |
| -------------------- | ------------------------------------------------------------------ |
| `prioridade_maxima`  | Cliente de alto risco com maior atraso igual ou superior a 30 dias |
| `prioridade_alta`    | Cliente de alto risco                                              |
| `prioridade_media`   | Cliente de médio risco                                             |
| `prioridade_revisao` | Cliente com risco desconhecido                                     |
| `prioridade_baixa`   | Cliente de baixo risco                                             |

Distribuição validada:

| Prioridade           | Clientes |
| -------------------- | -------: |
| `prioridade_baixa`   |  210.109 |
| `prioridade_media`   |   92.276 |
| `prioridade_maxima`  |   23.707 |
| `prioridade_alta`    |   13.486 |
| `prioridade_revisao` |        9 |

---

## 9. Pergunta: Qual Ação Recomendada para Cada Cliente?

Essa pergunta é respondida pelo campo:

```text
acao_recomendada
```

Valores possíveis:

| Ação recomendada                | Interpretação                                                       |
| ------------------------------- | ------------------------------------------------------------------- |
| `lembrete_preventivo_reforcado` | Comunicação mais forte para clientes de alto risco                  |
| `lembrete_preventivo_padrao`    | Comunicação preventiva padrão para clientes de médio risco          |
| `comunicacao_relacionamento`    | Comunicação leve para clientes de baixo risco com perfil antecipado |
| `lembrete_suave`                | Lembrete leve para clientes de baixo risco                          |
| `revisar_dados_pagamento`       | Revisão necessária para clientes com risco desconhecido             |

Distribuição validada:

| Ação recomendada                | Clientes |
| ------------------------------- | -------: |
| `comunicacao_relacionamento`    |  151.500 |
| `lembrete_preventivo_padrao`    |   92.276 |
| `lembrete_suave`                |   58.609 |
| `lembrete_preventivo_reforcado` |   37.193 |
| `revisar_dados_pagamento`       |        9 |

---

## 10. Pergunta: Qual Canal Pode Ser Usado Para Contato?

Essa pergunta é respondida pelo campo:

```text
canal_sugerido
```

A regra utiliza os dados disponíveis na Silver de clientes.

Valores possíveis:

| Canal sugerido            | Interpretação                                   |
| ------------------------- | ----------------------------------------------- |
| `email`                   | Cliente possui e-mail disponível                |
| `celular`                 | Cliente possui celular disponível ou contatável |
| `telefone`                | Cliente possui telefone disponível              |
| `canal_nao_identificado`  | Não foi possível identificar canal de contato   |
| `cadastro_nao_disponivel` | Cliente não possui cadastro disponível          |

Essa regra não envia mensagens automaticamente. Ela apenas sugere o canal mais apropriado com base nos dados disponíveis.

---

## 11. Pergunta: Quantos Clientes Têm Cadastro Disponível?

Essa pergunta é respondida pelos campos:

```text
flg_cliente_com_cadastro
status_cadastro
```

Resultado validado:

| Status de cadastro     | Clientes |
| ---------------------- | -------: |
| `cliente_com_cadastro` |  291.643 |
| `cliente_sem_cadastro` |   47.944 |

Percentual de clientes com cadastro:

```text
85,88%
```

Decisão de modelagem:

A Gold mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

Isso evita perda de clientes importantes para análise de comportamento.

---

## 12. Pergunta: Qual Valor Histórico Está Associado aos Clientes Priorizados?

Essa pergunta é respondida pelo campo:

```text
valor_previsto_total_priorizado
```

Regra:

| Condição                                       | Valor                         |
| ---------------------------------------------- | ----------------------------- |
| `nivel_risco IN ('alto_risco', 'medio_risco')` | recebe `valor_previsto_total` |
| Demais casos                                   | recebe 0                      |

Resultado validado:

```text
valor_previsto_total_priorizado aproximadamente 112.862.100.000
```

Esse campo pode ser usado no Power BI para medir o valor histórico associado à carteira priorizada.

---

## 13. Pergunta: Como Agrupar os Clientes Para Análise de Negócio?

Essa pergunta é respondida pelo campo:

```text
grupo_negocio
```

Valores possíveis:

| Grupo                    | Interpretação                   |
| ------------------------ | ------------------------------- |
| `clientes_prioritarios`  | Clientes de médio ou alto risco |
| `clientes_para_revisao`  | Clientes com risco desconhecido |
| `clientes_monitoramento` | Clientes de baixo risco         |

Esse campo facilita a criação de filtros e segmentações no Power BI.

---

## 14. Pergunta: Como a Área de Negócio Pode Usar Essas Informações?

A Gold permite criar uma visão orientada à ação:

| Situação                                    | Ação sugerida                             |
| ------------------------------------------- | ----------------------------------------- |
| Cliente de alto risco                       | Enviar lembrete preventivo reforçado      |
| Cliente de médio risco                      | Enviar lembrete preventivo padrão         |
| Cliente de baixo risco e pagador antecipado | Usar comunicação de relacionamento        |
| Cliente de baixo risco                      | Enviar lembrete suave ou apenas monitorar |
| Cliente com risco desconhecido              | Revisar dados antes de ação automatizada  |

Essa abordagem evita tratar todos os clientes da mesma forma.

---

## 15. Perguntas Que o Dashboard Pode Responder

O dashboard no Power BI poderá responder:

| Pergunta                                            | Campo principal                   |
| --------------------------------------------------- | --------------------------------- |
| Quantos clientes foram analisados?                  | `id_cliente`                      |
| Quantos clientes são de alto risco?                 | `nivel_risco`                     |
| Quantos clientes devem ser priorizados?             | `flg_priorizar_contato`           |
| Qual prioridade de contato tem mais clientes?       | `prioridade_contato`              |
| Qual ação recomendada é mais comum?                 | `acao_recomendada`                |
| Quantos clientes não possuem cadastro?              | `status_cadastro`                 |
| Qual valor está associado aos clientes priorizados? | `valor_previsto_total_priorizado` |
| Quais clientes têm maior atraso histórico?          | `maior_atraso_dias`               |
| Quais clientes têm maior taxa de atraso?            | `taxa_atraso_pct`                 |
| Qual canal sugerido para contato?                   | `canal_sugerido`                  |

---

## 16. Perguntas Que um Futuro Agente de IA Poderá Responder

Um futuro agente de IA/RAG poderá usar a Gold e a documentação do projeto para responder perguntas como:

```text
Por que este cliente foi classificado como alto_risco?
```

```text
Quais clientes devem receber lembrete preventivo reforçado?
```

```text
Qual ação recomendada para clientes de medio_risco?
```

```text
Quantos clientes priorizados não possuem cadastro?
```

```text
Qual grupo de clientes representa maior valor previsto priorizado?
```

```text
Quais regras foram usadas para definir prioridade_contato?
```

O agente poderá recuperar informações deste documento, das regras de negócio e do dicionário da Gold para gerar respostas mais explicáveis.

---

## 17. Relação Entre Perguntas, Camadas e Arquivos

| Pergunta                                   | Camada | Arquivo                                          |
| ------------------------------------------ | ------ | ------------------------------------------------ |
| O pagamento foi atrasado?                  | Silver | `silver_pagamentos_parcelas.parquet`             |
| Qual o comportamento histórico do cliente? | Silver | `silver_comportamento_pagamento_cliente.parquet` |
| Qual o perfil cadastral do cliente?        | Silver | `silver_clientes_cadastro.parquet`               |
| Qual cliente deve ser priorizado?          | Gold   | `gold_indicadores_cliente.parquet`               |
| Qual ação deve ser recomendada?            | Gold   | `gold_indicadores_cliente.parquet`               |
| Qual canal sugerido para contato?          | Gold   | `gold_indicadores_cliente.parquet`               |
| Qual valor histórico está priorizado?      | Gold   | `gold_indicadores_cliente.parquet`               |

---

## 18. Limitações da Resposta de Negócio

As respostas geradas pelo projeto devem ser interpretadas com alguns cuidados:

* A classificação de risco é baseada em regras de negócio, não em modelo preditivo supervisionado.
* As datas do dataset são relativas, não datas reais de calendário.
* Clientes sem cadastro foram mantidos para preservar histórico de pagamento.
* A sugestão de canal depende da disponibilidade dos dados cadastrais.
* Antes de automatizar mensagens reais, seria necessário validar regras com áreas de negócio, jurídico, privacidade e canais de comunicação.

---

## 19. Conclusão

O projeto transforma dados brutos de pagamentos e cadastro em uma visão analítica final capaz de apoiar decisões de negócio.

A camada Gold responde à pergunta central do projeto ao indicar:

```text
quem tem maior risco
quem deve ser priorizado
qual ação é recomendada
qual canal pode ser usado
qual valor está associado à carteira priorizada
```

Com isso, a empresa pode sair de uma estratégia genérica de lembrete para uma abordagem mais segmentada, rastreável e orientada por dados.
