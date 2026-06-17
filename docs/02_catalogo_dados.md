# Catálogo de Dados

Este documento descreve os principais arquivos de dados utilizados e gerados no projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

O objetivo do catálogo é facilitar a navegação pelo projeto, mostrando:

* quais dados entram no pipeline;
* quais arquivos são gerados em cada camada;
* qual é a finalidade de cada arquivo;
* qual script cria ou valida cada etapa;
* qual arquivo deve ser usado no Power BI.

---

## 1. Visão Geral

O projeto utiliza uma arquitetura em camadas no padrão medalhão:

```text
raw
↓
bronze
↓
silver
↓
gold
```

Cada camada tem uma função específica:

| Camada | Função                                                                            |
| ------ | --------------------------------------------------------------------------------- |
| Raw    | Armazena os arquivos originais do dataset                                         |
| Bronze | Converte os arquivos originais para Parquet, mantendo estrutura próxima da origem |
| Silver | Trata, traduz, padroniza e cria regras reutilizáveis                              |
| Gold   | Consolida indicadores finais para análise de negócio e Power BI                   |

---

## 2. Diretórios de Dados

Os dados do projeto estão organizados dentro da pasta:

```text
data/
```

Estrutura principal:

```text
data/
├── raw/
├── bronze/
├── silver/
└── gold/
```

---

## 3. Camada Raw

A camada Raw contém os arquivos originais do dataset.

Local:

```text
data/raw/
```

Arquivos utilizados:

```text
application_train.csv
installments_payments.csv
```

---

### 3.1 `application_train.csv`

Arquivo com dados cadastrais e características dos clientes.

| Item              | Descrição                               |
| ----------------- | --------------------------------------- |
| Camada            | Raw                                     |
| Formato           | CSV                                     |
| Origem            | Dataset Home Credit                     |
| Granularidade     | 1 linha = 1 cliente no cadastro         |
| Uso no projeto    | Base para criação da Silver de clientes |
| Script consumidor | `scripts/01_origem_para_bronze.py`      |

Principais informações:

* identificador do cliente;
* tipo de contrato;
* gênero;
* renda;
* escolaridade;
* estado civil;
* tipo de moradia;
* ocupação;
* idade;
* valor de crédito;
* valor de anuidade;
* quantidade de filhos;
* quantidade de membros da família;
* informações de contato;
* histórico de inadimplência.

---

### 3.2 `installments_payments.csv`

Arquivo com histórico de parcelas e pagamentos.

| Item              | Descrição                                 |
| ----------------- | ----------------------------------------- |
| Camada            | Raw                                       |
| Formato           | CSV                                       |
| Origem            | Dataset Home Credit                       |
| Granularidade     | 1 linha = 1 parcela/pagamento             |
| Uso no projeto    | Base para criação da Silver de pagamentos |
| Script consumidor | `scripts/01_origem_para_bronze.py`        |

Principais informações:

* identificador do cliente;
* identificador do contrato anterior;
* número da parcela;
* versão da parcela;
* dia previsto de pagamento;
* dia real de pagamento;
* valor previsto;
* valor pago.

---

## 4. Camada Bronze

A camada Bronze contém os arquivos convertidos para Parquet, ainda próximos da estrutura original.

Local:

```text
data/bronze/
```

Arquivos gerados:

```text
bronze_clientes_cadastro.parquet
bronze_pagamentos_parcelas.parquet
```

Script responsável:

```text
scripts/01_origem_para_bronze.py
```

Script de validação:

```text
scripts/02_validar_bronze_arquivos.py
```

---

### 4.1 `bronze_clientes_cadastro.parquet`

Arquivo Bronze criado a partir do `application_train.csv`.

| Item              | Descrição                                   |
| ----------------- | ------------------------------------------- |
| Camada            | Bronze                                      |
| Formato           | Parquet                                     |
| Origem            | `data/raw/application_train.csv`            |
| Granularidade     | 1 linha = 1 cliente no cadastro             |
| Uso no projeto    | Entrada para criação da Silver de clientes  |
| Script gerador    | `scripts/01_origem_para_bronze.py`          |
| Script consumidor | `scripts/05_bronze_para_silver_clientes.py` |

Observação:

Na Bronze, as colunas podem manter os nomes originais do dataset, como `SK_ID_CURR`, `TARGET`, `AMT_INCOME_TOTAL` e `DAYS_BIRTH`.

Isso é esperado, porque a Bronze preserva rastreabilidade com a origem.

---

### 4.2 `bronze_pagamentos_parcelas.parquet`

Arquivo Bronze criado a partir do `installments_payments.csv`.

