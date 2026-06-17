# Regras de Negócio - Risco, Priorização e Ação Recomendada

Este documento descreve as principais regras de negócio utilizadas no projeto **AI-Powered Payment Reminder & Delinquency Prevention Platform**.

As regras foram aplicadas para transformar histórico de pagamentos em indicadores de comportamento, classificação de risco e priorização de contato preventivo.

O objetivo é apoiar a seguinte pergunta de negócio:

> Como identificar clientes com maior risco de atraso e priorizar ações de lembrete preventivo antes do vencimento?

---

## 1. Visão Geral das Regras

As regras de negócio foram aplicadas principalmente em duas etapas do pipeline:

| Etapa | Script                                     | Responsabilidade                                                                |
| ----- | ------------------------------------------ | ------------------------------------------------------------------------------- |
| 07    | `07_criar_silver_comportamento_cliente.py` | Cria perfil de pagamento e nível de risco por cliente                           |
| 09    | `09_criar_gold_indicadores_cliente.py`     | Cria prioridade de contato, ação recomendada, canal sugerido e grupo de negócio |

A Silver de comportamento cria as métricas base por cliente.

A Gold transforma essas métricas em indicadores finais para consumo no Power BI e para tomada de decisão pela área de negócio.

---

## 2. Regra Base de Atraso

A regra principal compara o dia real do pagamento com o dia previsto de vencimento.

```text
dif_dias_vencimento = dias_pagamento_ref - dias_previsto_ref
```

Interpretação:

|                     Resultado | Significado              |
| ----------------------------: | ------------------------ |
|     `dif_dias_vencimento < 0` | Cliente pagou antecipado |
|     `dif_dias_vencimento = 0` | Cliente pagou no prazo   |
|     `dif_dias_vencimento > 0` | Cliente pagou em atraso  |
| `dif_dias_vencimento IS NULL` | Pagamento não registrado |

---

## 3. Status de Pagamento

O campo `status_pagamento` classifica cada parcela/pagamento.

| Condição                         | Status                     |
| -------------------------------- | -------------------------- |
| Data de pagamento não registrada | `sem_pagamento_registrado` |
| `dif_dias_vencimento < 0`        | `pago_antecipado`          |
| `dif_dias_vencimento = 0`        | `pago_no_prazo`            |
| `dif_dias_vencimento > 0`        | `pago_em_atraso`           |

Essa classificação é criada na Silver de pagamentos:

```text
silver_pagamentos_parcelas.parquet
```

---

## 4. Campos Derivados de Atraso e Antecipação

Para evitar distorção nos indicadores, foram criados campos separados para atraso e antecipação.

| Campo                 | Descrição                                                                          |
| --------------------- | ---------------------------------------------------------------------------------- |
| `dias_atraso`         | Quantidade de dias de atraso. Nunca deve ser negativo.                             |
| `dias_antecipacao`    | Quantidade de dias de antecipação. Nunca deve ser negativo.                        |
| `dif_dias_vencimento` | Diferença geral entre pagamento e vencimento. Pode ser negativa, zero ou positiva. |

Exemplo:

| `dif_dias_vencimento` | `dias_atraso` | `dias_antecipacao` | Interpretação          |
| --------------------: | ------------: | -----------------: | ---------------------- |
|                    -5 |             0 |                  5 | Pagou 5 dias antes     |
|                     0 |             0 |                  0 | Pagou no prazo         |
|                    10 |            10 |                  0 | Pagou 10 dias atrasado |

---

## 5. Métricas de Comportamento por Cliente

A Silver de comportamento consolida os pagamentos em nível de cliente.

Arquivo:

```text
data/silver/silver_comportamento_pagamento_cliente.parquet
```

Principais métricas:

| Campo                    | Descrição                                           |
| ------------------------ | --------------------------------------------------- |
| `qtd_parcelas_total`     | Total de parcelas associadas ao cliente             |
| `qtd_parcelas_validas`   | Parcelas com pagamento registrado                   |
| `qtd_parcelas_atraso`    | Parcelas pagas em atraso                            |
| `qtd_pagas_antecipado`   | Parcelas pagas antecipadamente                      |
| `qtd_pagas_no_prazo`     | Parcelas pagas no prazo                             |
| `taxa_atraso_pct`        | Percentual de atraso sobre parcelas válidas         |
| `media_dias_atraso`      | Média de dias de atraso considerando apenas atrasos |
| `maior_atraso_dias`      | Maior atraso histórico do cliente                   |
| `maior_antecipacao_dias` | Maior antecipação histórica do cliente              |

---

## 6. Regra de Perfil de Pagamento

O campo `perfil_pagamento` descreve o comportamento histórico do cliente.

