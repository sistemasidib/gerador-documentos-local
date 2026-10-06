import os
import pandas as pd
import re

from utils.utils import normalizar_cpf

def ler_bd(name: str) -> pd.DataFrame:
    df = pd.read_csv(name, encoding='utf-8', sep=',')
    df_limpo = df.dropna(how='all')
    return df_limpo

import pandas as pd

def ler_bd_xls(name: str, uppercase: bool = True) -> pd.DataFrame:
    # Determina o engine conforme a extensão
    if name.endswith('.xlsx'):
        engine = 'openpyxl'
    elif name.endswith('.xls'):
        engine = 'xlrd'
    else:
        raise ValueError("Unsupported file format. Use .xls or .xlsx.")

    try:
        df = pd.read_excel(name, engine=engine).fillna("")
    except Exception as e:
        if "BOF record" in str(e) or "html" in str(e):
            print("File is not a valid Excel format; attempting to read as HTML.")
            try:
                df_list = pd.read_html(name)
                df = df_list[0]
            except Exception as e_html:
                raise ValueError(f"Could not read the file as either Excel or HTML. Error: {e_html}") from e_html
        else:
            raise e

    df_limpo = df.dropna(how='all')

    if uppercase:
        # Colunas para maiúsculas
        df_limpo.columns = [str(col).upper() for col in df_limpo.columns]
        # Usa map diretamente para converter strings nas células
        df_limpo = df_limpo.map(lambda x: x.upper() if isinstance(x, str) else x)

    return df_limpo

def exportar_info_escolas(df: pd.DataFrame, output_file: str):
    # Agrupar por escola e contar informações
    escolas_info = df.groupby(['ESCOLA', 'LOCAL_PROVA', 'UF', 'DATA_PROVA', 'TURNO', 'DIA','ENDERECO']).agg({
        'ID_SALA': 'nunique',  # Conta o número único de salas por escola
        'INSC': 'count'        # Conta o número de candidatos (inscrições) por escola
    }).reset_index()
    
    # Renomear as colunas
    escolas_info.columns = ['ESCOLA', 'LOCAL DE PROVA', 'UF', 'DATA', 'TURNO', 'DIA', 'ENDERECO','QTDE. SALAS', 'QTDE. CANDIDATOS']
    
    # Reordenar as colunas
    escolas_info = escolas_info[['DATA', 'DIA', 'TURNO', 'QTDE. SALAS', 'QTDE. CANDIDATOS', 'ESCOLA', 'LOCAL DE PROVA' ,'UF', 'ENDERECO']]

    escolas_info = escolas_info.sort_values(['DIA','TURNO'])
    
    # Exportar para Excel
    escolas_info.to_excel(output_file, index=False)
    print(f"Arquivo exportado com sucesso: {output_file}")

def exportar_candidatos_especiais(df: pd.DataFrame, output_file: str):
    """
    Exporta candidatos que possuem informação nos campos TIPO ou SOLICITACAO 
    """
    colunas_disponiveis = df.columns.tolist()
    
    condicao_filtro = pd.Series(False, index=df.index)

    if 'TIPO' in colunas_disponiveis:
        condicao_filtro = condicao_filtro | (df['TIPO'].notna() & (df['TIPO'] != ''))
    
    if 'RESPOSTA' in colunas_disponiveis:
        condicao_filtro = condicao_filtro | (df['RESPOSTA'].notna() & (df['RESPOSTA'] != ''))

    candidatos_especiais = df[condicao_filtro]
    
    candidatos_especiais.to_excel(output_file, index=False)
    print(f"Arquivo exportado com sucesso: {output_file}")

from datetime import datetime, timedelta

import pandas as pd
import re
from datetime import datetime

def exportar_info_vini(df: pd.DataFrame, output_dir: str):
    # Seleciona as colunas de interesse e as renomeia
    df = df.rename(columns={
        'INSC': 'INSCRICAO',
        'NOME': 'NOME',
        'CPF': 'CPF',
        'DIA': 'DIA_PROVA',
        'DATA_PROVA': 'DIA',
        'EDITAL': 'CONCURSO',
        'CARGO': 'CARGO',
        'LOCAL_PROVA': 'LOCAL_PROVA',
        'ESCOLA': 'ESCOLA',
        'ANDAR': 'ANDAR',
        'BLOCO': 'BLOCO',
        'SALA': 'SALA',
        # 'RUA': 'RUA',
        # 'BAIRRO': 'BAIRRO',
        # 'CEP': 'CEP',
        'TURNO': 'TURNO'
    })

    # df[['RUA', 'BAIRRO', 'CEP']] = df['ENDERECO'].str.split(',', n=2, expand=True).fillna('')

    df['CPF'] = df['CPF'].apply(normalizar_cpf)
    
    # Formatação da coluna DIA
    df['DIA'] = pd.to_datetime(df['DIA'], dayfirst=True).dt.strftime('%Y-%m-%d')

    # Lógica para adicionar e formatar as colunas de horário
    def definir_horarios_e_provas(row):

        abertura = '00:00:00'
        fechamento = '00:00:00'
        hora_prova = '00:00:00'
            
        return pd.Series([abertura, fechamento, hora_prova])

    # Aplica a função para criar as novas colunas
    df[['HORÁRIO DE ABERTURA DOS PORTÕES', 'HORÁRIO DE FECHAMENTO DOS PORTÕES', 'HORÁRIO DAS PROVAS']] = df.apply(definir_horarios_e_provas, axis=1)
    
    # Concatena as colunas de endereço
    # df['ENDERECO'] = df['RUA'].astype(str) + ', ' + df['BAIRRO'].astype(str) + ', ' + df['CEP'].astype(str)
    
    # Remove as colunas originais de endereço
    # df = df.drop(columns=['RUA', 'BAIRRO', 'CEP'])

    # Adiciona a nova coluna 'OBS' vazia
    df['OBS'] = ''

    # Reorganiza as colunas na ordem desejada para o arquivo final
    colunas_ordenadas = [
        'INSCRICAO', 'NOME', 'CPF', 'DIA',
        'HORÁRIO DE ABERTURA DOS PORTÕES', 'HORÁRIO DE FECHAMENTO DOS PORTÕES', 'HORÁRIO DAS PROVAS',
        'CONCURSO', 'CARGO', 'LOCAL_PROVA', 
        'ESCOLA', 'ANDAR', 'BLOCO', 'SALA', 'ENDERECO', 'OBS'
    ]
    df = df[colunas_ordenadas]

    os.makedirs(output_dir, exist_ok=True)
    caminho_arquivo = os.path.join(output_dir, 'tablets.csv')

    # Exporta para CSV com separador ;
    df.to_csv(caminho_arquivo, index=False, sep=";", encoding="utf-8-sig")
    print(f"Arquivo exportado com sucesso: {caminho_arquivo}")
