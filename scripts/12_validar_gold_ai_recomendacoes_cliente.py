from pathlib import Path
import pandas as pd


# =========================================================
# CONFIGURAÇÕES
# =========================================================
PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_GOLD = PASTA_PROJETO / "data" / "gold"

ARQUIVO_RECOMENDACOES = PASTA_GOLD / "gold_ai_recomendacoes_cliente.parquet"
ARQUIVO_RECOMENDACOES_TESTE = PASTA_GOLD / "gold_ai_recomendacoes_cliente_teste.parquet"

print("PASTA_GOLD:", PASTA_GOLD)
print("ARQUIVO_RECOMENDACOES existe?", ARQUIVO_RECOMENDACOES.exists())
print("ARQUIVO_RECOMENDACOES_TESTE existe?", ARQUIVO_RECOMENDACOES_TESTE.exists())


# =========================================================
# LEITURA DOS ARQUIVOS
# =========================================================
df_recomendacoes = pd.read_parquet(ARQUIVO_RECOMENDACOES)
df_recomendacoes_teste = pd.read_parquet(ARQUIVO_RECOMENDACOES_TESTE)

print("\nShape base final:", df_recomendacoes.shape)
print("Shape base final teste:", df_recomendacoes_teste.shape)


# =========================================================
# COLUNAS
# =========================================================
print("\nColunas da base final de recomendações:")
print(df_recomendacoes.columns.tolist())


# =========================================================
# LINHA DE TESTE
# =========================================================
print("\nLinha de teste 999999:")
colunas_teste = [
    "id_cliente",
    "dias_para_vencimento",
    "nivel_risco",
    "grupo_negocio",
    "perfil_historico_pagamento",
    "severidade_historica",
    "bloqueio_automacao",
    "motivo_bloqueio_base",
    "prioridade_base_regra",
    "prioridade_final",
    "canal_sugerido_final",
    "acao_recomendada_ia",
    "status_automacao",
    "necessita_revisao_humana",
    "mensagem_sugerida_ia",
    "justificativa_ia",
]

print(
    df_recomendacoes_teste.loc[
        df_recomendacoes_teste["id_cliente"] == 999999,
        colunas_teste
    ]
)


# =========================================================
# AMOSTRA DE CLIENTES PRONTOS PARA ACIONAMENTO
# =========================================================
print("\nAmostra de clientes prontos para acionamento:")
colunas_amostra = [
    "id_cliente",
    "dias_para_vencimento",
    "nivel_risco",
    "grupo_negocio",
    "prioridade_final",
    "canal_sugerido_final",
    "acao_recomendada_ia",
    "status_automacao",
    "necessita_revisao_humana",
]

print(
    df_recomendacoes.loc[
        df_recomendacoes["status_automacao"] == "pronto_para_acionamento",
        colunas_amostra
    ].head(10)
)


# =========================================================
# AMOSTRA DE CLIENTES BLOQUEADOS
# =========================================================
print("\nAmostra de clientes bloqueados:")
print(
    df_recomendacoes.loc[
        df_recomendacoes["status_automacao"] == "bloqueado",
        [
            "id_cliente",
            "nivel_risco",
            "bloqueio_automacao",
            "motivo_bloqueio_base",
            "necessita_revisao_humana",
            "acao_recomendada_ia",
        ]
    ].head(10)
)


# =========================================================
# RESUMOS DE NEGÓCIO
# =========================================================
print("\nResumo por prioridade final:")
print(df_recomendacoes["prioridade_final"].value_counts(dropna=False))

print("\nResumo por status de automação:")
print(df_recomendacoes["status_automacao"].value_counts(dropna=False))

print("\nResumo por ação recomendada pela IA:")
print(df_recomendacoes["acao_recomendada_ia"].value_counts(dropna=False).head(10))


# =========================================================
# RESUMO FINAL
# =========================================================
print("\nValidação concluída com sucesso.")