| Condição                                                  | Perfil                       |
| --------------------------------------------------------- | ---------------------------- |
| Cliente sem parcelas válidas                              | `comportamento_desconhecido` |
| Sem atrasos e mais pagamentos antecipados do que no prazo | `pagador_antecipado`         |
| Sem atrasos                                               | `pagador_no_prazo`           |
| Taxa de atraso menor que 10%                              | `baixo_atraso`               |
| Taxa de atraso maior ou igual a 10% e menor que 30%       | `atraso_moderado`            |
| Taxa de atraso maior ou igual a 30%                       | `alto_atraso`                |

---

## 7. Regra de Nível de Risco

O campo `nivel_risco` classifica o cliente em grupos de risco.

| Condição                                                                                                                  | Nível de risco       |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Cliente sem parcelas válidas                                                                                              | `risco_desconhecido` |
| Taxa de atraso maior ou igual a 30% ou maior atraso maior ou igual a 30 dias                                              | `alto_risco`         |
| Taxa de atraso maior ou igual a 10%, ou média de atraso maior ou igual a 5 dias, ou maior atraso maior ou igual a 10 dias | `medio_risco`        |
| Demais casos                                                                                                              | `baixo_risco`        |

Essa regra considera tanto frequência quanto severidade do atraso.

Ou seja:

* cliente com muitos atrasos vira risco maior;
* cliente com poucos atrasos, mas com atraso muito alto, também pode virar risco maior;
* cliente sem histórico suficiente vira `risco_desconhecido`.

---

## 8. Regra de Priorização de Contato

Na Gold, o campo `prioridade_contato` define a urgência da comunicação preventiva.

| Condição                                               | Prioridade           |
| ------------------------------------------------------ | -------------------- |
| `nivel_risco = alto_risco` e `maior_atraso_dias >= 30` | `prioridade_maxima`  |
| `nivel_risco = alto_risco`                             | `prioridade_alta`    |
| `nivel_risco = medio_risco`                            | `prioridade_media`   |
| `nivel_risco = risco_desconhecido`                     | `prioridade_revisao` |
| Demais casos                                           | `prioridade_baixa`   |

---

## 9. Regra da Flag de Priorização

O campo `flg_priorizar_contato` indica se o cliente deve entrar em uma ação prioritária.

| Condição                                                             | Valor |
| -------------------------------------------------------------------- | ----: |
| `nivel_risco IN ('alto_risco', 'medio_risco', 'risco_desconhecido')` |     1 |
| `nivel_risco = baixo_risco`                                          |     0 |

Interpretação:

| Valor | Significado                        |
| ----: | ---------------------------------- |
|     1 | Cliente deve ser priorizado        |
|     0 | Cliente pode ser apenas monitorado |

---

## 10. Regra de Ação Recomendada

O campo `acao_recomendada` traduz o risco em uma sugestão de ação para o negócio.

| Condição                                                              | Ação recomendada                |
| --------------------------------------------------------------------- | ------------------------------- |
| `nivel_risco = alto_risco`                                            | `lembrete_preventivo_reforcado` |
| `nivel_risco = medio_risco`                                           | `lembrete_preventivo_padrao`    |
| `nivel_risco = baixo_risco` e `perfil_pagamento = pagador_antecipado` | `comunicacao_relacionamento`    |
| `nivel_risco = baixo_risco`                                           | `lembrete_suave`                |
| `nivel_risco = risco_desconhecido`                                    | `revisar_dados_pagamento`       |

---

## 11. Regra de Grupo de Negócio

O campo `grupo_negocio` facilita filtros e visualizações no Power BI.

| Condição                                       | Grupo                    |
| ---------------------------------------------- | ------------------------ |
| `nivel_risco IN ('alto_risco', 'medio_risco')` | `clientes_prioritarios`  |
| `nivel_risco = risco_desconhecido`             | `clientes_para_revisao`  |
| Demais casos                                   | `clientes_monitoramento` |

---

## 12. Regra de Valor Priorizado

O campo `valor_previsto_total_priorizado` representa o valor previsto associado aos clientes priorizados.

| Condição                                       | Valor                         |
| ---------------------------------------------- | ----------------------------- |
| `nivel_risco IN ('alto_risco', 'medio_risco')` | recebe `valor_previsto_total` |
| Demais casos                                   | recebe 0                      |

Esse campo permite calcular no Power BI o valor histórico associado à carteira priorizada.

---

## 13. Regra de Cobertura Cadastral

A Gold mantém todos os clientes com histórico de pagamento, mesmo quando não existe cadastro disponível.

A regra utiliza `LEFT JOIN` entre:

