# Pipeline de Dados - Etapas do Projeto

Este documento descreve as etapas do pipeline de dados do projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

O objetivo do pipeline é transformar dados brutos de pagamentos e cadastro de clientes em uma camada analítica final, pronta para consumo no Power BI e para uso futuro por um agente de IA/RAG.

---

## Visão Geral do Pipeline

O pipeline segue a arquitetura medalhão:

```text
raw
↓
bronze
↓
silver
↓
gold
```

Cada camada tem uma responsabilidade específica:

| Camada | Responsabilidade                                                   |
| ------ | ------------------------------------------------------------------ |
| Raw    | Armazenar os arquivos originais                                    |
| Bronze | Converter os dados para Parquet, preservando a estrutura da origem |
| Silver | Tratar, padronizar, enriquecer e validar os dados                  |
| Gold   | Criar indicadores finais para consumo analítico                    |

---

## Estrutura Final das Camadas

### Raw

Arquivos originais:

```text
application_train.csv
installments_payments.csv
```

### Bronze

Arquivos gerados:

```text
bronze_clientes_cadastro.parquet
bronze_pagamentos_parcelas.parquet
```

### Silver

Arquivos gerados:

```text
silver_pagamentos_parcelas.parquet
silver_clientes_cadastro.parquet
silver_comportamento_pagamento_cliente.parquet
```

### Gold

Arquivo final:

```text
gold_indicadores_cliente.parquet
```

---

## Etapa 01 - Origem para Bronze

Script:

```text
scripts/01_origem_para_bronze.py
```

Objetivo:

Converter os arquivos CSV da camada Raw para arquivos Parquet na camada Bronze.

Entradas:

```text
data/raw/application_train.csv
data/raw/installments_payments.csv
```

Saídas:

```text
data/bronze/bronze_clientes_cadastro.parquet
data/bronze/bronze_pagamentos_parcelas.parquet
```

Responsabilidades:

* Ler os arquivos CSV originais;
* Converter para Parquet;
* Padronizar os nomes físicos dos arquivos;
* Manter a estrutura original dos dados;
* Preservar rastreabilidade com a origem.

Observação:

A Bronze não aplica regras de negócio profundas. Ela mantém os dados próximos da origem para permitir auditoria e comparação com os arquivos originais.

---

## Etapa 02 - Validação da Bronze

Script:

```text
scripts/02_validar_bronze_arquivos.py
```

Objetivo:

Validar se os arquivos da camada Bronze foram criados corretamente.

Arquivos validados:

```text
data/bronze/bronze_clientes_cadastro.parquet
data/bronze/bronze_pagamentos_parcelas.parquet
```

Validações realizadas:

* Existência dos arquivos;
* Total de registros;
* Schema das tabelas;
* Amostra dos dados.

---

## Etapa 03 - Bronze para Silver de Pagamentos

Script:

```text
scripts/03_bronze_para_silver_pagamentos.py
```

Objetivo:

Criar a Silver de pagamentos a partir da Bronze de pagamentos por parcela.

Entrada:

```text
data/bronze/bronze_pagamentos_parcelas.parquet
```

Saída:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

Responsabilidades:

* Renomear colunas para português, caixa baixa e snake_case;
* Criar diferenças entre data prevista e data de pagamento;
* Identificar pagamentos antecipados, no prazo, atrasados e sem pagamento registrado;
* Criar flags de atraso, antecipação e pagamento no prazo;
* Criar indicadores de qualidade dos dados;
* Identificar nulos críticos;
* Criar metadados de rastreabilidade.

Principais campos criados:

```text
dif_dias_vencimento
dias_atraso
dias_antecipacao
status_pagamento
status_valor_pagamento
flg_pagamento_atrasado
flg_pagamento_antecipado
flg_pagamento_no_prazo
flg_nulo_critico
qtd_nulos_criticos
```

Regra principal:

```text
dif_dias_vencimento = dias_pagamento_ref - dias_previsto_ref
```

Interpretação:

|   Resultado | Significado          |
| ----------: | -------------------- |
| menor que 0 | pagamento antecipado |
|   igual a 0 | pagamento no prazo   |
| maior que 0 | pagamento em atraso  |

