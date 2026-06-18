from pathlib import Path
import duckdb


# ============================================================
# Script 11 - Criar Gold Base de Lembrete de Vencimento Simulada
# ============================================================
#
# Objetivo:
# Criar uma base simulada de clientes elegíveis para lembrete
# preventivo de vencimento, a partir da Gold de indicadores.
#
# Observação importante:
# O dataset público utilizado no projeto não possui uma base real
# de faturas futuras em aberto como existiria em um banco.
# Por isso, esta etapa simula uma base operacional de vencimentos
# para demonstrar como a solução funcionaria em um cenário real.
#
# Em um banco real, esta simulação seria substituída por uma tabela
# transacional de contas/faturas em aberto.
# ============================================================


ROOT_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_GOLD_INDICADORES = (
    ROOT_DIR / "data" / "gold" / "gold_indicadores_cliente.parquet"
)

ARQUIVO_GOLD_LEMBRETE = (
    ROOT_DIR / "data" / "gold" / "gold_base_lembrete_vencimento_simulada.parquet"
)


def validar_arquivo_entrada() -> None:
    """Valida se a Gold de indicadores existe antes de criar a nova Gold."""
    if not ARQUIVO_GOLD_INDICADORES.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {ARQUIVO_GOLD_INDICADORES}"
        )


def criar_gold_lembrete_vencimento() -> None:
    """Cria a Gold simulada de lembrete de vencimento."""

    validar_arquivo_entrada()

    if ARQUIVO_GOLD_LEMBRETE.exists():
        ARQUIVO_GOLD_LEMBRETE.unlink()

    caminho_entrada = str(ARQUIVO_GOLD_INDICADORES).replace("\\", "/")
    caminho_saida = str(ARQUIVO_GOLD_LEMBRETE).replace("\\", "/")

    con = duckdb.connect()

    query = f"""
    COPY (
        WITH gold AS (
            SELECT
                *
            FROM read_parquet('{caminho_entrada}')
        ),

        base_vencimento AS (
            SELECT
                *,

                CASE
                    WHEN nivel_risco = 'alto_risco'
                        THEN 1 + CAST(hash(id_cliente) % 3 AS INTEGER)

                    WHEN nivel_risco = 'medio_risco'
                        THEN 2 + CAST(hash(id_cliente) % 4 AS INTEGER)

                    WHEN nivel_risco = 'baixo_risco'
                        THEN 3 + CAST(hash(id_cliente) % 5 AS INTEGER)

                    ELSE 2
                END AS dias_para_vencimento

            FROM gold
        ),

        base_enriquecida AS (
            SELECT
                id_cliente,

                'FAT_SIM_' || CAST(id_cliente AS VARCHAR) AS id_fatura_simulada,

                CURRENT_DATE AS data_referencia_simulacao,

                dias_para_vencimento,

                CURRENT_DATE + dias_para_vencimento AS data_vencimento_simulada,

                CASE
                    WHEN dias_para_vencimento <= 1
                        THEN 'vence_em_ate_1_dia'

                    WHEN dias_para_vencimento BETWEEN 2 AND 3
                        THEN 'vence_em_2_a_3_dias'

                    WHEN dias_para_vencimento BETWEEN 4 AND 5
                        THEN 'vence_em_4_a_5_dias'

                    ELSE 'vence_em_6_ou_mais_dias'
                END AS faixa_vencimento,

                ROUND(
                    LEAST(
                        GREATEST(
                            COALESCE(valor_previsto_total / NULLIF(qtd_parcelas_validas, 0), 0),
                            50
                        ),
                        20000
                    ),
                    2
                ) AS valor_fatura_simulada,

                nivel_risco,
                perfil_pagamento,
                prioridade_contato,
                flg_priorizar_contato,
                acao_recomendada,
                grupo_negocio,
                canal_sugerido,
                status_cadastro,
                flg_cliente_com_cadastro,

                taxa_atraso_pct,
                media_dias_atraso,
                maior_atraso_dias,
                qtd_parcelas_total,
                qtd_parcelas_validas,
                qtd_parcelas_atraso,

                faixa_idade,
                faixa_renda,
                genero,
                tipo_renda,
                escolaridade,
                estado_civil,
                tipo_moradia,
                ocupacao,

                CASE
                    WHEN prioridade_contato IN ('prioridade_maxima', 'prioridade_alta')
                        THEN 'alta_urgencia'

                    WHEN prioridade_contato = 'prioridade_media'
                        THEN 'media_urgencia'

                    WHEN prioridade_contato = 'prioridade_revisao'
                        THEN 'revisar_antes_do_envio'

                    ELSE 'baixa_urgencia'
                END AS urgencia_envio,

                CASE
                    WHEN status_cadastro = 'cliente_sem_cadastro'
                        THEN 0

                    WHEN canal_sugerido IN ('canal_nao_identificado', 'cadastro_nao_disponivel')
                        THEN 0

                    WHEN nivel_risco = 'risco_desconhecido'
                        THEN 0

                    WHEN dias_para_vencimento BETWEEN 1 AND 7
                        THEN 1

                    ELSE 0
                END AS flg_elegivel_envio,

                CASE
                    WHEN status_cadastro = 'cliente_sem_cadastro'
                        THEN 'cliente_sem_cadastro'

                    WHEN canal_sugerido IN ('canal_nao_identificado', 'cadastro_nao_disponivel')
                        THEN 'sem_canal_valido'

                    WHEN nivel_risco = 'risco_desconhecido'
                        THEN 'risco_desconhecido_revisar'

                    WHEN dias_para_vencimento BETWEEN 1 AND 7
                        THEN 'elegivel_envio'

                    ELSE 'fora_janela_envio'
                END AS status_elegibilidade_envio,

                CASE
                    WHEN nivel_risco = 'alto_risco'
                        THEN 'Olá! Sua conta vence em breve. Para evitar encargos por atraso, recomendamos consultar as opções de pagamento no app.'

                    WHEN nivel_risco = 'medio_risco'
                        THEN 'Olá! Sua conta está próxima do vencimento. Acesse o app para consultar ou realizar o pagamento.'

                    WHEN nivel_risco = 'baixo_risco' AND perfil_pagamento = 'pagador_antecipado'
                        THEN 'Olá! Passando para lembrar que sua conta vence em breve. Obrigado por manter seus pagamentos em dia.'

                    WHEN nivel_risco = 'baixo_risco'
                        THEN 'Olá! Sua conta vence em breve. Você pode consultar os detalhes pelo app.'

                    ELSE 'Cliente requer revisão dos dados antes de receber comunicação automática.'
                END AS mensagem_sugerida,

                CURRENT_TIMESTAMP AS dt_processamento_gold

            FROM base_vencimento
        )

        SELECT
            *
        FROM base_enriquecida

    ) TO '{caminho_saida}' (FORMAT PARQUET, COMPRESSION ZSTD);
    """

    con.execute(query)

    print("\nGold simulada de lembrete de vencimento criada com sucesso!")
    print(f"Arquivo gerado: {ARQUIVO_GOLD_LEMBRETE}")

    imprimir_validacoes(con, caminho_saida)

    con.close()