```text
silver_comportamento_pagamento_cliente
+
silver_clientes_cadastro
```

Campos criados:

| Campo                      | Regra                                                      |
| -------------------------- | ---------------------------------------------------------- |
| `flg_cliente_com_cadastro` | 1 quando o cliente existe no cadastro; 0 quando não existe |
| `status_cadastro`          | `cliente_com_cadastro` ou `cliente_sem_cadastro`           |

Essa decisão evita perda de clientes com histórico de pagamento.

---

## 14. Regra de Canal Sugerido

O campo `canal_sugerido` indica o melhor canal disponível para contato, com base no cadastro.

| Condição                       | Canal sugerido            |
| ------------------------------ | ------------------------- |
| Cliente sem cadastro           | `cadastro_nao_disponivel` |
| Cliente com e-mail             | `email`                   |
| Cliente com celular contatável | `celular`                 |
| Cliente com celular informado  | `celular`                 |
| Cliente com telefone informado | `telefone`                |
| Nenhum canal identificado      | `canal_nao_identificado`  |

---

## 15. Resultado Final das Regras

A aplicação das regras gerou a seguinte distribuição na Gold:

| Nível de risco       | Clientes |
| -------------------- | -------: |
| `baixo_risco`        |  210.109 |
| `medio_risco`        |   92.276 |
| `alto_risco`         |   37.193 |
| `risco_desconhecido` |        9 |

Clientes priorizados:

```text
129.478
```

Distribuição por prioridade:

| Prioridade           | Clientes |
| -------------------- | -------: |
| `prioridade_baixa`   |  210.109 |
| `prioridade_media`   |   92.276 |
| `prioridade_maxima`  |   23.707 |
| `prioridade_alta`    |   13.486 |
| `prioridade_revisao` |        9 |

---

## 16. Interpretação para a Área de Negócio

A classificação não deve ser lida como uma previsão estatística definitiva de inadimplência.

Ela deve ser interpretada como uma segmentação analítica baseada no histórico de comportamento de pagamento.

Exemplo de leitura:

| Cliente              | Interpretação                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| `baixo_risco`        | Cliente com bom comportamento histórico. Pode receber lembrete leve ou comunicação de relacionamento. |
| `medio_risco`        | Cliente com sinais de atraso. Deve receber lembrete preventivo padrão.                                |
| `alto_risco`         | Cliente com atraso frequente ou severo. Deve receber comunicação preventiva reforçada.                |
| `risco_desconhecido` | Cliente com dados insuficientes. Deve ser revisado antes de uma ação automatizada.                    |

---

## 17. Validação das Regras

As regras foram validadas pelo script:

```text
scripts/10_validar_gold_indicadores_cliente.py
```

Principais validações aprovadas:

```text
0 valores categóricos inválidos
0 flags fora do padrão
0 inconsistências de regras de negócio
0 inconsistências numéricas
0 duplicidade de clientes
0 diferença de volume entre Silver comportamento e Gold
```

---

## 18. Uso no Power BI

Campos recomendados para análise das regras:

| Objetivo              | Campos                                                     |
| --------------------- | ---------------------------------------------------------- |
| Medir risco           | `nivel_risco`, `taxa_atraso_pct`, `maior_atraso_dias`      |
| Priorizar clientes    | `prioridade_contato`, `flg_priorizar_contato`              |
| Definir ação          | `acao_recomendada`, `grupo_negocio`                        |
| Avaliar contato       | `canal_sugerido`, `status_cadastro`                        |
| Medir valor associado | `valor_previsto_total_priorizado`                          |
| Segmentar clientes    | `faixa_idade`, `faixa_renda`, `tipo_renda`, `escolaridade` |

---

## 19. Limitações e Cuidados

As regras foram criadas com base no histórico disponível no dataset.

Pontos de atenção:

* As datas do dataset são referências relativas, não datas reais de calendário.
* A classificação de risco é baseada em regras de negócio, não em modelo preditivo supervisionado.
* Clientes sem cadastro foram mantidos na Gold para preservar histórico de pagamento.
* A renda possui valores extremos; análises financeiras devem considerar faixas, mediana ou percentis.
* Antes de automatizar envio de mensagens, seria necessário validar regras com negócio, jurídico, privacidade e canais de comunicação.

---

## 20. Próximas Evoluções

Possíveis melhorias futuras:

* Criar modelo preditivo de atraso;
* Criar score de risco ponderado;
* Ajustar pesos por recência do atraso;
* Considerar valor da parcela e proximidade do vencimento;
* Criar estratégia de mensagem por canal;
* Integrar a Gold com dashboard no Power BI;
* Usar RAG para explicar as regras e apoiar perguntas de negócio.
