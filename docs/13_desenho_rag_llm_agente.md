# Desenho Futuro da Solução com RAG, LLM e Agente de IA

## Objetivo

Este documento descreve a evolução futura da solução de priorização de clientes para lembretes de pagamento, considerando a incorporação de RAG, LLM e agente de IA.

A proposta desta etapa não é substituir a lógica já implementada, mas ampliar a capacidade da solução para gerar mensagens mais naturais, justificativas mais contextuais e respostas mais fundamentadas nas regras de negócio.

## Estado Atual da Solução

Na versão atual, o projeto já entrega uma camada inteligente de recomendação operacional baseada em dados estruturados e regras de negócio.

Atualmente, a solução já é capaz de:

- consolidar a entrada da camada inteligente em `gold_ai_input_cliente.parquet`
- gerar a recomendação final em `gold_ai_recomendacoes_cliente.parquet`
- classificar prioridade de clientes
- definir canal sugerido
- definir ação recomendada
- separar clientes prontos para automação de clientes bloqueados
- indicar necessidade de revisão humana

Essa base já é suficiente para apoiar a operação de lembretes de pagamento antes do vencimento.

## Papel do LLM na Evolução da Solução

O LLM entrará como uma camada complementar de geração textual.

Sua função principal será transformar a saída operacional da solução em textos mais naturais, claros e contextualizados para uso em comunicação preventiva.

### Campos que poderão ser gerados pelo LLM

- `mensagem_sugerida_llm`
- `justificativa_llm`

### Exemplos de aplicação

O LLM poderá ser usado para:

- gerar uma mensagem final de lembrete com tom mais natural
- gerar uma justificativa textual para apoio à interpretação da recomendação
- adaptar o texto de acordo com a prioridade e o contexto do cliente
- apoiar futuras interfaces conversacionais ou operacionais

### Importante

A decisão principal da solução continuará ancorada em regras e dados estruturados. O LLM atuará como refinador textual da saída e não como substituto da camada de decisão já implementada.

## Papel do RAG na Evolução da Solução

O RAG será responsável por recuperar documentação relevante para apoiar a geração textual e futuras respostas mais explicáveis.

### Finalidade do RAG

O RAG permitirá que a solução consulte documentos de negócio antes de gerar mensagens ou justificativas, aumentando a rastreabilidade e o alinhamento com as regras da operação.

### Documentos iniciais já estruturados

Na pasta `docs/rag/`, o projeto já possui documentos iniciais para essa futura camada, como:

- `01_politica_comunicacao.md`
- `02_regras_priorizacao.md`
- `03_tratamento_clientes_bloqueados.md`
- `04_tom_mensagem.md`

### O que o RAG poderá recuperar

- regras de bloqueio da automação
- critérios de priorização
- diretrizes de tom da mensagem
- tratamento esperado para clientes sem cadastro
- tratamento esperado para risco desconhecido

### Benefício esperado

Com RAG, a solução poderá gerar mensagens e justificativas mais aderentes à lógica do projeto, reduzindo improviso e aumentando a consistência da resposta.

## Papel do Agente de IA na Evolução da Solução

O agente de IA será a camada futura de orquestração da solução.

Seu papel será consumir a base consolidada, consultar regras e documentos, acionar o LLM quando necessário e entregar uma recomendação mais completa para a operação.

### Funções esperadas do agente

- consumir os dados finais por cliente
- interpretar o status da automação
- consultar documentação via RAG
- gerar mensagem final via LLM
- gerar justificativa textual da recomendação
- apoiar o fluxo ponta a ponta da comunicação preventiva

### Exemplo de fluxo futuro

1. a solução identifica o cliente e sua prioridade operacional
2. o agente lê os dados finais do cliente
3. o RAG recupera documentos relevantes
4. o LLM gera mensagem e justificativa
5. a saída final é disponibilizada para consumo operacional

## Fluxo Evolutivo da Arquitetura

### Etapa já implementada

- dados tratados em Raw, Bronze, Silver e Gold
- base histórica consolidada por cliente
- base operacional de lembretes
- entrada da camada inteligente
- recomendação operacional final

### Etapa futura com RAG, LLM e agente

- recuperação de documentos de negócio
- geração textual com LLM
- orquestração por agente de IA
- recomendação mais explicável e contextualizada

## O que muda e o que não muda

### O que permanece

- a lógica central de priorização
- a separação entre clientes elegíveis e bloqueados
- a estrutura de dados consolidada
- a decisão operacional baseada em regras

### O que evolui

- a forma de gerar mensagem final
- a forma de justificar a recomendação
- a capacidade de consultar documentos do projeto
- a orquestração de todo o fluxo por uma camada de agente

## Conclusão

A solução já possui uma base sólida de dados, analytics e decisão operacional para lembretes de pagamento.

A evolução futura com RAG, LLM e agente de IA não substitui o que já foi construído, mas amplia a capacidade da solução para:

- gerar comunicação mais natural
- responder com maior contexto
- apoiar explicabilidade
- aumentar maturidade operacional

Com isso, o projeto evolui de uma camada inteligente baseada em regras para uma arquitetura preparada para comunicação assistida por IA e consulta de documentação de negócio.
