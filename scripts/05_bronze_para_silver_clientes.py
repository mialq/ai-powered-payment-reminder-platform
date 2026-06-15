"""
Script: 05_bronze_para_silver_clientes.py

Objetivo:
    Criar a camada Silver de clientes a partir da Bronze de cadastro.

Entrada:
    data/bronze/bronze_clientes_cadastro.parquet

Saída:
    data/silver/silver_clientes_cadastro.parquet

Responsabilidade desta etapa:
    - Ler os dados de cadastro de clientes da Bronze.
    - Padronizar nomes de colunas para português, caixa baixa e snake_case.
    - Traduzir valores categóricos principais para português.
    - Criar variáveis úteis para análise de perfil do cliente.
    - Criar flags de qualidade dos dados.
    - Preservar rastreabilidade com arquivo_origem e arquivo_bronze.
"""

from pathlib import Path
import duckdb


# =============================================================================
# 1. CAMINHOS DO PROJETO
# =============================================================================

raiz_projeto = Path(__file__).resolve().parents[1]

caminho_bronze = raiz_projeto / "data" / "bronze"
caminho_silver = raiz_projeto / "data" / "silver"

caminho_silver.mkdir(parents=True, exist_ok=True)

# Arquivo de entrada:
# Cadastro de clientes vindo da camada Bronze.
arquivo_bronze_clientes = caminho_bronze / "bronze_clientes_cadastro.parquet"

# Arquivo oficial de saída:
# Cadastro de clientes tratado na camada Silver.
arquivo_silver_clientes = caminho_silver / "silver_clientes_cadastro.parquet"

# Arquivo temporário:
# Evita sobrescrever a Silver oficial antes da criação terminar com sucesso.
arquivo_silver_clientes_tmp = caminho_silver / "silver_clientes_cadastro_tmp.parquet"


# =============================================================================
# 2. VALIDAÇÕES INICIAIS E LIMPEZA CONTROLADA
# =============================================================================

if not arquivo_bronze_clientes.exists():
    raise FileNotFoundError(f"Arquivo Bronze de clientes não encontrado: {arquivo_bronze_clientes}")

arquivos_para_remover = [
    arquivo_silver_clientes_tmp,

    # Possíveis nomes antigos antes da padronização
    caminho_silver / "silver_application_train.parquet",
    caminho_silver / "silver_clientes.parquet",
]

for arquivo in arquivos_para_remover:
    if arquivo.exists():
        arquivo.unlink()
        print(f"Arquivo removido da Silver: {arquivo}")


# =============================================================================
# 3. CONEXÃO COM DUCKDB
# =============================================================================

con = duckdb.connect()

print("Iniciando transformação Bronze -> Silver de clientes...")


# =============================================================================
# 4. CRIAÇÃO DA SILVER DE CLIENTES
# =============================================================================

