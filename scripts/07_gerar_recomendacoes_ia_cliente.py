from pathlib import Path
import pandas as pd
import numpy as np


# =========================================================
# CONFIGURAÇÕES
# =========================================================
GERAR_VERSAO_TESTE = True

PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_GOLD = PASTA_PROJETO / "data" / "gold"

ARQUIVO_AI_INPUT = PASTA_GOLD / "gold_ai_input_cliente.parquet"
ARQUIVO_AI_INPUT_TESTE = PASTA_GOLD / "gold_ai_input_cliente_teste.parquet"

ARQUIVO_SAIDA_RECOMENDACOES = PASTA_GOLD / "gold_ai_recomendacoes_cliente.parquet"
ARQUIVO_SAIDA_RECOMENDACOES_TESTE = PASTA_GOLD / "gold_ai_recomendacoes_cliente_teste.parquet"

print("PASTA_GOLD:", PASTA_GOLD)
print("ARQUIVO_AI_INPUT existe?", ARQUIVO_AI_INPUT.exists())
print("ARQUIVO_AI_INPUT_TESTE existe?", ARQUIVO_AI_INPUT_TESTE.exists())


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def texto_limpo(valor) -> str:
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def definir_status_automacao(linha: pd.Series) -> str:
    bloqueio = texto_limpo(linha.get("bloqueio_automacao")).lower()

    if bloqueio == "sim":
        return "bloqueado"

    return "pronto_para_acionamento"


def definir_revisao_humana(linha: pd.Series) -> str:
    bloqueio = texto_limpo(linha.get("bloqueio_automacao")).lower()
    motivo = texto_limpo(linha.get("motivo_bloqueio_base")).lower()

    if bloqueio == "sim":
        return "sim"

    if motivo in {"cliente_sem_cadastro", "risco_desconhecido", "nao_elegivel_envio"}:
        return "sim"

    return "nao"


def definir_canal_sugerido_final(linha: pd.Series) -> str:
    status_automacao = texto_limpo(linha.get("status_automacao")).lower()
    prioridade = texto_limpo(linha.get("prioridade_final")).lower()
    canal_base = texto_limpo(linha.get("canal_sugerido")).lower()

    if status_automacao == "bloqueado":
        return "sem_envio"

    if canal_base:
        return canal_base

    if prioridade == "alta":
        return "whatsapp"

    if prioridade == "media_alta":
        return "whatsapp"

    if prioridade == "media":
        return "sms"

    return "app"


def definir_acao_recomendada_ia(linha: pd.Series) -> str:
    status_automacao = texto_limpo(linha.get("status_automacao")).lower()
    prioridade = texto_limpo(linha.get("prioridade_final")).lower()
    motivo = texto_limpo(linha.get("motivo_bloqueio_base")).lower()
    acao_base = texto_limpo(linha.get("acao_recomendada")).lower()

    if status_automacao == "bloqueado":
        if motivo == "cliente_sem_cadastro":
            return "revisao_cadastral"
        if motivo == "risco_desconhecido":
            return "revisao_regra_risco"
        if motivo == "nao_elegivel_envio":
            return "avaliacao_manual"
        return "revisao_manual"

    if prioridade == "alta":
        return "lembrete_reforcado"

    if prioridade == "media_alta":
        return "lembrete_preventivo"

    if prioridade == "media":
        return "lembrete_suave"

    if "relaci" in acao_base:
        return "contato_relacional"

    return "lembrete_suave"


def definir_prioridade_final(linha: pd.Series) -> str:
    prioridade_base = texto_limpo(linha.get("prioridade_base_regra")).lower()
    severidade = texto_limpo(linha.get("severidade_historica")).lower()
    percentual_atraso = linha.get("pct_atraso", np.nan)
    dias_para_vencimento = linha.get("dias_para_vencimento", np.nan)
    quantidade_nao_pagos = linha.get("qtd_nao_pagos", np.nan)

    percentual_atraso = 0 if pd.isna(percentual_atraso) else percentual_atraso
    dias_para_vencimento = 999 if pd.isna(dias_para_vencimento) else dias_para_vencimento
    quantidade_nao_pagos = 0 if pd.isna(quantidade_nao_pagos) else quantidade_nao_pagos

    if prioridade_base == "bloqueada":
        return "bloqueada"

    if prioridade_base == "alta":
        return "alta"

    if prioridade_base == "media_alta":
        return "media_alta"

    # refinamento adicional da recomendação
    if dias_para_vencimento <= 2 and severidade == "alta":
        return "media_alta"

    if percentual_atraso >= 40 or quantidade_nao_pagos > 0:
        return "media_alta"

    if prioridade_base == "media":
        return "media"

    return "baixa"


