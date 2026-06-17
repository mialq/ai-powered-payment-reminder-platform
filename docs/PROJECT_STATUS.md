# Project Status

Status atual do projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

---

## Situação Geral

O pipeline medalhão do projeto foi reorganizado e executado com sucesso.

As camadas `bronze`, `silver` e `gold` foram padronizadas, os scripts foram renomeados em português e a tabela final da Gold foi criada para consumo no Power BI.

---

## Camada Gold Atual

Arquivo final da Gold:

```text
data/gold/gold_indicadores_cliente.parquet
```

Granularidade:

```text
1 linha = 1 cliente com histórico de pagamento
```

Total de clientes:

| Indicador               |   Valor |
| ----------------------- | ------: |
| Total de clientes       | 339.587 |
| Clientes com cadastro   | 291.643 |
| Clientes sem cadastro   |  47.944 |
| Percentual com cadastro |  85,88% |
| Clientes priorizados    | 129.478 |

---

## Distribuição por Nível de Risco

| Nível de risco       | Clientes |
| -------------------- | -------: |
| `baixo_risco`        |  210.109 |
| `medio_risco`        |   92.276 |
| `alto_risco`         |   37.193 |
| `risco_desconhecido` |        9 |

---

## Distribuição por Prioridade de Contato

| Prioridade           | Clientes |
| -------------------- | -------: |
| `prioridade_baixa`   |  210.109 |
| `prioridade_media`   |   92.276 |
| `prioridade_maxima`  |   23.707 |
| `prioridade_alta`    |   13.486 |
| `prioridade_revisao` |        9 |

---

## Distribuição por Ação Recomendada

| Ação recomendada                | Clientes |
| ------------------------------- | -------: |
| `comunicacao_relacionamento`    |  151.500 |
| `lembrete_preventivo_padrao`    |   92.276 |
| `lembrete_suave`                |   58.609 |
| `lembrete_preventivo_reforcado` |   37.193 |
| `revisar_dados_pagamento`       |        9 |

---

## Scripts do Pipeline

Scripts atuais:

```text
scripts/01_origem_para_bronze.py
scripts/02_validar_bronze_arquivos.py
scripts/03_bronze_para_silver_pagamentos.py
scripts/04_validar_silver_pagamentos.py
scripts/05_bronze_para_silver_clientes.py
scripts/06_validar_silver_clientes.py
scripts/07_criar_silver_comportamento_cliente.py
scripts/08_validar_silver_comportamento_cliente.py
scripts/09_criar_gold_indicadores_cliente.py
scripts/10_validar_gold_indicadores_cliente.py
```

---

## Arquivos Principais Gerados

Bronze:

```text
data/bronze/bronze_clientes_cadastro.parquet
data/bronze/bronze_pagamentos_parcelas.parquet
```

Silver:

```text
data/silver/silver_pagamentos_parcelas.parquet
data/silver/silver_clientes_cadastro.parquet
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Gold:

```text
data/gold/gold_indicadores_cliente.parquet
```

---

## Documentação Atualizada

Documentos principais:

```text
docs/01_business_understand.md
docs/02_data_catalog.md
docs/03_data_dictionary.md
docs/04_architecture.md
docs/05_gold_metrics.md
docs/06_ia_agent_design.md
docs/07_business_question_mapping.md
docs/08_pipeline_etapas.md
docs/09_dicionario_gold_indicadores_cliente.md
docs/10_regras_negocio_priorizacao.md
docs/PROJECT_STATUS.md
```

---

## Status Técnico

Validações aprovadas na Gold:

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

## Próximas Etapas

Próximas atividades sugeridas:

1. Atualizar e revisar todos os documentos antigos;
2. Conferir se não restaram termos antigos na documentação;
3. Limpar arquivos antigos locais da pasta Gold;
4. Abrir a Gold oficial no Power BI;
5. Criar visualizações finais;
6. Publicar o projeto no GitHub com README e documentação consistentes;
7. Evoluir futuramente para camada de IA/RAG.