# A Bronze mantém os nomes originais do arquivo de origem.
# Nesta etapa, criamos uma versão Silver com nomes em português,
# valores categóricos traduzidos e variáveis de perfil do cliente.
con.execute(f"""
    COPY (
        WITH clientes_tratados AS (
            SELECT
                CAST(SK_ID_CURR AS BIGINT) AS id_cliente,

                CAST(TARGET AS INTEGER) AS flg_inadimplencia_historica,

                CASE
                    WHEN NAME_CONTRACT_TYPE = 'Cash loans' THEN 'emprestimo_dinheiro'
                    WHEN NAME_CONTRACT_TYPE = 'Revolving loans' THEN 'credito_rotativo'
                    ELSE 'nao_informado'
                END AS tipo_contrato,

                CASE
                    WHEN CODE_GENDER = 'F' THEN 'feminino'
                    WHEN CODE_GENDER = 'M' THEN 'masculino'
                    ELSE 'nao_informado'
                END AS genero,

                CASE
                    WHEN FLAG_OWN_CAR = 'Y' THEN 1
                    WHEN FLAG_OWN_CAR = 'N' THEN 0
                    ELSE NULL
                END AS flg_possui_carro,

                CASE
                    WHEN FLAG_OWN_REALTY = 'Y' THEN 1
                    WHEN FLAG_OWN_REALTY = 'N' THEN 0
                    ELSE NULL
                END AS flg_possui_imovel,

                CAST(CNT_CHILDREN AS INTEGER) AS qtd_filhos,

                CAST(AMT_INCOME_TOTAL AS DOUBLE) AS renda_total,
                CAST(AMT_CREDIT AS DOUBLE) AS valor_credito,
                CAST(AMT_ANNUITY AS DOUBLE) AS valor_anuidade,
                CAST(AMT_GOODS_PRICE AS DOUBLE) AS valor_bens,

                CASE
                    WHEN NAME_TYPE_SUITE = 'Unaccompanied' THEN 'sozinho'
                    WHEN NAME_TYPE_SUITE = 'Family' THEN 'familia'
                    WHEN NAME_TYPE_SUITE = 'Spouse, partner' THEN 'conjuge_parceiro'
                    WHEN NAME_TYPE_SUITE = 'Children' THEN 'filhos'
                    WHEN NAME_TYPE_SUITE = 'Other_A' THEN 'outro_a'
                    WHEN NAME_TYPE_SUITE = 'Other_B' THEN 'outro_b'
                    WHEN NAME_TYPE_SUITE = 'Group of people' THEN 'grupo_pessoas'
                    ELSE 'nao_informado'
                END AS tipo_acompanhante,

                CASE
                    WHEN NAME_INCOME_TYPE = 'Working' THEN 'trabalhador'
                    WHEN NAME_INCOME_TYPE = 'Commercial associate' THEN 'associado_comercial'
                    WHEN NAME_INCOME_TYPE = 'Pensioner' THEN 'aposentado_pensionista'
                    WHEN NAME_INCOME_TYPE = 'State servant' THEN 'servidor_publico'
                    WHEN NAME_INCOME_TYPE = 'Unemployed' THEN 'desempregado'
                    WHEN NAME_INCOME_TYPE = 'Student' THEN 'estudante'
                    WHEN NAME_INCOME_TYPE = 'Businessman' THEN 'empresario'
                    WHEN NAME_INCOME_TYPE = 'Maternity leave' THEN 'licenca_maternidade'
                    ELSE 'nao_informado'
                END AS tipo_renda,

                CASE
                    WHEN NAME_EDUCATION_TYPE = 'Secondary / secondary special' THEN 'ensino_medio'
                    WHEN NAME_EDUCATION_TYPE = 'Higher education' THEN 'ensino_superior'
                    WHEN NAME_EDUCATION_TYPE = 'Incomplete higher' THEN 'ensino_superior_incompleto'
                    WHEN NAME_EDUCATION_TYPE = 'Lower secondary' THEN 'ensino_fundamental'
                    WHEN NAME_EDUCATION_TYPE = 'Academic degree' THEN 'pos_graduacao'
                    ELSE 'nao_informado'
                END AS escolaridade,

                CASE
                    WHEN NAME_FAMILY_STATUS = 'Married' THEN 'casado'
                    WHEN NAME_FAMILY_STATUS = 'Single / not married' THEN 'solteiro'
                    WHEN NAME_FAMILY_STATUS = 'Civil marriage' THEN 'uniao_estavel'
                    WHEN NAME_FAMILY_STATUS = 'Separated' THEN 'separado'
                    WHEN NAME_FAMILY_STATUS = 'Widow' THEN 'viuvo'
                    ELSE 'nao_informado'
                END AS estado_civil,

                CASE
                    WHEN NAME_HOUSING_TYPE = 'House / apartment' THEN 'casa_ou_apartamento'
                    WHEN NAME_HOUSING_TYPE = 'With parents' THEN 'mora_com_pais'
                    WHEN NAME_HOUSING_TYPE = 'Municipal apartment' THEN 'apartamento_municipal'
                    WHEN NAME_HOUSING_TYPE = 'Rented apartment' THEN 'apartamento_alugado'
                    WHEN NAME_HOUSING_TYPE = 'Office apartment' THEN 'apartamento_funcional'
                    WHEN NAME_HOUSING_TYPE = 'Co-op apartment' THEN 'apartamento_cooperativa'
                    ELSE 'nao_informado'
                END AS tipo_moradia,

                CAST(REGION_POPULATION_RELATIVE AS DOUBLE) AS populacao_relativa_regiao,

                CAST(ROUND(ABS(DAYS_BIRTH) / 365.25, 0) AS INTEGER) AS idade_anos,

                CASE
                    WHEN DAYS_EMPLOYED IS NULL THEN NULL
                    WHEN CAST(DAYS_EMPLOYED AS BIGINT) = 365243 THEN NULL
                    ELSE CAST(ROUND(ABS(DAYS_EMPLOYED) / 365.25, 2) AS DOUBLE)
                END AS tempo_emprego_anos,

                CASE
                    WHEN OWN_CAR_AGE IS NULL THEN NULL
                    ELSE CAST(OWN_CAR_AGE AS DOUBLE)
                END AS idade_carro_anos,

                CAST(FLAG_MOBIL AS INTEGER) AS flg_possui_celular,
                CAST(FLAG_EMP_PHONE AS INTEGER) AS flg_possui_telefone_emprego,
                CAST(FLAG_WORK_PHONE AS INTEGER) AS flg_possui_telefone_trabalho,
                CAST(FLAG_CONT_MOBILE AS INTEGER) AS flg_celular_contatavel,
                CAST(FLAG_PHONE AS INTEGER) AS flg_possui_telefone,
                CAST(FLAG_EMAIL AS INTEGER) AS flg_possui_email,

                CASE
                    WHEN OCCUPATION_TYPE = 'Laborers' THEN 'trabalhadores_operacionais'
                    WHEN OCCUPATION_TYPE = 'Core staff' THEN 'equipe_administrativa'
                    WHEN OCCUPATION_TYPE = 'Accountants' THEN 'contadores'
                    WHEN OCCUPATION_TYPE = 'Managers' THEN 'gestores'
                    WHEN OCCUPATION_TYPE = 'Drivers' THEN 'motoristas'
                    WHEN OCCUPATION_TYPE = 'Sales staff' THEN 'equipe_vendas'
                    WHEN OCCUPATION_TYPE = 'Cleaning staff' THEN 'equipe_limpeza'
                    WHEN OCCUPATION_TYPE = 'Cooking staff' THEN 'equipe_cozinha'
                    WHEN OCCUPATION_TYPE = 'Private service staff' THEN 'servicos_particulares'
                    WHEN OCCUPATION_TYPE = 'Medicine staff' THEN 'equipe_saude'
                    WHEN OCCUPATION_TYPE = 'Security staff' THEN 'equipe_seguranca'
                    WHEN OCCUPATION_TYPE = 'High skill tech staff' THEN 'equipe_tecnica_qualificada'
                    WHEN OCCUPATION_TYPE = 'Waiters/barmen staff' THEN 'garcons_barmen'
                    WHEN OCCUPATION_TYPE = 'Low-skill Laborers' THEN 'trabalhadores_baixa_qualificacao'
                    WHEN OCCUPATION_TYPE = 'Realty agents' THEN 'corretores_imobiliarios'
                    WHEN OCCUPATION_TYPE = 'Secretaries' THEN 'secretarias'
                    WHEN OCCUPATION_TYPE = 'IT staff' THEN 'equipe_ti'
                    WHEN OCCUPATION_TYPE = 'HR staff' THEN 'equipe_rh'
                    ELSE 'nao_informado'
                END AS ocupacao,

                CAST(CNT_FAM_MEMBERS AS DOUBLE) AS qtd_membros_familia,

                CAST(REGION_RATING_CLIENT AS INTEGER) AS avaliacao_regiao_cliente,
                CAST(REGION_RATING_CLIENT_W_CITY AS INTEGER) AS avaliacao_regiao_cliente_cidade,

                CASE
                    WHEN WEEKDAY_APPR_PROCESS_START = 'MONDAY' THEN 'segunda_feira'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'TUESDAY' THEN 'terca_feira'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'WEDNESDAY' THEN 'quarta_feira'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'THURSDAY' THEN 'quinta_feira'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'FRIDAY' THEN 'sexta_feira'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'SATURDAY' THEN 'sabado'
                    WHEN WEEKDAY_APPR_PROCESS_START = 'SUNDAY' THEN 'domingo'
                    ELSE 'nao_informado'
                END AS dia_semana_solicitacao,

                CAST(HOUR_APPR_PROCESS_START AS INTEGER) AS hora_solicitacao,

                CAST(EXT_SOURCE_1 AS DOUBLE) AS fonte_externa_1,
                CAST(EXT_SOURCE_2 AS DOUBLE) AS fonte_externa_2,
                CAST(EXT_SOURCE_3 AS DOUBLE) AS fonte_externa_3,

                CAST(OBS_30_CNT_SOCIAL_CIRCLE AS DOUBLE) AS qtd_obs_circulo_social_30d,
                CAST(DEF_30_CNT_SOCIAL_CIRCLE AS DOUBLE) AS qtd_def_circulo_social_30d,
                CAST(OBS_60_CNT_SOCIAL_CIRCLE AS DOUBLE) AS qtd_obs_circulo_social_60d,
                CAST(DEF_60_CNT_SOCIAL_CIRCLE AS DOUBLE) AS qtd_def_circulo_social_60d,

                CAST(DAYS_LAST_PHONE_CHANGE AS DOUBLE) AS dias_ultima_alteracao_telefone_ref,

                CAST(AMT_REQ_CREDIT_BUREAU_HOUR AS DOUBLE) AS qtd_consultas_credito_hora,
                CAST(AMT_REQ_CREDIT_BUREAU_DAY AS DOUBLE) AS qtd_consultas_credito_dia,
                CAST(AMT_REQ_CREDIT_BUREAU_WEEK AS DOUBLE) AS qtd_consultas_credito_semana,
                CAST(AMT_REQ_CREDIT_BUREAU_MON AS DOUBLE) AS qtd_consultas_credito_mes,
                CAST(AMT_REQ_CREDIT_BUREAU_QRT AS DOUBLE) AS qtd_consultas_credito_trimestre,
                CAST(AMT_REQ_CREDIT_BUREAU_YEAR AS DOUBLE) AS qtd_consultas_credito_ano,

                'application_train.csv' AS arquivo_origem,
                'bronze_clientes_cadastro.parquet' AS arquivo_bronze

            FROM read_parquet('{arquivo_bronze_clientes.as_posix()}')
        ),

        clientes_com_regras AS (
            SELECT
                *,

                ROUND(valor_credito / NULLIF(renda_total, 0), 2) AS razao_credito_renda,
                ROUND(valor_anuidade / NULLIF(renda_total, 0), 2) AS razao_anuidade_renda,

                CASE WHEN id_cliente IS NULL THEN 1 ELSE 0 END AS flg_id_cliente_nulo,
                CASE WHEN renda_total IS NULL THEN 1 ELSE 0 END AS flg_renda_nula,
                CASE WHEN valor_credito IS NULL THEN 1 ELSE 0 END AS flg_credito_nulo,
                CASE WHEN valor_anuidade IS NULL THEN 1 ELSE 0 END AS flg_anuidade_nula,
                CASE WHEN idade_anos IS NULL THEN 1 ELSE 0 END AS flg_idade_nula,

                CASE
                    WHEN renda_total < 0
                      OR valor_credito < 0
                      OR valor_anuidade < 0
                      OR valor_bens < 0
                    THEN 1
                    ELSE 0
                END AS flg_valor_negativo,

                (
                    CASE WHEN id_cliente IS NULL THEN 1 ELSE 0 END
                  + CASE WHEN renda_total IS NULL THEN 1 ELSE 0 END
                  + CASE WHEN valor_credito IS NULL THEN 1 ELSE 0 END
                  + CASE WHEN valor_anuidade IS NULL THEN 1 ELSE 0 END
                  + CASE WHEN idade_anos IS NULL THEN 1 ELSE 0 END
                ) AS qtd_nulos_criticos

            FROM clientes_tratados
        )

        SELECT
            *,
            CASE WHEN qtd_nulos_criticos > 0 THEN 1 ELSE 0 END AS flg_nulo_critico,
            current_timestamp AS dt_processamento_silver

        FROM clientes_com_regras
    )
    TO '{arquivo_silver_clientes_tmp.as_posix()}'
    (FORMAT PARQUET);
""")


