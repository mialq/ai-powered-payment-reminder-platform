from pathlib import Path
import pandas as pd

pasta_projeto = Path.cwd()
pasta_gold = pasta_projeto / "data" / "gold"

arquivo_ai_input = pasta_gold / "gold_ai_input_cliente.parquet"
arquivo_ai_input_teste = pasta_gold / "gold_ai_input_cliente_teste.parquet"

df_ai_input = pd.read_parquet(arquivo_ai_input)
df_ai_input_teste = pd.read_parquet(arquivo_ai_input_teste)

print("Shape base AI input:", df_ai_input.shape)
print("Shape base AI input teste:", df_ai_input_teste.shape)

print("\nColunas da base AI input:")
print(df_ai_input.columns.tolist())

print("\nPrimeiras 5 linhas:")
print(df_ai_input.head())

print("\nLinha de teste:")
print(df_ai_input_teste[df_ai_input_teste["id_cliente"] == 999999])