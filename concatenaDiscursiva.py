import base64
import pandas as pd

from ler_documento import ler_bd_xls
from utils.criptografia import mascarar_numero

excel = "FALTA"


df = ler_bd_xls( f"{excel}.xlsx",sheet_name="falta")

df["COD"] = df["INSCRIÇÃO"].apply(mascarar_numero)
df.to_excel(f"{excel}_INSC.xlsx", index=False)
