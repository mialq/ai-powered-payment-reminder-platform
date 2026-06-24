from pathlib import Path
import pandas as pd
import numpy as np

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ADICIONAR_LINHA_TESTE = True

PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_GOLD = PASTA_PROJETO / "data" / "gold"

ARQUIVO_BASE_ATUAL = PASTA_GOLD / "gold_base_lembrete_vencimento_simulada.parquet"
ARQUIVO_BASE_HISTORICA = PASTA_GOLD / "gold_indicadores_cliente.parquet"

ARQUIVO_SAIDA_AI_INPUT = PASTA_GOLD / "gold_ai_input_cliente.parquet"
ARQUIVO_SAIDA_AI_INPUT_TESTE = PASTA_GOLD / "gold_ai_input_cliente_teste.parquet"

print("PASTA_PROJETO:", PASTA_PROJETO)
print("PASTA_GOLD:", PASTA_GOLD)
print("ARQUIVO_BASE_ATUAL:", ARQUIVO_BASE_ATUAL)
print("ARQUIVO_BASE_HISTORICA:", ARQUIVO_BASE_HISTORICA)
print("PASTA_GOLD existe?", PASTA_GOLD.exists())
print("BASE ATUAL existe?", ARQUIVO_BASE_ATUAL.exists())
print("BASE HISTÓRICA existe?", ARQUIVO_BASE_HISTORICA.exists())

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def selecionar_primeira_coluna_existente(df: pd.DataFrame, nomes_possiveis: list[str], novo_nome: str) -> pd.DataFrame:
    """
    Cria ou padroniza uma coluna usando a primeira coluna existente da lista.
    """
    for coluna in nomes_possiveis:
        if coluna in df.columns:
            if coluna != novo_nome:
                df[novo_nome] = df[coluna]
            return df

    if novo_nome not in df.columns:
        df[novo_nome] = np.nan

    return df


def normalizar_percentual(serie: pd.Series) -> pd.Series:
    """
    Se o percentual vier em fração (ex.: 0.33), transforma para 33.
    Se já vier como 33, mantém.
    """
    serie_numerica = pd.to_numeric(serie, errors="coerce")
    maior_valor = serie_numerica.dropna().max()

    if pd.notna(maior_valor) and maior_valor <= 1.5:
        serie_numerica = serie_numerica * 100

    return serie_numerica


def interpretar_booleano(valor) -> bool:
    """
    Interpreta vários formatos como verdadeiro ou falso.
    """
    if pd.isna(valor):
        return False

    if isinstance(valor, bool):
        return valor

    if isinstance(valor, (int, float)):
        return valor == 1

    valor_texto = str(valor).strip().lower()
    return valor_texto in {"1", "true", "sim", "s", "yes", "y", "elegivel_envio"}


def classificar_perfil_historico_pagamento(linha: pd.Series) -> str:
    percentual_atraso = linha.get("pct_atraso", np.nan)
    atraso_medio_dias = linha.get("atraso_medio_dias", np.nan)
    maior_atraso_dias = linha.get("maior_atraso_dias", np.nan)
    quantidade_nao_pagos = linha.get("qtd_nao_pagos", np.nan)
    valor_em_aberto = linha.get("valor_em_aberto", np.nan)

    percentual_atraso = 0 if pd.isna(percentual_atraso) else percentual_atraso
    atraso_medio_dias = 0 if pd.isna(atraso_medio_dias) else atraso_medio_dias
    maior_atraso_dias = 0 if pd.isna(maior_atraso_dias) else maior_atraso_dias
    quantidade_nao_pagos = 0 if pd.isna(quantidade_nao_pagos) else quantidade_nao_pagos
    valor_em_aberto = 0 if pd.isna(valor_em_aberto) else valor_em_aberto

    if quantidade_nao_pagos > 0 or valor_em_aberto > 0:
        return "inadimplencia_relevante"

    if percentual_atraso >= 30 or atraso_medio_dias > 5 or maior_atraso_dias >= 15:
        return "atrasante_recorrente"

    if percentual_atraso >= 10:
        return "pagador_irregular"

    return "bom_pagador"


