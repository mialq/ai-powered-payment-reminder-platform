# Dicionário de Dados - Gold Indicadores Cliente

Este documento descreve os campos da tabela final da camada Gold:

```text
data/gold/gold_indicadores_cliente.parquet
```

A tabela `gold_indicadores_cliente` foi criada para consumo analítico no Power BI e para apoiar a priorização de ações preventivas de lembrete de pagamento.

A granularidade da tabela é:

```text
1 linha = 1 cliente com histórico de pagamento
```

---

## Objetivo da Tabela

A tabela Gold consolida informações de comportamento de pagamento, dados cadastrais, classificação de risco e priorização de contato.

Ela permite responder perguntas como:

* Quantos clientes possuem alto risco de atraso?
* Quais clientes devem ser priorizados para lembrete preventivo?
* Qual ação recomendada para cada grupo de clientes?
* Qual o canal sugerido para contato?
* Quantos clientes com histórico de pagamento possuem cadastro disponível?
* Qual o valor previsto associado aos clientes priorizados?

---

## Origem dos Dados

A Gold foi criada a partir de duas tabelas da camada Silver:

```text
silver_comportamento_pagamento_cliente.parquet
silver_clientes_cadastro.parquet
```

A tabela principal da Gold parte da Silver de comportamento de pagamento e faz enriquecimento com cadastro por meio de `LEFT JOIN`.

Essa decisão mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

---

## Resumo da Tabela

| Informação              |   Valor |
| ----------------------- | ------: |
| Total de clientes       | 339.587 |
| Clientes com cadastro   | 291.643 |
| Clientes sem cadastro   |  47.944 |
| Percentual com cadastro |  85,88% |
| Clientes priorizados    | 129.478 |

---

## Campos de Identificação

| Campo        | Tipo lógico | Descrição                                                           |
| ------------ | ----------- | ------------------------------------------------------------------- |
| `id_cliente` | inteiro     | Identificador único do cliente. É a chave principal da tabela Gold. |

---

## Campos de Comportamento de Pagamento

| Campo                            | Tipo lógico | Descrição                                                                                                       |
| -------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------- |
| `nivel_risco`                    | categórico  | Classificação final de risco do cliente com base no comportamento de pagamento.                                 |
| `perfil_pagamento`               | categórico  | Perfil comportamental do cliente em relação aos pagamentos.                                                     |
| `qtd_parcelas_total`             | inteiro     | Quantidade total de parcelas/pagamentos associados ao cliente.                                                  |
| `qtd_parcelas_validas`           | inteiro     | Quantidade de parcelas com pagamento registrado e válidas para cálculo de comportamento.                        |
| `qtd_parcelas_atraso`            | numérico    | Quantidade de parcelas pagas em atraso.                                                                         |
| `qtd_pagas_antecipado`           | numérico    | Quantidade de parcelas pagas antes do vencimento.                                                               |
| `qtd_pagas_no_prazo`             | numérico    | Quantidade de parcelas pagas exatamente no prazo.                                                               |
| `taxa_atraso_pct`                | percentual  | Percentual de parcelas atrasadas em relação às parcelas válidas.                                                |
| `media_dias_vs_vencimento`       | numérico    | Média da diferença entre data de pagamento e data prevista. Pode ser negativa quando há pagamentos antecipados. |
| `media_dias_atraso`              | numérico    | Média de dias de atraso considerando apenas pagamentos atrasados.                                               |
| `maior_atraso_dias`              | numérico    | Maior atraso histórico registrado para o cliente.                                                               |
| `maior_antecipacao_dias`         | numérico    | Maior antecipação histórica registrada para o cliente.                                                          |
| `valor_previsto_total`           | monetário   | Soma total dos valores previstos das parcelas do cliente.                                                       |
| `valor_pago_total`               | monetário   | Soma total dos valores efetivamente pagos pelo cliente.                                                         |
| `dif_valor_pago_previsto_total`  | monetário   | Diferença entre valor pago total e valor previsto total.                                                        |
| `qtd_registros_com_nulo_critico` | numérico    | Quantidade de registros do cliente com algum campo crítico nulo na Silver de pagamentos.                        |
| `qtd_campos_criticos_nulos`      | numérico    | Quantidade total de campos críticos nulos associados ao cliente.                                                |
| `qtd_pagamentos_parciais`        | numérico    | Quantidade de pagamentos em que o valor pago foi menor que o valor previsto.                                    |
| `qtd_pagamentos_acima_previsto`  | numérico    | Quantidade de pagamentos em que o valor pago foi maior que o valor previsto.                                    |