def gerar_mensagem_sugerida_ia(linha: pd.Series) -> str:
    status_automacao = texto_limpo(linha.get("status_automacao")).lower()
    motivo = texto_limpo(linha.get("motivo_bloqueio_base")).lower()
    prioridade = texto_limpo(linha.get("prioridade_final")).lower()
    canal = texto_limpo(linha.get("canal_sugerido_final")).lower()
    dias = linha.get("dias_para_vencimento", np.nan)

    dias_texto = "em breve" if pd.isna(dias) else f"em {int(dias)} dia(s)"

    if status_automacao == "bloqueado":
        if motivo == "cliente_sem_cadastro":
            return "Cliente sem cadastro válido para contato automático. Encaminhar para revisão cadastral."
        if motivo == "risco_desconhecido":
            return "Cliente com risco não identificado. Encaminhar para revisão antes de qualquer comunicação automática."
        if motivo == "nao_elegivel_envio":
            return "Cliente não elegível para envio automático. Avaliar tratamento manual."
        return "Cliente bloqueado para automação. Avaliar tratamento manual."

    if prioridade == "alta":
        return (
            f"Olá! Identificamos um pagamento com vencimento {dias_texto}. "
            f"Recomendamos regularização o quanto antes. Canal sugerido: {canal}."
        )

    if prioridade == "media_alta":
        return (
            f"Olá! Sua conta vence {dias_texto}. "
            f"Acesse nossos canais para consultar ou realizar o pagamento. Canal sugerido: {canal}."
        )

    if prioridade == "media":
        return (
            f"Olá! Passando para lembrar que há um pagamento próximo do vencimento {dias_texto}. "
            f"Se possível, consulte as opções disponíveis no app."
        )

    return (
        f"Olá! Este é um lembrete preventivo sobre um pagamento com vencimento {dias_texto}. "
        f"Consulte os detalhes no app."
    )


def gerar_justificativa_ia(linha: pd.Series) -> str:
    status_automacao = texto_limpo(linha.get("status_automacao")).lower()
    motivo = texto_limpo(linha.get("motivo_bloqueio_base")).lower()
    prioridade = texto_limpo(linha.get("prioridade_final")).lower()
    nivel_risco = texto_limpo(linha.get("nivel_risco")).replace("_", " ")
    grupo_negocio = texto_limpo(linha.get("grupo_negocio")).replace("_", " ")
    perfil_historico = texto_limpo(linha.get("perfil_historico_pagamento")).replace("_", " ")
    dias = linha.get("dias_para_vencimento", np.nan)
    percentual_atraso = linha.get("pct_atraso", np.nan)
    valor_em_aberto = linha.get("valor_em_aberto", np.nan)

    dias_txt = "não informado" if pd.isna(dias) else f"{int(dias)} dia(s)"
    atraso_txt = "não informado" if pd.isna(percentual_atraso) else f"{round(float(percentual_atraso), 2)}%"
    aberto_txt = "não informado" if pd.isna(valor_em_aberto) else f"R$ {round(float(valor_em_aberto), 2):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if status_automacao == "bloqueado":
        return (
            f"Cliente bloqueado para automação devido ao motivo '{motivo}'. "
            f"Necessita revisão humana antes de qualquer ação."
        )

    return (
        f"Cliente classificado com prioridade '{prioridade}' por combinar prazo de vencimento de {dias_txt}, "
        f"nível de risco '{nivel_risco}', grupo de negócio '{grupo_negocio}' e histórico '{perfil_historico}'. "
        f"Percentual de atraso histórico: {atraso_txt}. Valor em aberto: {aberto_txt}."
    )