# =============================================================================
# 5. SUBSTITUIÇÃO SEGURA DO ARQUIVO SILVER OFICIAL
# =============================================================================

# A transformação grava primeiro em um arquivo temporário.
# Somente após o processamento terminar com sucesso, o arquivo Silver antigo é removido
# e o arquivo temporário passa a ser o novo arquivo oficial.
if arquivo_silver_clientes.exists():
    arquivo_silver_clientes.unlink()
    print(f"Arquivo Silver anterior removido: {arquivo_silver_clientes}")

arquivo_silver_clientes_tmp.replace(arquivo_silver_clientes)

print(f"Silver de clientes criada com sucesso: {arquivo_silver_clientes}")


# =============================================================================
# 6. VALIDAÇÃO RÁPIDA
# =============================================================================

resumo = con.execute(f"""
    SELECT
        COUNT(*) AS total_registros,
        COUNT(DISTINCT id_cliente) AS total_clientes_distintos,
        COUNT(*) - COUNT(DISTINCT id_cliente) AS registros_duplicados,
        SUM(flg_nulo_critico) AS registros_com_nulo_critico,
        SUM(qtd_nulos_criticos) AS total_campos_criticos_nulos,
        SUM(flg_valor_negativo) AS registros_com_valor_negativo
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
""").df()

print("\nResumo de qualidade da Silver de clientes:")
print(resumo)


resumo_genero = con.execute(f"""
    SELECT
        genero,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
    GROUP BY genero
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por gênero:")
print(resumo_genero)


resumo_tipo_renda = con.execute(f"""
    SELECT
        tipo_renda,
        COUNT(*) AS qtd_clientes
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
    GROUP BY tipo_renda
    ORDER BY qtd_clientes DESC
""").df()

print("\nResumo por tipo de renda:")
print(resumo_tipo_renda)


amostra = con.execute(f"""
    SELECT *
    FROM read_parquet('{arquivo_silver_clientes.as_posix()}')
    LIMIT 10
""").df()

print("\nAmostra da Silver de clientes:")
print(amostra)

print("\nTransformação Bronze -> Silver de clientes concluída com sucesso.")