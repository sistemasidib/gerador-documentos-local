import dataclasses
import json
import pandas as pd

from models import Cargo, Candidato, Edital, Ensalamento, Escola, Sala, BdFormatado
from models.bdFormatado import DiaBD
from utils.utils import normalizar_cpf, safe_filename


def _normalizar_nome_coluna(coluna: str) -> str:
    coluna = str(coluna)
    # Remove BOM e espacos nao separaveis que costumam vir de planilhas.
    coluna = coluna.replace("\ufeff", "").replace("\xa0", " ")
    return coluna.strip().upper()


def formatar_bd(df: pd.DataFrame) -> BdFormatado:
    df.columns = [_normalizar_nome_coluna(coluna) for coluna in df.columns]
    # df.fillna('', inplace=True)

    if "ID_EDITAL" not in df.columns:
        raise ValueError(
            "Coluna obrigatoria 'ID_EDITAL' nao encontrada. "
            f"Colunas detectadas: {list(df.columns)}"
        )

    if "ID_CARGO" in df.columns and "CARGO" in df.columns:
        id_cargo = df["ID_CARGO"].astype(str).str.strip()
        id_vazio = (
            df["ID_CARGO"].isna()
            | id_cargo.eq("")
            | id_cargo.str.lower().isin(["nan", "none"])
        )
        if id_vazio.any():
            df["ID_CARGO"] = df["ID_CARGO"].astype(object)
            df.loc[id_vazio, "ID_CARGO"] = (
                df.loc[id_vazio, "CARGO"].astype(str).str.strip().str[:9]
            )

    db = BdFormatado(
        edital=Edital(
            df['ID_EDITAL'].iloc[0],
            df['EDITAL'].iloc[0]  
        ),
        sabado=DiaBD(
            manha=[],
            tarde=[]
        ),
        domingo=DiaBD(
            manha=[],
            tarde=[]
        )
    )

    # criar cargos
    cargos = {}
    cargos_group = df.groupby('ID_CARGO')
    for id_cargo, cargo_df in cargos_group:
        cargo = Cargo(
            id=id_cargo,
            nome=cargo_df['CARGO'].iloc[0],
            turno=cargo_df['TURNO'].iloc[0],
            dia=cargo_df['DIA'].iloc[0],
            hora_prova=cargo_df['HORA_PROVA'].iloc[0],
            data_prova=cargo_df['DATA_PROVA'].iloc[0],
            escolaridade=cargo_df['ESCOLARIDADE'].iloc[0],
            qtd_questoes_prova=cargo_df['QTD_QUESTOES_PROVA'].iloc[0],
            peca=cargo_df['PECA'].iloc[0],
            qtd_questoes_discursiva=cargo_df['QTD_QUESTOES_DISCURSIVA'].iloc[0],
            qtd_linhas_discursiva=cargo_df['QTD_LINHAS_DISCURSIVA'].iloc[0],
            redacao=cargo_df['REDACAO'].iloc[0],
            edital=Edital(
                cargo_df['ID_EDITAL'].iloc[0],
                cargo_df['EDITAL'].iloc[0]
            ),
        )
        cargos[id_cargo] = cargo

    # print(cargos)

    envelope = 1
    
    escolas = df.groupby(['TAG_ESCOLA','ID_ESCOLA', "TURNO", "DIA"])

    for (tag_escola,id_escola, turno, dia), escola_df in escolas:
        escola = Escola(
            id=id_escola,
            tag=tag_escola,
            nome=safe_filename(escola_df['ESCOLA'].iloc[0]),
            cidade=escola_df['LOCAL_PROVA'].iloc[0],  # Changed from 'CIDADE' to 'LOCAL_PROVA'
            uf=escola_df['UF'].iloc[0], 
            salas=[]
        )
        
        # criando as salas
        salas = escola_df.groupby('ID_SALA')

        for id_sala, sala_df in salas:
            sala = Sala(
                id=id_sala,
                bloco=sala_df['BLOCO'].iloc[0],
                andar=sala_df['ANDAR'].iloc[0],
                sala=sala_df['SALA'].iloc[0],
                envelope=sala_df['ENVELOPE'].iloc[0],
                ensalados=[]
            )
            envelope += 1

            for _, row in sala_df.iterrows():
                candidato = Candidato(
                    row['INSC'],
                    row['NOME'],
                    row['RG'],
                    normalizar_cpf(row['CPF']),
                    row['TIPO'],
                    row['SOLICITACAO'],    
                    cargos[row['ID_CARGO']]               
                )
                sala.ensalados.append(
                    Ensalamento(
                        candidato=candidato,
                        ordem_geral=row['ORDEM_GERAL'],
                        carteira=row['CART'],
                        turno=row['TURNO'],
                        dia=row['DIA'],
                        data_prova=row['DATA_PROVA'],
                    )
                )

            escola.salas.append(sala)

        if dia.lower() == "domingo":
            if turno.lower() == "tarde":
                db.domingo.tarde.append(escola)
            else:
                db.domingo.manha.append(escola)
        else:
            if turno.lower() == "tarde":
                db.sabado.tarde.append(escola)
            else:
                db.sabado.manha.append(escola)
        
    projeto_dict = dataclasses.asdict(db)
    # projeto_json = json.dumps(projeto_dict, indent=4, default=str, ensure_ascii=False)
    # print(projeto_json)

    return db


# df = pd.read_csv('DB_SECULT_FORMATADO.csv')
# df.columns = df.columns.str.strip()
# df.fillna('', inplace=True)
# # df_limpo = df.dropna(how='all')

# formatar_bd(df)