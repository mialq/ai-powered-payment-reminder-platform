# Dicionário de Dados

Este documento descreve os principais arquivos, tabelas e campos utilizados no projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

O objetivo do dicionário é explicar, de forma simples e rastreável, como os dados brutos foram transformados nas camadas `bronze`, `silver` e `gold`.

---

## 1. Convenção de Nomenclatura

A partir da camada Silver, os nomes foram padronizados em português, minúsculo e `snake_case`.

Exemplo:

| Padrão antigo/origem | Padrão adotado         |
| -------------------- | ---------------------- |
| `SK_ID_CURR`         | `id_cliente`           |
| `SK_ID_PREV`         | `id_contrato_anterior` |
| `DAYS_INSTALMENT`    | `dias_previsto_ref`    |
| `DAYS_ENTRY_PAYMENT` | `dias_pagamento_ref`   |
| `AMT_INSTALMENT`     | `valor_previsto`       |
| `AMT_PAYMENT`        | `valor_pago`           |

As camadas do projeto continuam com nomes técnicos em inglês:

```text
raw
bronze
silver
gold
```

Mas os arquivos, colunas e valores categóricos foram padronizados em português sempre que possível.

---

## 2. Visão Geral das Camadas

| Camada | Objetivo                                           | Exemplo de arquivo                                                                                                         |
| ------ | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Raw    | Dados originais em CSV                             | `application_train.csv`, `installments_payments.csv`                                                                       |
| Bronze | Dados convertidos para Parquet, próximos da origem | `bronze_clientes_cadastro.parquet`, `bronze_pagamentos_parcelas.parquet`                                                   |
| Silver | Dados tratados, traduzidos e padronizados          | `silver_pagamentos_parcelas.parquet`, `silver_clientes_cadastro.parquet`, `silver_comportamento_pagamento_cliente.parquet` |
| Gold   | Dados finais para análise de negócio e Power BI    | `gold_indicadores_cliente.parquet`                                                                                         |

---

## 3. Arquivos Raw

Os arquivos Raw são os arquivos originais do dataset.

### `application_train.csv`

Arquivo de cadastro e características dos clientes.

Principais informações utilizadas:

| Campo original        | Descrição                            |
| --------------------- | ------------------------------------ |
| `SK_ID_CURR`          | Identificador do cliente             |
| `TARGET`              | Indicador de inadimplência histórica |
| `NAME_CONTRACT_TYPE`  | Tipo de contrato                     |
| `CODE_GENDER`         | Gênero                               |
| `NAME_INCOME_TYPE`    | Tipo de renda                        |
| `NAME_EDUCATION_TYPE` | Escolaridade                         |
| `NAME_FAMILY_STATUS`  | Estado civil                         |
| `NAME_HOUSING_TYPE`   | Tipo de moradia                      |
| `OCCUPATION_TYPE`     | Ocupação                             |
| `DAYS_BIRTH`          | Idade em dias negativos              |
| `AMT_INCOME_TOTAL`    | Renda total                          |
| `AMT_CREDIT`          | Valor do crédito                     |
| `AMT_ANNUITY`         | Valor da anuidade/parcela            |
| `AMT_GOODS_PRICE`     | Valor dos bens                       |
| `CNT_CHILDREN`        | Quantidade de filhos                 |
| `CNT_FAM_MEMBERS`     | Quantidade de membros da família     |
| `FLAG_OWN_CAR`        | Indica se possui carro               |
| `FLAG_OWN_REALTY`     | Indica se possui imóvel              |

---

### `installments_payments.csv`

Arquivo de histórico de parcelas e pagamentos.

Principais informações utilizadas:

| Campo original           | Descrição                                          |
| ------------------------ | -------------------------------------------------- |
| `SK_ID_CURR`             | Identificador do cliente                           |
| `SK_ID_PREV`             | Identificador do contrato anterior                 |
| `NUM_INSTALMENT_VERSION` | Versão da parcela                                  |
| `NUM_INSTALMENT_NUMBER`  | Número da parcela                                  |
| `DAYS_INSTALMENT`        | Dia previsto de vencimento, em referência relativa |
| `DAYS_ENTRY_PAYMENT`     | Dia real de pagamento, em referência relativa      |
| `AMT_INSTALMENT`         | Valor previsto da parcela                          |
| `AMT_PAYMENT`            | Valor efetivamente pago                            |

