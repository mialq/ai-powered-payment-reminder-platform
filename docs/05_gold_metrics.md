# Métricas da Camada Gold

Este documento descreve as principais métricas e indicadores criados na camada Gold do projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

A camada Gold foi criada para consumo analítico no Power BI e para apoiar decisões de negócio relacionadas à priorização de lembretes preventivos de pagamento.

---

## Arquivo Final da Gold

Arquivo gerado:

```text
data/gold/gold_indicadores_cliente.parquet
```

Granularidade:

```text
1 linha = 1 cliente com histórico de pagamento
```

Total de clientes na Gold:

```text
339.587
```

---

## Objetivo da Gold

A Gold consolida dados de comportamento de pagamento e cadastro de clientes para responder à pergunta de negócio:

> Como identificar clientes com maior risco de atraso e priorizar ações de lembrete preventivo antes do vencimento?

A tabela final permite analisar:

* nível de risco do cliente;
* perfil de pagamento;
* prioridade de contato;
* ação recomendada;
* canal sugerido;
* cobertura cadastral;
* valor histórico associado aos clientes priorizados.

---

## Fontes da Gold

A Gold foi criada a partir de duas tabelas da camada Silver:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
data/silver/silver_clientes_cadastro.parquet
```

A tabela principal é a Silver de comportamento de pagamento.
A Silver de cadastro entra como enriquecimento por meio de `LEFT JOIN`.

Essa decisão mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

---

## Decisão de Modelagem

A Gold parte da tabela:

```text
silver_comportamento_pagamento_cliente.parquet
```

e faz enriquecimento com:

```text
silver_clientes_cadastro.parquet
```

A decisão foi usar `LEFT JOIN` para evitar perda de clientes que possuem histórico de pagamento, mas não aparecem no cadastro.

Para esses casos, a Gold cria os campos:

```text
flg_cliente_com_cadastro = 0
status_cadastro = cliente_sem_cadastro
```

Para clientes encontrados no cadastro:

```text
flg_cliente_com_cadastro = 1
status_cadastro = cliente_com_cadastro
```

---

## Resumo Geral da Gold

| Indicador                           |   Valor |
| ----------------------------------- | ------: |
| Total de clientes                   | 339.587 |
| Clientes com cadastro               | 291.643 |
| Clientes sem cadastro               |  47.944 |
| Percentual de clientes com cadastro |  85,88% |
| Clientes priorizados para contato   | 129.478 |

---

## Distribuição por Nível de Risco

O campo `nivel_risco` classifica o cliente com base no comportamento histórico de pagamento.

| Nível de risco       | Quantidade de clientes |
| -------------------- | ---------------------: |
| `baixo_risco`        |                210.109 |
| `medio_risco`        |                 92.276 |
| `alto_risco`         |                 37.193 |
| `risco_desconhecido` |                      9 |

Interpretação:

| Nível de risco       | Interpretação                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------- |
| `baixo_risco`        | Cliente com bom comportamento histórico de pagamento.                                         |
| `medio_risco`        | Cliente com sinais relevantes de atraso. Deve ser priorizado para lembrete preventivo padrão. |
| `alto_risco`         | Cliente com atraso frequente ou severo. Deve receber comunicação preventiva reforçada.        |
| `risco_desconhecido` | Cliente sem dados suficientes para classificação segura. Deve ser revisado.                   |

---

## Distribuição por Perfil de Pagamento

O campo `perfil_pagamento` descreve o comportamento histórico do cliente.

| Perfil de pagamento          | Quantidade de clientes |
| ---------------------------- | ---------------------: |
| `pagador_antecipado`         |                151.500 |
| `baixo_atraso`               |                 87.939 |
| `atraso_moderado`            |                 71.455 |
| `alto_atraso`                |                 20.451 |
| `pagador_no_prazo`           |                  8.233 |
| `comportamento_desconhecido` |                      9 |

Interpretação:

| Perfil                       | Descrição                                          |
| ---------------------------- | -------------------------------------------------- |
| `pagador_antecipado`         | Cliente que costuma pagar antes do vencimento.     |
| `pagador_no_prazo`           | Cliente sem atrasos e com pagamentos no prazo.     |
| `baixo_atraso`               | Cliente com baixa taxa histórica de atraso.        |
| `atraso_moderado`            | Cliente com comportamento intermediário de atraso. |
| `alto_atraso`                | Cliente com comportamento elevado de atraso.       |
| `comportamento_desconhecido` | Cliente sem dados suficientes para classificação.  |

---

## Clientes Priorizados

O campo `flg_priorizar_contato` indica se o cliente deve entrar em uma ação prioritária.

Regra:

```text
flg_priorizar_contato = 1 quando nivel_risco IN ('alto_risco', 'medio_risco', 'risco_desconhecido')
flg_priorizar_contato = 0 quando nivel_risco = 'baixo_risco'
```

Resultado:

| Grupo                    | Quantidade de clientes |
| ------------------------ | ---------------------: |
| Clientes priorizados     |                129.478 |
| Clientes não priorizados |                210.109 |

Clientes priorizados por nível de risco:

| Nível de risco       | Clientes priorizados |
| -------------------- | -------------------: |
| `medio_risco`        |               92.276 |
| `alto_risco`         |               37.193 |
| `risco_desconhecido` |                    9 |
| `baixo_risco`        |                    0 |

---

## Distribuição por Prioridade de Contato

O campo `prioridade_contato` define a urgência da comunicação preventiva.

| Prioridade de contato | Quantidade de clientes |
| --------------------- | ---------------------: |
| `prioridade_baixa`    |                210.109 |
| `prioridade_media`    |                 92.276 |
| `prioridade_maxima`   |                 23.707 |
| `prioridade_alta`     |                 13.486 |
| `prioridade_revisao`  |                      9 |

Regras:

| Condição                                               | Prioridade           |
| ------------------------------------------------------ | -------------------- |
| `nivel_risco = alto_risco` e `maior_atraso_dias >= 30` | `prioridade_maxima`  |
| `nivel_risco = alto_risco`                             | `prioridade_alta`    |
| `nivel_risco = medio_risco`                            | `prioridade_media`   |
| `nivel_risco = risco_desconhecido`                     | `prioridade_revisao` |
| Demais casos                                           | `prioridade_baixa`   |

---

## Distribuição por Ação Recomendada

O campo `acao_recomendada` traduz o risco em uma sugestão de ação de negócio.

| Ação recomendada                | Quantidade de clientes |
| ------------------------------- | ---------------------: |
| `comunicacao_relacionamento`    |                151.500 |
| `lembrete_preventivo_padrao`    |                 92.276 |
| `lembrete_suave`                |                 58.609 |
| `lembrete_preventivo_reforcado` |                 37.193 |
| `revisar_dados_pagamento`       |                      9 |

Regras:

| Condição                                                              | Ação recomendada                |
| --------------------------------------------------------------------- | ------------------------------- |
| `nivel_risco = alto_risco`                                            | `lembrete_preventivo_reforcado` |
| `nivel_risco = medio_risco`                                           | `lembrete_preventivo_padrao`    |
| `nivel_risco = baixo_risco` e `perfil_pagamento = pagador_antecipado` | `comunicacao_relacionamento`    |
| `nivel_risco = baixo_risco`                                           | `lembrete_suave`                |
| `nivel_risco = risco_desconhecido`                                    | `revisar_dados_pagamento`       |

---

## Grupo de Negócio

O campo `grupo_negocio` facilita filtros no Power BI.

| Grupo de negócio         | Regra                           |
| ------------------------ | ------------------------------- |
| `clientes_prioritarios`  | Clientes de médio ou alto risco |
| `clientes_para_revisao`  | Clientes com risco desconhecido |
| `clientes_monitoramento` | Clientes de baixo risco         |

---

## Cobertura Cadastral

A cobertura cadastral indica quantos clientes da Gold possuem dados de cadastro disponíveis.

| Status de cadastro     | Quantidade de clientes |
| ---------------------- | ---------------------: |
| `cliente_com_cadastro` |                291.643 |
| `cliente_sem_cadastro` |                 47.944 |

Percentual de clientes com cadastro:

```text
85,88%
```

Essa informação é importante porque mostra que nem todos os clientes com histórico de pagamento estavam disponíveis no cadastro.

Mesmo assim, esses clientes foram mantidos na Gold para não perder histórico relevante de comportamento.

---

## Canal Sugerido

O campo `canal_sugerido` indica o melhor canal disponível para contato com o cliente, de acordo com os dados cadastrais.

Regras:

| Condição                       | Canal sugerido            |
| ------------------------------ | ------------------------- |
| Cliente sem cadastro           | `cadastro_nao_disponivel` |
| Cliente com e-mail             | `email`                   |
| Cliente com celular contatável | `celular`                 |
| Cliente com celular informado  | `celular`                 |
| Cliente com telefone informado | `telefone`                |
| Nenhum canal identificado      | `canal_nao_identificado`  |

---

## Valor Priorizado

O campo `valor_previsto_total_priorizado` representa o valor histórico previsto associado aos clientes priorizados.

Regra:

| Condição                                       | Valor                         |
| ---------------------------------------------- | ----------------------------- |
| `nivel_risco IN ('alto_risco', 'medio_risco')` | recebe `valor_previsto_total` |
| Demais casos                                   | recebe 0                      |

Resultado total:

```text
valor_previsto_total_priorizado = 112.862.100.000 aproximadamente
```

Observação:

Esse valor aparece no terminal em notação científica como:

```text
1.128621e+11
```

No Power BI, ele deve ser formatado como número decimal ou moeda para facilitar leitura.

---

## Principais Campos da Gold

| Campo                             | Descrição                                                         |
| --------------------------------- | ----------------------------------------------------------------- |
| `id_cliente`                      | Identificador único do cliente.                                   |
| `nivel_risco`                     | Classificação de risco do cliente.                                |
| `perfil_pagamento`                | Perfil histórico de comportamento de pagamento.                   |
| `qtd_parcelas_total`              | Total de parcelas associadas ao cliente.                          |
| `qtd_parcelas_validas`            | Total de parcelas com pagamento registrado.                       |
| `qtd_parcelas_atraso`             | Total de parcelas pagas em atraso.                                |
| `taxa_atraso_pct`                 | Percentual de atraso do cliente.                                  |
| `media_dias_atraso`               | Média de dias de atraso considerando apenas pagamentos atrasados. |
| `maior_atraso_dias`               | Maior atraso histórico do cliente.                                |
| `valor_previsto_total`            | Valor total previsto das parcelas do cliente.                     |
| `valor_pago_total`                | Valor total pago pelo cliente.                                    |
| `flg_cliente_com_cadastro`        | Indica se o cliente possui cadastro disponível.                   |
| `status_cadastro`                 | Classificação da cobertura cadastral.                             |
| `faixa_idade`                     | Faixa etária do cliente.                                          |
| `faixa_renda`                     | Faixa de renda do cliente.                                        |
| `canal_sugerido`                  | Canal recomendado para contato.                                   |
| `prioridade_contato`              | Prioridade de comunicação preventiva.                             |
| `flg_priorizar_contato`           | Flag que indica se o cliente deve ser priorizado.                 |
| `acao_recomendada`                | Ação sugerida para o cliente.                                     |
| `grupo_negocio`                   | Agrupamento de negócio para análise.                              |
| `valor_previsto_total_priorizado` | Valor previsto associado aos clientes priorizados.                |
| `dt_processamento_gold`           | Data e hora de processamento da Gold.                             |

---

## Métricas Recomendadas para Power BI

### Cartões

| Indicador                       | Campo base                        |
| ------------------------------- | --------------------------------- |
| Total de clientes               | `id_cliente`                      |
| Clientes priorizados            | `flg_priorizar_contato`           |
| Clientes de alto risco          | `nivel_risco`                     |
| Clientes de médio risco         | `nivel_risco`                     |
| Clientes com cadastro           | `flg_cliente_com_cadastro`        |
| Clientes sem cadastro           | `status_cadastro`                 |
| Valor previsto total priorizado | `valor_previsto_total_priorizado` |

### Gráficos

| Visual                           | Campo sugerido       |
| -------------------------------- | -------------------- |
| Clientes por risco               | `nivel_risco`        |
| Clientes por prioridade          | `prioridade_contato` |
| Clientes por ação recomendada    | `acao_recomendada`   |
| Clientes por perfil de pagamento | `perfil_pagamento`   |
| Clientes por cobertura cadastral | `status_cadastro`    |
| Clientes por faixa de renda      | `faixa_renda`        |
| Clientes por faixa etária        | `faixa_idade`        |
| Clientes por canal sugerido      | `canal_sugerido`     |

### Filtros

Campos recomendados para segmentação:

```text
nivel_risco
prioridade_contato
acao_recomendada
status_cadastro
faixa_idade
faixa_renda
genero
tipo_renda
escolaridade
tipo_moradia
canal_sugerido
grupo_negocio
```

---

## Validações da Gold

A Gold foi validada pelo script:

```text
scripts/10_validar_gold_indicadores_cliente.py
```

Validações aprovadas:

```text
339.587 clientes
339.587 clientes distintos
0 duplicados
0 colunas faltando
0 colunas extras
0 valores categóricos inválidos
0 flags fora do padrão
0 inconsistências de regras de negócio
0 inconsistências numéricas
0 diferença de volume entre Silver comportamento e Gold
```

---

## Interpretação para o Negócio

A Gold não deve ser interpretada como um modelo preditivo estatístico definitivo.

Ela representa uma segmentação analítica baseada em regras de negócio e comportamento histórico de pagamento.

A leitura recomendada é:

| Grupo                | Interpretação                                                                     |
| -------------------- | --------------------------------------------------------------------------------- |
| `baixo_risco`        | Clientes para monitoramento ou comunicação leve.                                  |
| `medio_risco`        | Clientes com sinais de atraso, recomendados para lembrete preventivo padrão.      |
| `alto_risco`         | Clientes com atraso frequente ou severo, recomendados para comunicação reforçada. |
| `risco_desconhecido` | Clientes que precisam de revisão antes de ação automatizada.                      |

---

## Próximos Usos

A Gold pode ser usada para:

* criação de dashboard no Power BI;
* priorização de clientes para lembrete preventivo;
* segmentação por risco e comportamento;
* análise de cobertura cadastral;
* apoio a um futuro agente de IA/RAG;
* geração de explicações de negócio sobre risco e priorização.