| Item              | Descrição                                     |
| ----------------- | --------------------------------------------- |
| Camada            | Bronze                                        |
| Formato           | Parquet                                       |
| Origem            | `data/raw/installments_payments.csv`          |
| Granularidade     | 1 linha = 1 parcela/pagamento                 |
| Uso no projeto    | Entrada para criação da Silver de pagamentos  |
| Script gerador    | `scripts/01_origem_para_bronze.py`            |
| Script consumidor | `scripts/03_bronze_para_silver_pagamentos.py` |

Observação:

Na Bronze, as colunas podem manter os nomes originais do dataset, como `SK_ID_CURR`, `DAYS_INSTALMENT`, `DAYS_ENTRY_PAYMENT`, `AMT_INSTALMENT` e `AMT_PAYMENT`.

---

## 5. Camada Silver

A camada Silver contém dados tratados, traduzidos, padronizados e enriquecidos com regras de negócio.

Local:

```text
data/silver/
```

Arquivos gerados:

```text
silver_pagamentos_parcelas.parquet
silver_clientes_cadastro.parquet
silver_comportamento_pagamento_cliente.parquet
```

---

## 6. Silver - Pagamentos por Parcela

Arquivo:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

| Item                | Descrição                                                   |
| ------------------- | ----------------------------------------------------------- |
| Camada              | Silver                                                      |
| Formato             | Parquet                                                     |
| Origem              | `data/bronze/bronze_pagamentos_parcelas.parquet`            |
| Granularidade       | 1 linha = 1 parcela/pagamento de um cliente                 |
| Script gerador      | `scripts/03_bronze_para_silver_pagamentos.py`               |
| Script de validação | `scripts/04_validar_silver_pagamentos.py`                   |
| Uso no projeto      | Base para cálculo do comportamento de pagamento por cliente |

Principais transformações:

* tradução dos campos para português;
* padronização em minúsculo e `snake_case`;
* cálculo de atraso e antecipação;
* criação de status de pagamento;
* criação de status de valor pago;
* criação de flags;
* identificação de nulos críticos.

Campos principais:

```text
id_cliente
id_contrato_anterior
versao_parcela
numero_parcela
dias_previsto_ref
dias_pagamento_ref
dif_dias_vencimento
dias_atraso
dias_antecipacao
valor_previsto
valor_pago
dif_valor_pago_previsto
status_pagamento
status_valor_pagamento
```

Regra principal:

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

Resultados validados:

| Indicador               |      Valor |
| ----------------------- | ---------: |
| Total de registros      | 13.605.401 |
| Pagamentos antecipados  |  9.309.477 |
| Pagamentos no prazo     |  3.146.350 |
| Pagamentos em atraso    |  1.146.669 |
| Pagamentos sem registro |      2.905 |
| Taxa geral de atraso    |      8,43% |

---

## 7. Silver - Clientes Cadastro

Arquivo:

```text
data/silver/silver_clientes_cadastro.parquet
```

| Item                | Descrição                                      |
| ------------------- | ---------------------------------------------- |
| Camada              | Silver                                         |
| Formato             | Parquet                                        |
| Origem              | `data/bronze/bronze_clientes_cadastro.parquet` |
| Granularidade       | 1 linha = 1 cliente no cadastro                |
| Script gerador      | `scripts/05_bronze_para_silver_clientes.py`    |
| Script de validação | `scripts/06_validar_silver_clientes.py`        |
| Uso no projeto      | Enriquecer a Gold com dados cadastrais         |

Principais transformações:

* tradução dos campos para português;
* padronização em minúsculo e `snake_case`;
* cálculo de idade em anos;
* criação de indicadores cadastrais;
* criação de razões financeiras;
* identificação de nulos críticos;
* padronização de categorias.

Campos principais:

```text
id_cliente
flg_inadimplencia_historica
tipo_contrato
genero
tipo_renda
escolaridade
estado_civil
tipo_moradia
ocupacao
idade_anos
renda_total
valor_credito
valor_anuidade
valor_bens
razao_credito_renda
razao_anuidade_renda
qtd_filhos
qtd_membros_familia
flg_possui_carro
flg_possui_imovel
flg_possui_celular
flg_celular_contatavel
flg_possui_telefone
flg_possui_email
```

Resultados validados:

| Indicador                  |   Valor |
| -------------------------- | ------: |
| Total de registros         | 307.511 |
| Clientes distintos         | 307.511 |
| Registros duplicados       |       0 |
| Registros com nulo crítico |      12 |

Observação:

O campo `renda_total` possui valores extremos. Para análises no Power BI, recomenda-se usar faixas, mediana ou percentis, evitando depender apenas da média.

---

## 8. Silver - Comportamento de Pagamento por Cliente

Arquivo:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