---

## Etapa 04 - Validação da Silver de Pagamentos

Script:

```text
scripts/04_validar_silver_pagamentos.py
```

Objetivo:

Validar a Silver de pagamentos.

Arquivo validado:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

Validações realizadas:

* Existência do arquivo;
* Total de registros;
* Colunas esperadas;
* Colunas extras;
* Padrão de nomes em caixa baixa e snake_case;
* Status de pagamento;
* Status de valor de pagamento;
* Nulos críticos;
* Regras de atraso e antecipação;
* Valores categóricos em caixa baixa;
* Validação financeira.

Resultado validado:

```text
13.605.401 registros
0 inconsistências de atraso
0 inconsistências de antecipação
0 inconsistências de prazo
0 valores financeiros negativos
```

---

## Etapa 05 - Bronze para Silver de Clientes

Script:

```text
scripts/05_bronze_para_silver_clientes.py
```

Objetivo:

Criar a Silver de clientes a partir da Bronze de cadastro.

Entrada:

```text
data/bronze/bronze_clientes_cadastro.parquet
```

Saída:

```text
data/silver/silver_clientes_cadastro.parquet
```

Responsabilidades:

* Renomear colunas para português, caixa baixa e snake_case;
* Traduzir campos categóricos;
* Criar variáveis de perfil do cliente;
* Criar flags de qualidade;
* Criar razões financeiras;
* Preservar metadados de origem.

Principais campos criados:

```text
id_cliente
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
razao_credito_renda
razao_anuidade_renda
flg_nulo_critico
qtd_nulos_criticos
```

---

## Etapa 06 - Validação da Silver de Clientes

Script:

```text
scripts/06_validar_silver_clientes.py
```

Objetivo:

Validar a Silver de clientes.

Arquivo validado:

```text
data/silver/silver_clientes_cadastro.parquet
```

Validações realizadas:

* Existência do arquivo;
* Total de registros;
* Total de clientes distintos;
* Duplicidade de clientes;
* Colunas esperadas;
* Padrão de nomes;
* Campos categóricos;
* Flags binárias;
* Qualidade dos dados;
* Validação financeira e cadastral;
* Metadados de origem.

Resultado validado:

```text
307.511 registros
307.511 clientes distintos
0 registros duplicados
0 valores financeiros negativos
```

Ponto de atenção tratado por flags:

```text
12 registros com nulo crítico
12 nulos em valor_anuidade
```

---

## Etapa 07 - Silver de Comportamento de Pagamento por Cliente

Script:

```text
scripts/07_criar_silver_comportamento_cliente.py
```

Objetivo:

Consolidar o histórico de pagamentos em nível de cliente.

Entrada:

```text
data/silver/silver_pagamentos_parcelas.parquet
```

Saída:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Responsabilidades:

* Agregar pagamentos por cliente;
* Calcular total de parcelas;
* Calcular parcelas válidas;
* Calcular quantidade de atrasos;
* Calcular taxa de atraso;
* Calcular média e maior atraso;
* Calcular valores totais previstos e pagos;
* Criar perfil de pagamento;
* Criar nível de risco.

Principais campos criados:

```text
qtd_parcelas_total
qtd_parcelas_validas
qtd_parcelas_atraso
taxa_atraso_pct
media_dias_atraso
maior_atraso_dias
perfil_pagamento
nivel_risco
```

---

## Etapa 08 - Validação da Silver de Comportamento

Script:

```text
scripts/08_validar_silver_comportamento_cliente.py
```

Objetivo:

Validar a Silver de comportamento de pagamento por cliente.

Arquivo validado:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Validações realizadas:

* Existência do arquivo;
* Total de clientes;
* Duplicidade;
* Colunas esperadas;
* Padrão de nomes;
* Valores categóricos permitidos;
* Regras numéricas;
* Resumo financeiro;
* Cobertura com a Silver de clientes;
* Data de processamento.

Resultado validado:

```text
339.587 clientes
339.587 clientes distintos
0 duplicados
0 valores categóricos inválidos
0 inconsistências numéricas
```