def gerar_recomendacoes(df_entrada: pd.DataFrame) -> pd.DataFrame:
    df_saida = df_entrada.copy()

    df_saida["status_automacao"] = df_saida.apply(definir_status_automacao, axis=1)
    df_saida["necessita_revisao_humana"] = df_saida.apply(definir_revisao_humana, axis=1)
    df_saida["prioridade_final"] = df_saida.apply(definir_prioridade_final, axis=1)
    df_saida["canal_sugerido_final"] = df_saida.apply(definir_canal_sugerido_final, axis=1)
    df_saida["acao_recomendada_ia"] = df_saida.apply(definir_acao_recomendada_ia, axis=1)
    df_saida["mensagem_sugerida_ia"] = df_saida.apply(gerar_mensagem_sugerida_ia, axis=1)
    df_saida["justificativa_ia"] = df_saida.apply(gerar_justificativa_ia, axis=1)

    colunas_finais = [
        "id_cliente",
        "id_fatura_simulada",
        "dias_para_vencimento",
        "faixa_vencimento",
        "valor_fatura_simulada",
        "nivel_risco",
        "grupo_negocio",
        "perfil_historico_pagamento",
        "severidade_historica",
        "pct_atraso",
        "qtd_nao_pagos",
        "valor_em_aberto",
        "bloqueio_automacao",
        "motivo_bloqueio_base",
        "prioridade_base_regra",
        "status_automacao",
        "necessita_revisao_humana",
        "prioridade_final",
        "canal_sugerido_final",
        "acao_recomendada_ia",
        "mensagem_sugerida_ia",
        "justificativa_ia",
    ]

    colunas_existentes = [coluna for coluna in colunas_finais if coluna in df_saida.columns]
    return df_saida[colunas_existentes].copy()


# =========================================================
# 1. LEITURA DA BASE DE ENTRADA DA IA
# =========================================================
print("Lendo base de entrada da IA...")
df_ai_input = pd.read_parquet(ARQUIVO_AI_INPUT)
print(f"Base principal lida com sucesso: {df_ai_input.shape}")

if GERAR_VERSAO_TESTE and ARQUIVO_AI_INPUT_TESTE.exists():
    df_ai_input_teste = pd.read_parquet(ARQUIVO_AI_INPUT_TESTE)
    print(f"Base de teste lida com sucesso: {df_ai_input_teste.shape}")
else:
    df_ai_input_teste = None


# =========================================================
# 2. GERAÇÃO DAS RECOMENDAÇÕES
# =========================================================
print("Gerando recomendações da IA para a base principal...")
df_recomendacoes = gerar_recomendacoes(df_ai_input)

if df_ai_input_teste is not None:
    print("Gerando recomendações da IA para a base de teste...")
    df_recomendacoes_teste = gerar_recomendacoes(df_ai_input_teste)
else:
    df_recomendacoes_teste = None


# =========================================================
# 3. SALVAR ARQUIVOS
# =========================================================
df_recomendacoes.to_parquet(ARQUIVO_SAIDA_RECOMENDACOES, index=False)
print(f"Arquivo salvo com sucesso: {ARQUIVO_SAIDA_RECOMENDACOES}")

if df_recomendacoes_teste is not None:
    df_recomendacoes_teste.to_parquet(ARQUIVO_SAIDA_RECOMENDACOES_TESTE, index=False)
    print(f"Arquivo de teste salvo com sucesso: {ARQUIVO_SAIDA_RECOMENDACOES_TESTE}")


# =========================================================
# 4. RESUMO E VALIDAÇÃO DA LINHA DE TESTE
# =========================================================
print("\nResumo:")
print(f"- Registros da base final de recomendações: {len(df_recomendacoes):,}".replace(",", "."))

if df_recomendacoes_teste is not None:
    print(f"- Registros da base final de recomendações teste: {len(df_recomendacoes_teste):,}".replace(",", "."))

    linha_teste = df_recomendacoes_teste[df_recomendacoes_teste["id_cliente"] == 999999]

    print("\nLinha de teste processada:")
    print(
        linha_teste[
            [
                "id_cliente",
                "prioridade_final",
                "canal_sugerido_final",
                "acao_recomendada_ia",
                "status_automacao",
                "necessita_revisao_humana",
                "mensagem_sugerida_ia",
            ]
        ]
    )

print("\nProcesso concluído com sucesso.")