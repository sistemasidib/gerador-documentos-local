import pandas as pd

# Carregar os arquivos
df1 = pd.read_excel("floriano.xlsx")
df2 = pd.read_excel("concursos/FLORIANO TODOS/ensalamento.xlsx")

# Garantir que as colunas necessárias existem
required_cols = {"INSC", "ESCOLA", "EDITAL", "SALA"}
if not required_cols.issubset(df1.columns) or not required_cols.issubset(df2.columns):
    raise ValueError("Ambos os arquivos precisam ter as colunas INSC, ESCOLA, EDITAL e SALA.")

# Juntar os dois dataframes pela coluna INSC
merged = df1.merge(df2, on="INSC", how="inner", suffixes=("_A", "_B"))

# Filtrar diferenças de escola
diferencas = merged[merged["ESCOLA_A"] != merged["ESCOLA_B"]]

# Selecionar somente as colunas desejadas
diferencas = diferencas[[
    "INSC",
    "EDITAL_A",
    "ESCOLA_A",
    "ESCOLA_B",
    "SALA_A",
    "SALA_B",
    "TURNO_A",
    "DIA_A",
]]

print("Total de diferenças encontradas:", len(diferencas))
print(diferencas)

# Salvar o resultado
output_path = "diferencas_escolas.xlsx"
diferencas.to_excel(output_path, index=False)

print(f"\nArquivo salvo em: {output_path}")