---

## 4. Arquivos Bronze

A camada Bronze armazena os dados em formato Parquet, ainda próximos da origem.

Arquivos:

```text
data/bronze/bronze_clientes_cadastro.parquet
data/bronze/bronze_pagamentos_parcelas.parquet
```

Na Bronze, as colunas ainda podem manter os nomes originais do dataset, como `SK_ID_CURR`, `DAYS_INSTALMENT` e `AMT_PAYMENT`.

Isso é esperado, porque a Bronze representa a primeira organização dos dados, antes da tradução e padronização.

---

## 5. Silver - Pagamentos por Parcela

Arquivo:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

Granularidade:

```text
1 linha = 1 parcela/pagamento de um cliente
```

Essa tabela traduz e padroniza os dados de pagamento.

### Campos principais

| Campo                     | Tipo lógico | Descrição                                                   |
| ------------------------- | ----------- | ----------------------------------------------------------- |
| `id_cliente`              | inteiro     | Identificador do cliente.                                   |
| `id_contrato_anterior`    | inteiro     | Identificador do contrato anterior associado ao pagamento.  |
| `versao_parcela`          | numérico    | Versão da parcela no contrato.                              |
| `numero_parcela`          | inteiro     | Número da parcela.                                          |
| `dias_previsto_ref`       | numérico    | Dia previsto de vencimento em referência relativa.          |
| `dias_pagamento_ref`      | numérico    | Dia real de pagamento em referência relativa.               |
| `dif_dias_vencimento`     | numérico    | Diferença entre o dia de pagamento e o dia previsto.        |
| `dias_atraso`             | numérico    | Quantidade de dias de atraso. Nunca deve ser negativa.      |
| `dias_antecipacao`        | numérico    | Quantidade de dias de antecipação. Nunca deve ser negativa. |
| `valor_previsto`          | monetário   | Valor previsto da parcela.                                  |
| `valor_pago`              | monetário   | Valor efetivamente pago.                                    |
| `dif_valor_pago_previsto` | monetário   | Diferença entre valor pago e valor previsto.                |
| `status_pagamento`        | categórico  | Classificação do pagamento em relação ao vencimento.        |
| `status_valor_pagamento`  | categórico  | Classificação do pagamento em relação ao valor previsto.    |
| `arquivo_origem`          | texto       | Nome do arquivo de origem.                                  |
| `arquivo_bronze`          | texto       | Nome do arquivo Bronze utilizado.                           |
| `dt_processamento_silver` | timestamp   | Data e hora de processamento da Silver.                     |

---

## 6. Regra Principal de Vencimento

A principal regra da Silver de pagamentos é:

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

---

## 7. Valores Permitidos - `status_pagamento`

| Valor                      | Descrição                                |
| -------------------------- | ---------------------------------------- |
| `pago_antecipado`          | Pagamento realizado antes do vencimento. |
| `pago_no_prazo`            | Pagamento realizado exatamente no prazo. |
| `pago_em_atraso`           | Pagamento realizado após o vencimento.   |
| `sem_pagamento_registrado` | Pagamento sem data ou valor registrado.  |

---

## 8. Valores Permitidos - `status_valor_pagamento`

| Valor                       | Descrição                              |
| --------------------------- | -------------------------------------- |
| `pagamento_integral`        | Valor pago igual ao valor previsto.    |
| `pagamento_parcial`         | Valor pago menor que o valor previsto. |
| `pagamento_acima_previsto`  | Valor pago maior que o valor previsto. |
| `valor_pago_nao_registrado` | Valor pago não informado.              |

---

## 9. Silver - Clientes Cadastro

Arquivo:

```text
data/silver/silver_clientes_cadastro.parquet
```

Granularidade:

```text
1 linha = 1 cliente no cadastro
```

Essa tabela traduz e padroniza os dados cadastrais dos clientes.

### Campos principais

