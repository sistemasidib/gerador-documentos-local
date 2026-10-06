import base64
import pandas as pd

from ler_documento import ler_bd_xls

df = ler_bd_xls("DISCURSIVAS_FALT.xlsx",False)

def base64_to_inscricao(b64_str):
    try:
        decoded = base64.b64decode(b64_str).decode("utf-8")
        return int(decoded)
    except:
        return None

df["INSC"] = df["COD"].apply(lambda x: base64_to_inscricao((x.strip())))
df.to_excel("DISCURSIVAS_FALT_INSC.xlsx", index=False)