def classificar_severidade_historica(perfil_historico_pagamento: str) -> str:
    mapa_severidade = {
        "bom_pagador": "baixa",
        "pagador_irregular": "media",
        "atrasante_recorrente": "alta",
        "inadimplencia_relevante": "alta",
    }
    return mapa_severidade.get(perfil_historico_pagamento, "media")


def definir_bloqueio_automacao(linha: pd.Series) -> tuple[str, str]:
    cliente_com_cadastro = interpretar_booleano(linha.get("flg_cliente_com_cadastro"))
    elegivel_envio = interpretar_booleano(linha.get("flg_elegivel_envio"))
    nivel_risco = str(linha.get("nivel_risco", "")).strip().lower()

    if not cliente_com_cadastro:
        return "sim", "cliente_sem_cadastro"

    if nivel_risco == "risco_desconhecido":
        return "sim", "risco_desconhecido"

    if not elegivel_envio:
        return "sim", "nao_elegivel_envio"

    return "nao", "nao_aplicavel"


def definir_prioridade_base_regra(linha: pd.Series) -> str:
    if linha.get("bloqueio_automacao") == "sim":
        return "bloqueada"

    dias_para_vencimento = linha.get("dias_para_vencimento", np.nan)
    dias_para_vencimento = 999 if pd.isna(dias_para_vencimento) else dias_para_vencimento

    nivel_risco = str(linha.get("nivel_risco", "")).strip().lower()
    severidade_historica = str(linha.get("severidade_historica", "")).strip().lower()
    priorizar_contato = interpretar_booleano(linha.get("flg_priorizar_contato"))

    if (dias_para_vencimento <= 1 and nivel_risco == "alto_risco") or (
        dias_para_vencimento <= 1 and severidade_historica == "alta"
    ):
        return "alta"

    if (dias_para_vencimento <= 3 and nivel_risco in {"alto_risco", "medio_risco"}) or (
        dias_para_vencimento <= 3 and severidade_historica == "alta"
    ):
        return "media_alta"

    if dias_para_vencimento <= 5 or priorizar_contato:
        return "media"

    return "baixa"


def criar_linha_teste(colunas_finais: list[str]) -> pd.DataFrame:
    """
    Cria uma linha fictícia para testar a base de entrada da IA.
    """
    linha = {
        "id_cliente": 999999,
        "id_fatura_simulada": "FATURA_TESTE_999999",
        "dias_para_vencimento": 2,
        "faixa_vencimento": "vence_em_2_a_3_dias",
        "valor_fatura_simulada": 480.00,
        "nivel_risco": "medio_risco",
        "grupo_negocio": "clientes_prioritarios",
        "acao_recomendada": "lembrete_preventivo_padrao",
        "mensagem_sugerida": "Olá! Sua conta está próxima do vencimento. Acesse o app para consultar ou realizar o pagamento.",
        "canal_sugerido": "whatsapp",
        "flg_cliente_com_cadastro": 1,
        "flg_elegivel_envio": 1,
        "flg_priorizar_contato": 1,
        "qtd_parcelas": 12,
        "qtd_em_dia": 7,
        "qtd_atrasadas": 4,
        "qtd_antecipadas": 1,
        "pct_em_dia": 58.33,
        "pct_atraso": 33.33,
        "pct_antecipacao": 8.33,
        "valor_total_pago": 5200.00,
        "valor_total_previsto": 5600.00,
        "atraso_medio_dias": 6,
        "maior_atraso_dias": 18,
        "qtd_nao_pagos": 1,
        "valor_em_aberto": 400.00,
        "perfil_historico_pagamento": "inadimplencia_relevante",
        "severidade_historica": "alta",
        "bloqueio_automacao": "nao",
        "motivo_bloqueio_base": "nao_aplicavel",
        "prioridade_base_regra": "media_alta",
    }

    df_linha_teste = pd.DataFrame([linha])

    for coluna in colunas_finais:
        if coluna not in df_linha_teste.columns:
            df_linha_teste[coluna] = np.nan

    return df_linha_teste[colunas_finais]