| Campo                         | Tipo lógico | Descrição                                              |
| ----------------------------- | ----------- | ------------------------------------------------------ |
| `id_cliente`                  | inteiro     | Identificador único do cliente.                        |
| `flg_inadimplencia_historica` | flag        | Indica histórico de inadimplência na base de cadastro. |
| `tipo_contrato`               | categórico  | Tipo de contrato do cliente.                           |
| `genero`                      | categórico  | Gênero informado no cadastro.                          |
| `tipo_renda`                  | categórico  | Tipo de renda declarada.                               |
| `escolaridade`                | categórico  | Escolaridade do cliente.                               |
| `estado_civil`                | categórico  | Estado civil do cliente.                               |
| `tipo_moradia`                | categórico  | Tipo de moradia informado.                             |
| `ocupacao`                    | categórico  | Ocupação profissional do cliente.                      |
| `idade_anos`                  | inteiro     | Idade aproximada do cliente em anos.                   |
| `renda_total`                 | monetário   | Renda total informada.                                 |
| `valor_credito`               | monetário   | Valor do crédito.                                      |
| `valor_anuidade`              | monetário   | Valor da anuidade ou parcela anualizada.               |
| `valor_bens`                  | monetário   | Valor dos bens associados à solicitação.               |
| `razao_credito_renda`         | numérico    | Relação entre valor do crédito e renda total.          |
| `razao_anuidade_renda`        | numérico    | Relação entre valor da anuidade e renda total.         |
| `qtd_filhos`                  | inteiro     | Quantidade de filhos.                                  |
| `qtd_membros_familia`         | numérico    | Quantidade de membros da família.                      |
| `flg_possui_carro`            | flag        | Indica se o cliente possui carro.                      |
| `flg_possui_imovel`           | flag        | Indica se o cliente possui imóvel.                     |
| `flg_possui_celular`          | flag        | Indica se o cliente possui celular informado.          |
| `flg_celular_contatavel`      | flag        | Indica se o celular é considerado contatável.          |
| `flg_possui_telefone`         | flag        | Indica se o cliente possui telefone informado.         |
| `flg_possui_email`            | flag        | Indica se o cliente possui e-mail informado.           |
| `flg_anuidade_nula`           | flag        | Indica se o valor da anuidade está nulo.               |
| `qtd_nulos_criticos`          | inteiro     | Quantidade de campos críticos nulos no cadastro.       |
| `flg_nulo_critico`            | flag        | Indica se existe algum campo crítico nulo.             |
| `arquivo_origem`              | texto       | Nome do arquivo de origem.                             |
| `arquivo_bronze`              | texto       | Nome do arquivo Bronze utilizado.                      |
| `dt_processamento_silver`     | timestamp   | Data e hora de processamento da Silver.                |

---

## 10. Silver - Comportamento de Pagamento por Cliente

Arquivo:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Granularidade:

```text
1 linha = 1 cliente com histórico de pagamento
```

Essa tabela consolida o comportamento de pagamento de cada cliente.

### Campos principais

