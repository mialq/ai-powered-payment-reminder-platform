# Regras de Priorização

## Objetivo

Definir como a solução classifica clientes para ações de lembrete de pagamento com base em prazo para vencimento, risco de atraso, histórico de pagamento e elegibilidade operacional.

## Critérios Principais

A priorização deve considerar a combinação de:

- dias para vencimento
- nível de risco
- severidade histórica
- percentual de atraso
- existência de valores em aberto
- quantidade de não pagos
- bloqueio ou elegibilidade para automação

## Regras de Prioridade

### Prioridade Alta

Aplicável quando:

- o vencimento está muito próximo
- e o cliente apresenta risco alto
- ou histórico severo de atraso
- ou combinação de vencimento próximo com alta criticidade histórica

### Prioridade Média-Alta

Aplicável quando:

- o cliente está próximo do vencimento
- e apresenta risco médio ou alto
- ou possui histórico relevante de atraso, ainda que sem bloqueio operacional

### Prioridade Média

Aplicável quando:

- o cliente é elegível para envio
- e possui vencimento próximo, mas com criticidade intermediária
- ou quando o caso exige contato preventivo, sem indício de severidade elevada

### Prioridade Baixa

Aplicável quando:

- o cliente é elegível para envio
- possui menor urgência operacional
- e não apresenta combinação forte de risco e histórico problemático

### Prioridade Bloqueada

Aplicável quando:

- a automação está bloqueada por regra
- o cliente exige revisão humana
- o cadastro está incompleto
- ou o risco não está identificado

## Observação Operacional

A prioridade pode ser refinada em futuras evoluções para considerar escalonamento após o vencimento, reincidência de atraso e resposta a comunicações anteriores.