| Item                | Descrição                                            |
| ------------------- | ---------------------------------------------------- |
| Camada              | Silver                                               |
| Formato             | Parquet                                              |
| Origem              | `data/silver/silver_pagamentos_parcelas.parquet`     |
| Granularidade       | 1 linha = 1 cliente com histórico de pagamento       |
| Script gerador      | `scripts/07_criar_silver_comportamento_cliente.py`   |
| Script de validação | `scripts/08_validar_silver_comportamento_cliente.py` |
| Uso no projeto      | Base principal para criação da Gold                  |

Principais transformações:

* agregação dos pagamentos por cliente;
* cálculo de totais de parcelas;
* cálculo de taxa de atraso;
* cálculo de maior atraso histórico;
* cálculo de maior antecipação;
* cálculo de valores totais;
* classificação do perfil de pagamento;
* classificação do nível de risco.

Campos principais:

```text
id_cliente
qtd_parcelas_total
qtd_parcelas_validas
qtd_parcelas_atraso
qtd_pagas_antecipado
qtd_pagas_no_prazo
taxa_atraso_pct
media_dias_vs_vencimento
media_dias_atraso
maior_atraso_dias
maior_antecipacao_dias
valor_previsto_total
valor_pago_total
dif_valor_pago_previsto_total
perfil_pagamento
nivel_risco
```

Resultados validados:

| Indicador                           |   Valor |
| ----------------------------------- | ------: |
| Clientes com histórico de pagamento | 339.587 |
| `baixo_risco`                       | 210.109 |
| `medio_risco`                       |  92.276 |
| `alto_risco`                        |  37.193 |
| `risco_desconhecido`                |       9 |

Cobertura com cadastro:

| Indicador                 |   Valor |
| ------------------------- | ------: |
| Clientes no comportamento | 339.587 |
| Clientes com cadastro     | 291.643 |
| Clientes sem cadastro     |  47.944 |
| Percentual com cadastro   |  85,88% |

---

## 9. Camada Gold

A camada Gold contém a visão final para consumo analítico.

Local:

```text
data/gold/
```

Arquivo final:

```text
gold_indicadores_cliente.parquet
```

---

## 10. Gold - Indicadores por Cliente

Arquivo:

```text
data/gold/gold_indicadores_cliente.parquet
```

| Item                     | Descrição                                                    |
| ------------------------ | ------------------------------------------------------------ |
| Camada                   | Gold                                                         |
| Formato                  | Parquet                                                      |
| Origem principal         | `data/silver/silver_comportamento_pagamento_cliente.parquet` |
| Origem de enriquecimento | `data/silver/silver_clientes_cadastro.parquet`               |
| Granularidade            | 1 linha = 1 cliente com histórico de pagamento               |
| Script gerador           | `scripts/09_criar_gold_indicadores_cliente.py`               |
| Script de validação      | `scripts/10_validar_gold_indicadores_cliente.py`             |
| Uso no projeto           | Fonte principal para Power BI e futura camada de IA/RAG      |

Decisão de modelagem:

A Gold parte da Silver de comportamento de pagamento e faz enriquecimento com a Silver de clientes usando `LEFT JOIN`.

Essa decisão mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

Campos principais:

```text
id_cliente
nivel_risco
perfil_pagamento
taxa_atraso_pct
media_dias_atraso
maior_atraso_dias
valor_previsto_total
valor_pago_total
flg_cliente_com_cadastro
status_cadastro
genero
tipo_renda
escolaridade
estado_civil
tipo_moradia
ocupacao
idade_anos
renda_total
faixa_idade
faixa_renda
canal_sugerido
prioridade_contato
flg_priorizar_contato
acao_recomendada
grupo_negocio
valor_previsto_total_priorizado
dt_processamento_gold
```

Resultados validados:

| Indicador               |   Valor |
| ----------------------- | ------: |
| Total de clientes       | 339.587 |
| Clientes com cadastro   | 291.643 |
| Clientes sem cadastro   |  47.944 |
| Percentual com cadastro |  85,88% |
| Clientes priorizados    | 129.478 |

Distribuição por nível de risco:

| Nível de risco       | Clientes |
| -------------------- | -------: |
| `baixo_risco`        |  210.109 |
| `medio_risco`        |   92.276 |
| `alto_risco`         |   37.193 |
| `risco_desconhecido` |        9 |

Distribuição por prioridade:

| Prioridade           | Clientes |
| -------------------- | -------: |
| `prioridade_baixa`   |  210.109 |
| `prioridade_media`   |   92.276 |
| `prioridade_maxima`  |   23.707 |
| `prioridade_alta`    |   13.486 |
| `prioridade_revisao` |        9 |

Distribuição por ação recomendada:

| Ação recomendada                | Clientes |
| ------------------------------- | -------: |
| `comunicacao_relacionamento`    |  151.500 |
| `lembrete_preventivo_padrao`    |   92.276 |
| `lembrete_suave`                |   58.609 |
| `lembrete_preventivo_reforcado` |   37.193 |
| `revisar_dados_pagamento`       |        9 |