| Campo                            | Tipo lógico | Descrição                                                           |
| -------------------------------- | ----------- | ------------------------------------------------------------------- |
| `id_cliente`                     | inteiro     | Identificador do cliente.                                           |
| `qtd_parcelas_total`             | inteiro     | Total de parcelas associadas ao cliente.                            |
| `qtd_parcelas_validas`           | inteiro     | Total de parcelas com pagamento registrado.                         |
| `qtd_parcelas_atraso`            | numérico    | Total de parcelas pagas em atraso.                                  |
| `qtd_pagas_antecipado`           | numérico    | Total de parcelas pagas antecipadamente.                            |
| `qtd_pagas_no_prazo`             | numérico    | Total de parcelas pagas no prazo.                                   |
| `taxa_atraso_pct`                | percentual  | Percentual de atraso em relação às parcelas válidas.                |
| `media_dias_vs_vencimento`       | numérico    | Média da diferença entre pagamento e vencimento. Pode ser negativa. |
| `media_dias_atraso`              | numérico    | Média de dias de atraso considerando apenas pagamentos atrasados.   |
| `maior_atraso_dias`              | numérico    | Maior atraso histórico do cliente.                                  |
| `maior_antecipacao_dias`         | numérico    | Maior antecipação histórica do cliente.                             |
| `valor_previsto_total`           | monetário   | Soma total dos valores previstos.                                   |
| `valor_pago_total`               | monetário   | Soma total dos valores pagos.                                       |
| `dif_valor_pago_previsto_total`  | monetário   | Diferença entre valor pago total e valor previsto total.            |
| `qtd_registros_com_nulo_critico` | inteiro     | Quantidade de registros com campos críticos nulos.                  |
| `qtd_campos_criticos_nulos`      | inteiro     | Quantidade total de campos críticos nulos.                          |
| `qtd_pagamentos_parciais`        | inteiro     | Quantidade de pagamentos parciais.                                  |
| `qtd_pagamentos_acima_previsto`  | inteiro     | Quantidade de pagamentos acima do valor previsto.                   |
| `perfil_pagamento`               | categórico  | Perfil comportamental do cliente.                                   |
| `nivel_risco`                    | categórico  | Classificação de risco do cliente.                                  |
| `dt_processamento_silver`        | timestamp   | Data e hora de processamento da Silver.                             |

---

## 11. Valores Permitidos - `perfil_pagamento`

| Valor                        | Descrição                                               |
| ---------------------------- | ------------------------------------------------------- |
| `pagador_antecipado`         | Cliente costuma pagar antes do vencimento.              |
| `pagador_no_prazo`           | Cliente não apresenta atrasos e costuma pagar no prazo. |
| `baixo_atraso`               | Cliente possui baixa taxa de atraso.                    |
| `atraso_moderado`            | Cliente possui comportamento moderado de atraso.        |
| `alto_atraso`                | Cliente possui comportamento elevado de atraso.         |
| `comportamento_desconhecido` | Cliente sem dados suficientes para classificação.       |

---

## 12. Valores Permitidos - `nivel_risco`

| Valor                | Descrição                                                |
| -------------------- | -------------------------------------------------------- |
| `baixo_risco`        | Cliente com baixo comportamento histórico de atraso.     |
| `medio_risco`        | Cliente com sinais relevantes de atraso.                 |
| `alto_risco`         | Cliente com atraso frequente ou severo.                  |
| `risco_desconhecido` | Cliente sem dados suficientes para classificação segura. |

---

## 13. Gold - Indicadores por Cliente

Arquivo:

```text
data/gold/gold_indicadores_cliente.parquet
```

Granularidade:

```text
1 linha = 1 cliente com histórico de pagamento
```

Essa tabela é a camada final do projeto para análise no Power BI.

A Gold parte da Silver de comportamento de pagamento e faz enriquecimento com a Silver de cadastro usando `LEFT JOIN`.

Isso mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

---

## 14. Campos Principais da Gold