# =========================================================
# 1. LEITURA DAS BASES
# =========================================================
print("Lendo arquivos parquet...")
df_base_atual = pd.read_parquet(ARQUIVO_BASE_ATUAL)
df_base_historica = pd.read_parquet(ARQUIVO_BASE_HISTORICA)

print(f"Base atual: {df_base_atual.shape}")
print(f"Base histórica: {df_base_historica.shape}")


# =========================================================
# 2. PADRONIZAÇÃO DAS COLUNAS
# =========================================================
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["id_cliente"], "id_cliente")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["id_fatura_simulada"], "id_fatura_simulada")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["dias_para_vencimento"], "dias_para_vencimento")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["faixa_vencimento"], "faixa_vencimento")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["valor_fatura_simulada"], "valor_fatura_simulada")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["nivel_risco"], "nivel_risco")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["grupo_negocio"], "grupo_negocio")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["acao_recomendada"], "acao_recomendada")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["mensagem_sugerida"], "mensagem_sugerida")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["canal_sugerido"], "canal_sugerido")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["flg_cliente_com_cadastro"], "flg_cliente_com_cadastro")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["flg_elegivel_envio"], "flg_elegivel_envio")
df_base_atual = selecionar_primeira_coluna_existente(df_base_atual, ["flg_priorizar_contato"], "flg_priorizar_contato")

df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["id_cliente"], "id_cliente")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["qtd_parcelas"], "qtd_parcelas")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["qtd_em_dia"], "qtd_em_dia")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["qtd_atrasadas"], "qtd_atrasadas")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["qtd_antecipadas"], "qtd_antecipadas")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["pct_em_dia"], "pct_em_dia")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["pct_atraso"], "pct_atraso")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["pct_antecipacao"], "pct_antecipacao")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["valor_total_pago"], "valor_total_pago")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["valor_total_previsto"], "valor_total_previsto")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["atraso_medio_dias", "media_dias_atraso"], "atraso_medio_dias")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["maior_atraso_dias"], "maior_atraso_dias")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["qtd_nao_pagos"], "qtd_nao_pagos")
df_base_historica = selecionar_primeira_coluna_existente(df_base_historica, ["valor_em_aberto"], "valor_em_aberto")


# =========================================================
# 3. NORMALIZAÇÃO DE PERCENTUAIS
# =========================================================
for coluna_percentual in ["pct_em_dia", "pct_atraso", "pct_antecipacao"]:
    if coluna_percentual in df_base_historica.columns:
        df_base_historica[coluna_percentual] = normalizar_percentual(df_base_historica[coluna_percentual])


# =========================================================
# 4. GARANTIR 1 LINHA POR CLIENTE
# =========================================================
quantidade_duplicados_base_atual = df_base_atual["id_cliente"].duplicated().sum()
quantidade_duplicados_base_historica = df_base_historica["id_cliente"].duplicated().sum()

print(f"Duplicados por id_cliente na base atual: {quantidade_duplicados_base_atual}")
print(f"Duplicados por id_cliente na base histórica: {quantidade_duplicados_base_historica}")

if quantidade_duplicados_base_atual > 0:
    df_base_atual = df_base_atual.drop_duplicates(subset=["id_cliente"], keep="first")

if quantidade_duplicados_base_historica > 0:
    df_base_historica = df_base_historica.drop_duplicates(subset=["id_cliente"], keep="first")