---

## Valores Permitidos - `nivel_risco`

| Valor                | Descrição                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| `baixo_risco`        | Cliente com baixo comportamento histórico de atraso.                                            |
| `medio_risco`        | Cliente com risco intermediário de atraso. Deve ser priorizado para lembrete preventivo padrão. |
| `alto_risco`         | Cliente com maior risco de atraso. Deve ser priorizado com comunicação reforçada.               |
| `risco_desconhecido` | Cliente sem dados suficientes para classificação segura. Deve ser revisado.                     |

---

## Valores Permitidos - `perfil_pagamento`

| Valor                        | Descrição                                                     |
| ---------------------------- | ------------------------------------------------------------- |
| `pagador_antecipado`         | Cliente que historicamente costuma pagar antes do vencimento. |
| `pagador_no_prazo`           | Cliente que não apresenta atrasos e costuma pagar no prazo.   |
| `baixo_atraso`               | Cliente com baixa taxa de atraso.                             |
| `atraso_moderado`            | Cliente com comportamento moderado de atraso.                 |
| `alto_atraso`                | Cliente com comportamento elevado de atraso.                  |
| `comportamento_desconhecido` | Cliente sem comportamento suficiente para classificação.      |

---

## Campos de Cobertura Cadastral

| Campo                      | Tipo lógico | Descrição                                                                                                                  |
| -------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------- |
| `flg_cliente_com_cadastro` | flag        | Indica se o cliente foi encontrado na Silver de cadastro. Valor 1 para cliente com cadastro e 0 para cliente sem cadastro. |
| `status_cadastro`          | categórico  | Indica se o cliente possui cadastro disponível.                                                                            |

### Valores Permitidos - `status_cadastro`

| Valor                  | Descrição                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------- |
| `cliente_com_cadastro` | Cliente encontrado na Silver de clientes.                                              |
| `cliente_sem_cadastro` | Cliente com histórico de pagamento, mas sem cadastro disponível na Silver de clientes. |

---

## Campos Cadastrais

| Campo                  | Tipo lógico | Descrição                                                      |
| ---------------------- | ----------- | -------------------------------------------------------------- |
| `genero`               | categórico  | Gênero informado no cadastro.                                  |
| `tipo_renda`           | categórico  | Tipo de renda ou ocupação econômica declarada.                 |
| `escolaridade`         | categórico  | Escolaridade do cliente.                                       |
| `estado_civil`         | categórico  | Estado civil do cliente.                                       |
| `tipo_moradia`         | categórico  | Tipo de moradia informado no cadastro.                         |
| `ocupacao`             | categórico  | Ocupação profissional do cliente.                              |
| `idade_anos`           | inteiro     | Idade aproximada do cliente em anos.                           |
| `renda_total`          | monetário   | Renda total informada no cadastro.                             |
| `valor_credito`        | monetário   | Valor de crédito associado ao cliente.                         |
| `valor_anuidade`       | monetário   | Valor da anuidade ou parcela anualizada associada ao contrato. |
| `valor_bens`           | monetário   | Valor dos bens associados à solicitação de crédito.            |
| `razao_credito_renda`  | numérico    | Relação entre valor de crédito e renda total.                  |
| `razao_anuidade_renda` | numérico    | Relação entre valor de anuidade e renda total.                 |
| `qtd_filhos`           | inteiro     | Quantidade de filhos informada no cadastro.                    |
| `qtd_membros_familia`  | numérico    | Quantidade de membros da família informada no cadastro.        |

---

## Campos de Flags Cadastrais