| Campo                             | Tipo lógico | Descrição                                             |
| --------------------------------- | ----------- | ----------------------------------------------------- |
| `id_cliente`                      | inteiro     | Identificador único do cliente.                       |
| `nivel_risco`                     | categórico  | Classificação de risco do cliente.                    |
| `perfil_pagamento`                | categórico  | Perfil histórico de pagamento.                        |
| `qtd_parcelas_total`              | inteiro     | Total de parcelas associadas ao cliente.              |
| `qtd_parcelas_validas`            | inteiro     | Total de parcelas com pagamento registrado.           |
| `qtd_parcelas_atraso`             | numérico    | Total de parcelas pagas em atraso.                    |
| `taxa_atraso_pct`                 | percentual  | Percentual de atraso do cliente.                      |
| `media_dias_atraso`               | numérico    | Média de dias de atraso.                              |
| `maior_atraso_dias`               | numérico    | Maior atraso histórico do cliente.                    |
| `valor_previsto_total`            | monetário   | Valor total previsto das parcelas do cliente.         |
| `valor_pago_total`                | monetário   | Valor total pago pelo cliente.                        |
| `flg_cliente_com_cadastro`        | flag        | Indica se o cliente possui cadastro disponível.       |
| `status_cadastro`                 | categórico  | Indica se o cliente foi encontrado na base cadastral. |
| `genero`                          | categórico  | Gênero informado no cadastro.                         |
| `tipo_renda`                      | categórico  | Tipo de renda do cliente.                             |
| `escolaridade`                    | categórico  | Escolaridade do cliente.                              |
| `estado_civil`                    | categórico  | Estado civil do cliente.                              |
| `tipo_moradia`                    | categórico  | Tipo de moradia do cliente.                           |
| `ocupacao`                        | categórico  | Ocupação do cliente.                                  |
| `idade_anos`                      | inteiro     | Idade aproximada do cliente.                          |
| `renda_total`                     | monetário   | Renda total informada.                                |
| `faixa_idade`                     | categórico  | Faixa etária do cliente.                              |
| `faixa_renda`                     | categórico  | Faixa de renda do cliente.                            |
| `canal_sugerido`                  | categórico  | Canal sugerido para contato.                          |
| `prioridade_contato`              | categórico  | Prioridade recomendada para contato preventivo.       |
| `flg_priorizar_contato`           | flag        | Indica se o cliente deve ser priorizado.              |
| `acao_recomendada`                | categórico  | Ação recomendada para o cliente.                      |
| `grupo_negocio`                   | categórico  | Agrupamento de negócio.                               |
| `valor_previsto_total_priorizado` | monetário   | Valor previsto associado aos clientes priorizados.    |
| `dt_processamento_gold`           | timestamp   | Data e hora de processamento da Gold.                 |

---

## 15. Valores Permitidos - `status_cadastro`

| Valor                  | Descrição                                                        |
| ---------------------- | ---------------------------------------------------------------- |
| `cliente_com_cadastro` | Cliente encontrado na Silver de cadastro.                        |
| `cliente_sem_cadastro` | Cliente com histórico de pagamento, mas sem cadastro disponível. |

---

## 16. Valores Permitidos - `faixa_idade`

| Valor                 | Descrição                    |
| --------------------- | ---------------------------- |
| `ate_24_anos`         | Cliente com até 24 anos.     |
| `25_a_34_anos`        | Cliente entre 25 e 34 anos.  |
| `35_a_44_anos`        | Cliente entre 35 e 44 anos.  |
| `45_a_59_anos`        | Cliente entre 45 e 59 anos.  |
| `60_anos_ou_mais`     | Cliente com 60 anos ou mais. |
| `idade_nao_informada` | Idade não disponível.        |

---

## 17. Valores Permitidos - `faixa_renda`

| Valor                 | Descrição                           |
| --------------------- | ----------------------------------- |
| `ate_30_mil`          | Renda até 30 mil.                   |
| `30_a_60_mil`         | Renda acima de 30 mil até 60 mil.   |
| `60_a_120_mil`        | Renda acima de 60 mil até 120 mil.  |
| `120_a_240_mil`       | Renda acima de 120 mil até 240 mil. |
| `acima_240_mil`       | Renda acima de 240 mil.             |
| `renda_nao_informada` | Renda não disponível.               |

---

## 18. Valores Permitidos - `canal_sugerido`

| Valor                     | Descrição                                        |
| ------------------------- | ------------------------------------------------ |
| `email`                   | Cliente possui e-mail disponível.                |
| `celular`                 | Cliente possui celular disponível ou contatável. |
| `telefone`                | Cliente possui telefone disponível.              |
| `canal_nao_identificado`  | Não foi possível identificar canal de contato.   |
| `cadastro_nao_disponivel` | Cliente sem cadastro disponível.                 |

---

## 19. Valores Permitidos - `prioridade_contato`

| Valor                | Descrição                                                           |
| -------------------- | ------------------------------------------------------------------- |
| `prioridade_maxima`  | Cliente de alto risco com maior atraso igual ou superior a 30 dias. |
| `prioridade_alta`    | Cliente de alto risco.                                              |
| `prioridade_media`   | Cliente de médio risco.                                             |
| `prioridade_revisao` | Cliente com risco desconhecido.                                     |
| `prioridade_baixa`   | Cliente de baixo risco.                                             |