---

## 11. Arquivo Recomendado para Power BI

O arquivo recomendado para o dashboard é:

```text
data/gold/gold_indicadores_cliente.parquet
```

Esse arquivo deve ser a fonte principal do Power BI, pois já contém:

* comportamento de pagamento;
* risco;
* prioridade;
* ação recomendada;
* canal sugerido;
* dados cadastrais enriquecidos;
* cobertura cadastral;
* valor previsto priorizado.

---

## 12. Documentos Relacionados aos Dados

Documentos principais para entender os dados:

```text
docs/03_dicionario_dados.md
docs/04_arquitetura.md
docs/05_metricas_gold.md
docs/07_mapeamento_perguntas_negocio.md
docs/08_etapas_pipeline.md
docs/09_dicionario_gold_indicadores_cliente.md
docs/10_regras_negocio_priorizacao.md
```

---

## 13. Observações de Governança

* Os arquivos de dados locais não precisam ser versionados no GitHub.
* A documentação e os scripts são versionados.
* A Bronze preserva rastreabilidade com os dados originais.
* A Silver concentra tratamento, padronização e regras reutilizáveis.
* A Gold deve ser usada como camada final de consumo.
* As regras de risco são regras de negócio, não modelo preditivo supervisionado.
* Antes de uso em produção, seria necessário validar privacidade, jurídico, canais de comunicação e governança de dados.

---

## 14. Resumo do Fluxo de Dados

O fluxo de dados do projeto segue a arquitetura medalhão, organizando os dados em camadas até chegar em uma visão final preparada para análise de negócio.

---

### 14.1 Entrada dos Dados

O pipeline começa com dois arquivos originais na camada Raw:

```text
data/raw/application_train.csv
data/raw/installments_payments.csv
```

O arquivo `application_train.csv` contém informações cadastrais dos clientes.

O arquivo `installments_payments.csv` contém o histórico de parcelas e pagamentos.

---

### 14.2 Conversão para Bronze

Na camada Bronze, os arquivos originais são convertidos para Parquet, mantendo a estrutura próxima da origem.

Arquivos gerados:

```text
data/bronze/bronze_clientes_cadastro.parquet
data/bronze/bronze_pagamentos_parcelas.parquet
```

Objetivo da Bronze:

```text
preservar rastreabilidade com os dados originais
```

---

### 14.3 Tratamento na Silver

Na camada Silver, os dados são traduzidos, padronizados e enriquecidos com regras de negócio.

Arquivos gerados:

```text
data/silver/silver_clientes_cadastro.parquet
data/silver/silver_pagamentos_parcelas.parquet
data/silver/silver_comportamento_pagamento_cliente.parquet
```

A Silver de clientes trata os dados cadastrais.

A Silver de pagamentos calcula atraso, antecipação, status de pagamento e status de valor pago.

A Silver de comportamento consolida o histórico de pagamentos por cliente e cria métricas como taxa de atraso, maior atraso, perfil de pagamento e nível de risco.

---

### 14.4 Consolidação na Gold

A camada Gold une comportamento de pagamento e cadastro para criar uma visão final por cliente.

Arquivo final:

```text
data/gold/gold_indicadores_cliente.parquet
```

Essa tabela contém os principais campos de negócio:

```text
nivel_risco
perfil_pagamento
prioridade_contato
flg_priorizar_contato
acao_recomendada
canal_sugerido
status_cadastro
valor_previsto_total_priorizado
```

A Gold é a principal fonte para análise no Power BI.

---

### 14.5 Consumo Analítico

A tabela Gold pode ser consumida por:

```text
Power BI
Futura camada de IA/RAG
```

No Power BI, ela apoia visualizações sobre risco, prioridade, ação recomendada, canal sugerido e cobertura cadastral.

Na futura camada de IA/RAG, ela poderá apoiar perguntas em linguagem natural e explicações sobre as regras de negócio.

---

### 14.6 Visão Simplificada do Pipeline

```text
application_train.csv
        ↓
bronze_clientes_cadastro.parquet
        ↓
silver_clientes_cadastro.parquet
        ↓
gold_indicadores_cliente.parquet
        ↓
Power BI / IA-RAG


installments_payments.csv
        ↓
bronze_pagamentos_parcelas.parquet
        ↓
silver_pagamentos_parcelas.parquet
        ↓
silver_comportamento_pagamento_cliente.parquet
        ↓
gold_indicadores_cliente.parquet
        ↓
Power BI / IA-RAG
```

Resumo da lógica:

```text
cadastro + comportamento de pagamento
        ↓
indicadores por cliente
        ↓
risco, prioridade, ação recomendada e canal sugerido
```

A Gold final entrega uma visão analítica orientada à ação.