def imprimir_validacoes(con: duckdb.DuckDBPyConnection, caminho_saida: str) -> None:
    """Imprime validações simples da Gold simulada."""

    print("\nResumo geral:")
    print(
        con.execute(
            f"""
            SELECT
                COUNT(*) AS total_registros,
                COUNT(DISTINCT id_cliente) AS total_clientes,
                SUM(flg_elegivel_envio) AS clientes_elegiveis_envio,
                SUM(CASE WHEN flg_elegivel_envio = 0 THEN 1 ELSE 0 END) AS clientes_nao_elegiveis_envio,
                ROUND(SUM(valor_fatura_simulada), 2) AS valor_total_faturas_simuladas
            FROM read_parquet('{caminho_saida}')
            """
        ).fetchdf()
    )

    print("\nClientes por nível de risco:")
    print(
        con.execute(
            f"""
            SELECT
                nivel_risco,
                COUNT(*) AS qtd_clientes,
                SUM(flg_elegivel_envio) AS qtd_elegiveis_envio
            FROM read_parquet('{caminho_saida}')
            GROUP BY nivel_risco
            ORDER BY qtd_clientes DESC
            """
        ).fetchdf()
    )

    print("\nClientes por faixa de vencimento:")
    print(
        con.execute(
            f"""
            SELECT
                faixa_vencimento,
                COUNT(*) AS qtd_clientes,
                SUM(flg_elegivel_envio) AS qtd_elegiveis_envio
            FROM read_parquet('{caminho_saida}')
            GROUP BY faixa_vencimento
            ORDER BY faixa_vencimento
            """
        ).fetchdf()
    )

    print("\nClientes por ação recomendada:")
    print(
        con.execute(
            f"""
            SELECT
                acao_recomendada,
                COUNT(*) AS qtd_clientes,
                SUM(flg_elegivel_envio) AS qtd_elegiveis_envio
            FROM read_parquet('{caminho_saida}')
            GROUP BY acao_recomendada
            ORDER BY qtd_clientes DESC
            """
        ).fetchdf()
    )

    print("\nClientes por status de elegibilidade:")
    print(
        con.execute(
            f"""
            SELECT
                status_elegibilidade_envio,
                COUNT(*) AS qtd_clientes
            FROM read_parquet('{caminho_saida}')
            GROUP BY status_elegibilidade_envio
            ORDER BY qtd_clientes DESC
            """
        ).fetchdf()
    )


if __name__ == "__main__":
    criar_gold_lembrete_vencimento()