---

## 20. Valores Permitidos - `acao_recomendada`

| Valor                           | Descrição                                                            |
| ------------------------------- | -------------------------------------------------------------------- |
| `lembrete_preventivo_reforcado` | Comunicação reforçada para clientes de alto risco.                   |
| `lembrete_preventivo_padrao`    | Comunicação preventiva padrão para clientes de médio risco.          |
| `comunicacao_relacionamento`    | Comunicação leve para clientes de baixo risco com perfil antecipado. |
| `lembrete_suave`                | Lembrete leve para clientes de baixo risco.                          |
| `revisar_dados_pagamento`       | Revisão necessária para clientes com risco desconhecido.             |

---

## 21. Valores Permitidos - `grupo_negocio`

| Valor                    | Descrição                        |
| ------------------------ | -------------------------------- |
| `clientes_prioritarios`  | Clientes de médio ou alto risco. |
| `clientes_para_revisao`  | Clientes com risco desconhecido. |
| `clientes_monitoramento` | Clientes de baixo risco.         |

---

## 22. Interpretação de Flags

Campos iniciados com `flg_` representam indicadores binários.

| Valor | Significado |
| ----: | ----------- |
|     0 | Não         |
|     1 | Sim         |

Exemplos:

| Campo                      | Interpretação                                         |
| -------------------------- | ----------------------------------------------------- |
| `flg_pagamento_atrasado`   | Indica se o pagamento foi atrasado.                   |
| `flg_cliente_com_cadastro` | Indica se o cliente possui cadastro disponível.       |
| `flg_priorizar_contato`    | Indica se o cliente deve ser priorizado para contato. |
| `flg_nulo_critico`         | Indica se existe algum campo crítico nulo.            |

---

## 23. Principais Indicadores Validados

### Silver de pagamentos

| Indicador               |      Valor |
| ----------------------- | ---------: |
| Total de registros      | 13.605.401 |
| Pagamentos antecipados  |  9.309.477 |
| Pagamentos no prazo     |  3.146.350 |
| Pagamentos em atraso    |  1.146.669 |
| Pagamentos sem registro |      2.905 |
| Taxa geral de atraso    |      8,43% |

### Silver de clientes

| Indicador                     |   Valor |
| ----------------------------- | ------: |
| Total de clientes no cadastro | 307.511 |
| Clientes distintos            | 307.511 |
| Registros duplicados          |       0 |
| Registros com nulo crítico    |      12 |

### Silver de comportamento por cliente

| Indicador                           |   Valor |
| ----------------------------------- | ------: |
| Clientes com histórico de pagamento | 339.587 |
| Baixo risco                         | 210.109 |
| Médio risco                         |  92.276 |
| Alto risco                          |  37.193 |
| Risco desconhecido                  |       9 |

### Gold de indicadores

| Indicador               |   Valor |
| ----------------------- | ------: |
| Total de clientes       | 339.587 |
| Clientes com cadastro   | 291.643 |
| Clientes sem cadastro   |  47.944 |
| Percentual com cadastro |  85,88% |
| Clientes priorizados    | 129.478 |

---

## 24. Observações Importantes

* A Bronze mantém os dados próximos da origem.
* A Silver aplica tradução, padronização, regras e tratamento.
* A Gold entrega a visão final para análise de negócio.
* A classificação de risco é baseada em regras de negócio, não em modelo preditivo supervisionado.
* As datas do dataset são relativas, não datas reais de calendário.
* Clientes sem cadastro foram mantidos na Gold para preservar o histórico de pagamento.
* A renda possui valores extremos; análises financeiras devem considerar faixas, mediana ou percentis.
* O campo `valor_previsto_total_priorizado` deve ser formatado no Power BI como número decimal ou moeda, evitando notação científica.

---

## 25. Documentos Relacionados

Este dicionário deve ser lido junto com:

```text
docs/05_metricas_gold.md
docs/07_mapeamento_perguntas_negocio.md
docs/08_etapas_pipeline.md
docs/09_dicionario_gold_indicadores_cliente.md
docs/10_regras_negocio_priorizacao.md
```