| Campo                         | Tipo lógico | Descrição                                                |
| ----------------------------- | ----------- | -------------------------------------------------------- |
| `flg_inadimplencia_historica` | flag        | Indica histórico de inadimplência na base de cadastro.   |
| `flg_possui_carro`            | flag        | Indica se o cliente possui carro.                        |
| `flg_possui_imovel`           | flag        | Indica se o cliente possui imóvel.                       |
| `flg_possui_celular`          | flag        | Indica se o cliente possui celular informado.            |
| `flg_celular_contatavel`      | flag        | Indica se o celular do cliente é considerado contatável. |
| `flg_possui_telefone`         | flag        | Indica se o cliente possui telefone informado.           |
| `flg_possui_email`            | flag        | Indica se o cliente possui e-mail informado.             |

Valores esperados para flags:

| Valor | Significado |
| ----: | ----------- |
|     0 | Não         |
|     1 | Sim         |

---

## Campos de Segmentação

| Campo            | Tipo lógico | Descrição                                                                             |
| ---------------- | ----------- | ------------------------------------------------------------------------------------- |
| `faixa_idade`    | categórico  | Agrupamento do cliente por faixa etária.                                              |
| `faixa_renda`    | categórico  | Agrupamento do cliente por faixa de renda.                                            |
| `canal_sugerido` | categórico  | Canal sugerido para contato com o cliente, com base nos dados cadastrais disponíveis. |

### Valores Permitidos - `faixa_idade`

| Valor                 | Descrição                    |
| --------------------- | ---------------------------- |
| `ate_24_anos`         | Cliente com até 24 anos.     |
| `25_a_34_anos`        | Cliente entre 25 e 34 anos.  |
| `35_a_44_anos`        | Cliente entre 35 e 44 anos.  |
| `45_a_59_anos`        | Cliente entre 45 e 59 anos.  |
| `60_anos_ou_mais`     | Cliente com 60 anos ou mais. |
| `idade_nao_informada` | Idade não disponível.        |

### Valores Permitidos - `faixa_renda`

| Valor                 | Descrição                           |
| --------------------- | ----------------------------------- |
| `ate_30_mil`          | Renda até 30 mil.                   |
| `30_a_60_mil`         | Renda acima de 30 mil até 60 mil.   |
| `60_a_120_mil`        | Renda acima de 60 mil até 120 mil.  |
| `120_a_240_mil`       | Renda acima de 120 mil até 240 mil. |
| `acima_240_mil`       | Renda acima de 240 mil.             |
| `renda_nao_informada` | Renda não disponível.               |

### Valores Permitidos - `canal_sugerido`

| Valor                     | Descrição                                                   |
| ------------------------- | ----------------------------------------------------------- |
| `email`                   | Cliente possui e-mail disponível.                           |
| `celular`                 | Cliente possui celular disponível ou contatável.            |
| `telefone`                | Cliente possui telefone disponível.                         |
| `canal_nao_identificado`  | Não foi possível identificar um canal de contato.           |
| `cadastro_nao_disponivel` | Cliente não possui cadastro disponível para enriquecimento. |

---

## Campos de Priorização

| Campo                             | Tipo lógico | Descrição                                                                                         |
| --------------------------------- | ----------- | ------------------------------------------------------------------------------------------------- |
| `prioridade_contato`              | categórico  | Prioridade recomendada para contato preventivo.                                                   |
| `flg_priorizar_contato`           | flag        | Indica se o cliente deve ser priorizado para contato.                                             |
| `acao_recomendada`                | categórico  | Ação recomendada para o cliente ou grupo de clientes.                                             |
| `grupo_negocio`                   | categórico  | Agrupamento de negócio para facilitar filtros e visualizações.                                    |
| `valor_previsto_total_priorizado` | monetário   | Valor previsto total associado aos clientes priorizados. Para clientes não priorizados, recebe 0. |

---

## Valores Permitidos - `prioridade_contato`