# =========================================================
# 5. JOIN DAS DUAS TABELAS
# =========================================================
print("Realizando join por id_cliente...")
df_ai_input = df_base_atual.merge(
    df_base_historica,
    on="id_cliente",
    how="left",
    suffixes=("", "_historico")
)

print(f"Base consolidada: {df_ai_input.shape}")


# =========================================================
# 6. CRIAÇÃO DAS COLUNAS DERIVADAS
# =========================================================
print("Criando colunas derivadas...")

df_ai_input["perfil_historico_pagamento"] = df_ai_input.apply(classificar_perfil_historico_pagamento, axis=1)
df_ai_input["severidade_historica"] = df_ai_input["perfil_historico_pagamento"].apply(classificar_severidade_historica)

resultado_bloqueio = df_ai_input.apply(definir_bloqueio_automacao, axis=1)
df_ai_input["bloqueio_automacao"] = [resultado[0] for resultado in resultado_bloqueio]
df_ai_input["motivo_bloqueio_base"] = [resultado[1] for resultado in resultado_bloqueio]

df_ai_input["prioridade_base_regra"] = df_ai_input.apply(definir_prioridade_base_regra, axis=1)


# =========================================================
# 7. SELEÇÃO E ORDEM DAS COLUNAS FINAIS
# =========================================================
colunas_finais = [
    "id_cliente",
    "id_fatura_simulada",
    "dias_para_vencimento",
    "faixa_vencimento",
    "valor_fatura_simulada",
    "nivel_risco",
    "grupo_negocio",
    "acao_recomendada",
    "mensagem_sugerida",
    "canal_sugerido",
    "flg_cliente_com_cadastro",
    "flg_elegivel_envio",
    "flg_priorizar_contato",
    "qtd_parcelas",
    "qtd_em_dia",
    "qtd_atrasadas",
    "qtd_antecipadas",
    "pct_em_dia",
    "pct_atraso",
    "pct_antecipacao",
    "valor_total_pago",
    "valor_total_previsto",
    "atraso_medio_dias",
    "maior_atraso_dias",
    "qtd_nao_pagos",
    "valor_em_aberto",
    "perfil_historico_pagamento",
    "severidade_historica",
    "bloqueio_automacao",
    "motivo_bloqueio_base",
    "prioridade_base_regra",
]

colunas_existentes = [coluna for coluna in colunas_finais if coluna in df_ai_input.columns]
df_ai_input_final = df_ai_input[colunas_existentes].copy()


# =========================================================
# 8. SALVAR ARQUIVO FINAL
# =========================================================
ARQUIVO_SAIDA_AI_INPUT.parent.mkdir(parents=True, exist_ok=True)

df_ai_input_final.to_parquet(ARQUIVO_SAIDA_AI_INPUT, index=False)
print(f"Arquivo salvo com sucesso: {ARQUIVO_SAIDA_AI_INPUT}")


# =========================================================
# 9. GERAR VERSÃO COM LINHA DE TESTE
# =========================================================
if ADICIONAR_LINHA_TESTE:
    print("Gerando arquivo de teste com 1 linha simulada...")

    df_linha_teste = criar_linha_teste(df_ai_input_final.columns.tolist())
    df_ai_input_teste = pd.concat([df_ai_input_final, df_linha_teste], ignore_index=True)

    df_ai_input_teste.to_parquet(ARQUIVO_SAIDA_AI_INPUT_TESTE, index=False)
    print(f"Arquivo de teste salvo com sucesso: {ARQUIVO_SAIDA_AI_INPUT_TESTE}")


# =========================================================
# 10. RESUMO FINAL
# =========================================================
print("\nResumo:")
print(f"- Registros finais da base AI input: {len(df_ai_input_final):,}".replace(",", "."))
if ADICIONAR_LINHA_TESTE:
    print(f"- Registros no arquivo de teste: {len(df_ai_input_teste):,}".replace(",", "."))
print("- Processo concluído com sucesso.")