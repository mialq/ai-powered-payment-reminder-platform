# Tratamento de Clientes Bloqueados

## Objetivo

Definir o tratamento operacional para clientes que não podem seguir para automação de lembretes de pagamento.

## Quando um Cliente Deve Ser Considerado Bloqueado

Um cliente deve ser classificado como bloqueado quando houver impedimento para envio automático, como:

- ausência de cadastro válido
- risco desconhecido
- não elegibilidade para envio
- necessidade de revisão manual

## Regras por Motivo de Bloqueio

### Cliente sem Cadastro

Quando o cliente não possui dados mínimos para contato:

- bloquear a automação
- não gerar mensagem automática
- direcionar o caso para revisão cadastral

### Risco Desconhecido

Quando o cliente não possui classificação confiável de risco:

- bloquear a automação
- não gerar mensagem automática
- encaminhar o caso para revisão da regra ou da classificação de risco

### Cliente Não Elegível para Envio

Quando existe alguma regra operacional que impede o envio:

- bloquear a automação
- não seguir para comunicação automática
- direcionar para avaliação manual

## Diretriz Geral

Casos bloqueados não devem ser tratados como clientes prontos para acionamento. A solução deve sinalizar claramente que esses registros exigem intervenção humana antes de qualquer contato.

## Resultado Esperado

A camada inteligente deve separar clientes prontos para automação de clientes bloqueados, garantindo mais segurança operacional e evitando comunicações inadequadas.