| Valor                | Descrição                                                           |
| -------------------- | ------------------------------------------------------------------- |
| `prioridade_maxima`  | Cliente de alto risco com maior atraso igual ou superior a 30 dias. |
| `prioridade_alta`    | Cliente de alto risco.                                              |
| `prioridade_media`   | Cliente de médio risco.                                             |
| `prioridade_revisao` | Cliente com risco desconhecido, exigindo revisão dos dados.         |
| `prioridade_baixa`   | Cliente de baixo risco.                                             |

---

## Valores Permitidos - `acao_recomendada`

| Valor                           | Descrição                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| `lembrete_preventivo_reforcado` | Comunicação mais forte para clientes de alto risco.                                    |
| `lembrete_preventivo_padrao`    | Comunicação preventiva padrão para clientes de médio risco.                            |
| `comunicacao_relacionamento`    | Comunicação leve de relacionamento para clientes de baixo risco com perfil antecipado. |
| `lembrete_suave`                | Lembrete leve para clientes de baixo risco.                                            |
| `revisar_dados_pagamento`       | Revisão necessária para clientes com risco desconhecido.                               |
| `acao_nao_classificada`         | Caso residual para regras não classificadas.                                           |

---

## Valores Permitidos - `grupo_negocio`

| Valor                    | Descrição                                                  |
| ------------------------ | ---------------------------------------------------------- |
| `clientes_prioritarios`  | Clientes de médio ou alto risco que devem ser priorizados. |
| `clientes_para_revisao`  | Clientes com risco desconhecido.                           |
| `clientes_monitoramento` | Clientes de baixo risco para acompanhamento.               |

---

## Campo de Processamento

| Campo                   | Tipo lógico | Descrição                                 |
| ----------------------- | ----------- | ----------------------------------------- |
| `dt_processamento_gold` | timestamp   | Data e hora em que a Gold foi processada. |

---

## Regras de Priorização

A priorização de contato segue a lógica abaixo:

| Condição                                               | Prioridade           |
| ------------------------------------------------------ | -------------------- |
| `nivel_risco = alto_risco` e `maior_atraso_dias >= 30` | `prioridade_maxima`  |
| `nivel_risco = alto_risco`                             | `prioridade_alta`    |
| `nivel_risco = medio_risco`                            | `prioridade_media`   |
| `nivel_risco = risco_desconhecido`                     | `prioridade_revisao` |
| demais casos                                           | `prioridade_baixa`   |

---

## Regra da Flag de Priorização

A flag `flg_priorizar_contato` recebe 1 quando:

```text
nivel_risco IN ('alto_risco', 'medio_risco', 'risco_desconhecido')
```

E recebe 0 quando:

```text
nivel_risco = 'baixo_risco'
```

---

## Regras de Ação Recomendada

| Condição                                                              | Ação recomendada                |
| --------------------------------------------------------------------- | ------------------------------- |
| `nivel_risco = alto_risco`                                            | `lembrete_preventivo_reforcado` |
| `nivel_risco = medio_risco`                                           | `lembrete_preventivo_padrao`    |
| `nivel_risco = baixo_risco` e `perfil_pagamento = pagador_antecipado` | `comunicacao_relacionamento`    |
| `nivel_risco = baixo_risco`                                           | `lembrete_suave`                |
| `nivel_risco = risco_desconhecido`                                    | `revisar_dados_pagamento`       |

---

## Observações para Power BI

Campos recomendados para cartões:

```text
total de clientes
clientes priorizados
clientes de alto risco
clientes de médio risco
clientes com cadastro
clientes sem cadastro
valor previsto total priorizado
```

Campos recomendados para gráficos:

```text
nivel_risco
prioridade_contato
acao_recomendada
perfil_pagamento
status_cadastro
faixa_idade
faixa_renda
canal_sugerido
grupo_negocio
```

Campos recomendados para filtros:

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
```

---

## Validações Realizadas

A Gold foi validada pelo script:

```text
scripts/10_validar_gold_indicadores_cliente.py
```

Principais validações aprovadas:

```text
339.587 clientes
339.587 clientes distintos
0 duplicados
0 colunas faltando
0 colunas extras
0 valores categóricos inválidos
0 flags fora do padrão
0 inconsistências de regras de negócio
0 diferença de volume entre Silver comportamento e Gold
```

---