Cobertura com cadastro:

```text
clientes_com_cadastro: 291.643
clientes_sem_cadastro: 47.944
pct_clientes_com_cadastro: 85,88%
```

---

## Etapa 09 - Criação da Gold de Indicadores por Cliente

Script:

```text
scripts/09_criar_gold_indicadores_cliente.py
```

Objetivo:

Criar a Gold final de indicadores por cliente para consumo no Power BI.

Entradas:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
data/silver/silver_clientes_cadastro.parquet
```

Saída:

```text
data/gold/gold_indicadores_cliente.parquet
```

Responsabilidades:

* Juntar comportamento de pagamento com cadastro de clientes;
* Manter todos os clientes com histórico de pagamento;
* Sinalizar clientes sem cadastro;
* Criar prioridade de contato;
* Criar ação recomendada;
* Criar canal sugerido;
* Criar grupo de negócio;
* Criar valor previsto total priorizado.

Decisão de modelagem:

A Gold parte da Silver de comportamento de pagamento e faz `LEFT JOIN` com a Silver de clientes. Essa decisão evita perder clientes que possuem histórico de pagamento, mas não aparecem no cadastro.

Campos principais:

```text
id_cliente
nivel_risco
perfil_pagamento
taxa_atraso_pct
maior_atraso_dias
flg_cliente_com_cadastro
status_cadastro
faixa_idade
faixa_renda
canal_sugerido
prioridade_contato
flg_priorizar_contato
acao_recomendada
grupo_negocio
valor_previsto_total_priorizado
```

---

## Etapa 10 - Validação da Gold

Script:

```text
scripts/10_validar_gold_indicadores_cliente.py
```

Objetivo:

Validar a Gold final de indicadores por cliente.

Arquivo validado:

```text
data/gold/gold_indicadores_cliente.parquet
```

Validações realizadas:

* Existência do arquivo;
* Total de clientes;
* Duplicidade;
* Colunas esperadas;
* Padrão de nomes;
* Valores categóricos permitidos;
* Campos categóricos em caixa baixa;
* Flags binárias;
* Regras de negócio;
* Validações numéricas;
* Cobertura cadastral;
* Comparação de volume com a Silver de comportamento;
* Data de processamento.

Resultado validado:

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

## Resultado Final do Pipeline

A Gold final contém uma linha por cliente com histórico de pagamento.

Resumo final:

```text
total_clientes: 339.587
clientes_com_cadastro: 291.643
clientes_sem_cadastro: 47.944
pct_clientes_com_cadastro: 85,88%
clientes_priorizados: 129.478
```

Distribuição por nível de risco:

| Nível de risco     | Clientes |
| ------------------ | -------: |
| baixo_risco        |  210.109 |
| medio_risco        |   92.276 |
| alto_risco         |   37.193 |
| risco_desconhecido |        9 |

Distribuição por prioridade de contato:

| Prioridade         | Clientes |
| ------------------ | -------: |
| prioridade_baixa   |  210.109 |
| prioridade_media   |   92.276 |
| prioridade_maxima  |   23.707 |
| prioridade_alta    |   13.486 |
| prioridade_revisao |        9 |

---

## Como executar o pipeline

Executar os scripts em ordem:

```bash
python scripts/01_origem_para_bronze.py
python scripts/02_validar_bronze_arquivos.py
python scripts/03_bronze_para_silver_pagamentos.py
python scripts/04_validar_silver_pagamentos.py
python scripts/05_bronze_para_silver_clientes.py
python scripts/06_validar_silver_clientes.py
python scripts/07_criar_silver_comportamento_cliente.py
python scripts/08_validar_silver_comportamento_cliente.py
python scripts/09_criar_gold_indicadores_cliente.py
python scripts/10_validar_gold_indicadores_cliente.py
```

---

## Arquivo Final para Consumo

O arquivo final para consumo analítico é:

```text
data/gold/gold_indicadores_cliente.parquet
```

Esse arquivo será utilizado no Power BI para construção do dashboard de risco, prioridade de contato e recomendação de ação preventiva.
