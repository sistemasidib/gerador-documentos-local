import math
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from formatador import formatar_bd
from conjuntos import  gerar_conjunto_cartao_resposta, gerar_conjunto_discursiva_sem_capa, gerar_conjunto_lista_geral, gerar_conjunto_lista_presenca, gerar_conjunto_logistica, gerar_conjunto_discursiva, gerar_etiqueta_discursiva, gerar_etiqueta_prova, gerar_etiqueta_respostas, gerar_etiquetas_pessoais
from gerador import executar_relatorios, exportar_com_codigo, exportar_doc, gerar_cartao_branco, gerar_discursiva_branco, gerar_relatorios_controle, gerar_relatorios_controle_escola
from ler_documento import exportar_candidatos_especiais, exportar_info_escolas, exportar_info_vini, ler_bd, ler_bd_xls
from models.bdFormatado import BdFormatado
from models.ensalamento import Ensalamento
from models.escola import Escola
from models.sala import Sala
from templates.cargo_por_escola.cargo_por_escola import gerar_cargo_por_escola
from templates.cargo_por_sala.cargo_por_sala import gerar_cargo_por_sala
from templates.cargo_por_turno.cargo_por_turno import gerar_cargo_por_turno
from templates.lista_presenca.lista_presenca import gerar_lista_presenca
from templates.mapa_alocacao.mapa_alocacao import gerar_mapa_alocacao
from templates.qrcode.qrcode import gerar_qr_code
from utils.limpar_terminal import clear_terminal
from utils.pdfExporter import PDFExporter
from utils.utils import set_diretorio_ensalamento


# edital = "BombeirosDF geral"
  # cria apenas a pasta


def gerar_docs(edital): 
    # Define o diretório do arquivo de ensalamento para busca das logos
    diretorio_ensalamento = f'concursos/{edital}'
    set_diretorio_ensalamento(diretorio_ensalamento)
    
    df = ler_bd_xls(f'{diretorio_ensalamento}/ensalamento.xlsx') 
    # df = ler_bd_xls(f'concursos/{edital}/docs/candidatos_especiais.xlsx') 
    db = formatar_bd(df)
    total_candidatos = len(df)
    out_dir = f'concursos/{edital}/docs'
    os.makedirs(out_dir, exist_ok=True)
    # print(df['ID_EDITAL'].iloc[0])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # cartão resposta
    executar_relatorios(db.sabado.manha, db.edital, gerar_conjunto_cartao_resposta, "cartao_resposta", "sabado_manha", out_dir)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_conjunto_cartao_resposta, "cartao_resposta", "sabado_tarde", out_dir)
    executar_relatorios(db.domingo.manha, db.edital, gerar_conjunto_cartao_resposta, "cartao_resposta", "domingo_manha", out_dir)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_conjunto_cartao_resposta, "cartao_resposta", "domingo_tarde", out_dir)

    # executar_relatorios(db.sabado.manha, db.edital, gerar_conjunto_discursiva, "discursiva", "sabado_manha", out_dir)
    # executar_relatorios(db.sabado.tarde, db.edital, gerar_conjunto_discursiva, "discursiva", "sabado_tarde", out_dir)
    # executar_relatorios(db.domingo.manha, db.edital, gerar_conjunto_discursiva, "discursiva", "domingo_manha", out_dir)
    # executar_relatorios(db.domingo.tarde, db.edital, gerar_conjunto_discursiva, "discursiva", "domingo_tarde", out_dir)

    executar_relatorios(db.sabado.manha, db.edital, gerar_conjunto_discursiva_sem_capa, "discursiva_sem_capa", "sabado_manha", out_dir)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_conjunto_discursiva_sem_capa, "discursiva_sem_capa", "sabado_tarde", out_dir)
    executar_relatorios(db.domingo.manha, db.edital, gerar_conjunto_discursiva_sem_capa, "discursiva_sem_capa", "domingo_manha", out_dir)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_conjunto_discursiva_sem_capa, "discursiva_sem_capa", "domingo_tarde", out_dir)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # logística
    executar_relatorios(db.sabado.manha, db.edital, gerar_conjunto_logistica, "logistica", "sabado_manha", out_dir)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_conjunto_logistica, "logistica", "sabado_tarde", out_dir)
    executar_relatorios(db.domingo.manha, db.edital, gerar_conjunto_logistica, "logistica", "domingo_manha", out_dir)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_conjunto_logistica, "logistica", "domingo_tarde", out_dir)

    executar_relatorios(db.sabado.manha, db.edital, gerar_etiqueta_respostas, "etiqueta_respostas", "sabado_manha", out_dir, etiqueta=True)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_etiqueta_respostas, "etiqueta_respostas", "sabado_tarde", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.manha, db.edital, gerar_etiqueta_respostas, "etiqueta_respostas", "domingo_manha", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_etiqueta_respostas, "etiqueta_respostas", "domingo_tarde", out_dir, etiqueta=True)

    executar_relatorios(db.sabado.manha, db.edital, gerar_etiqueta_prova, "etiqueta_prova", "sabado_manha", out_dir, etiqueta=True)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_etiqueta_prova, "etiqueta_prova", "sabado_tarde", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.manha, db.edital, gerar_etiqueta_prova, "etiqueta_prova", "domingo_manha", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_etiqueta_prova, "etiqueta_prova", "domingo_tarde", out_dir, etiqueta=True)

    executar_relatorios(db.sabado.manha, db.edital, gerar_etiqueta_discursiva, "etiqueta_discursiva", "sabado_manha", out_dir, etiqueta=True)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_etiqueta_discursiva, "etiqueta_discursiva", "sabado_tarde", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.manha, db.edital, gerar_etiqueta_discursiva, "etiqueta_discursiva", "domingo_manha", out_dir, etiqueta=True)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_etiqueta_discursiva, "etiqueta_discursiva", "domingo_tarde", out_dir, etiqueta=True)

    executar_relatorios(db.sabado.manha, db.edital, gerar_etiquetas_pessoais, "etiqueta_pessoal", "sabado_manha", out_dir, etiqueta=True, pessoal=True)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_etiquetas_pessoais, "etiqueta_pessoal", "sabado_tarde", out_dir, etiqueta=True, pessoal=True)
    executar_relatorios(db.domingo.manha, db.edital, gerar_etiquetas_pessoais, "etiqueta_pessoal", "domingo_manha", out_dir, etiqueta=True, pessoal=True)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_etiquetas_pessoais, "etiqueta_pessoal", "domingo_tarde", out_dir, etiqueta=True, pessoal=True)

    executar_relatorios(db.sabado.manha, db.edital, gerar_conjunto_lista_geral, "lista_de_candidatos", "sabado_manha", out_dir)
    executar_relatorios(db.sabado.tarde, db.edital, gerar_conjunto_lista_geral, "lista_de_candidatos", "sabado_tarde", out_dir)
    executar_relatorios(db.domingo.manha, db.edital, gerar_conjunto_lista_geral, "lista_de_candidatos", "domingo_manha", out_dir)
    executar_relatorios(db.domingo.tarde, db.edital, gerar_conjunto_lista_geral, "lista_de_candidatos", "domingo_tarde", out_dir)

    gerar_relatorios_controle_escola(db, gerar_mapa_alocacao, "mapa_alocacao", out_dir, deitado=True)
    gerar_relatorios_controle_escola(db, gerar_cargo_por_sala, "cargo_por_sala", out_dir)

    gerar_relatorios_controle(db,gerar_cargo_por_escola, "cargo_por_escola", out_dir)
    gerar_relatorios_controle(db,gerar_cargo_por_turno, "cargo_por_turno", out_dir)

    # # # # # # # # # # # # # # # # # Uso das funções
    exportar_info_escolas(df, f'{out_dir}/escolas_info.xlsx')
    exportar_candidatos_especiais(df, f'{out_dir}/candidatos_especiais.xlsx')

    gerar_cartao_branco(db, [100],out_dir)
    gerar_discursiva_branco(
        db, 
        edital_id=int(df['ID_EDITAL'].iloc[0]), 
        qtd_candidatos=math.ceil(total_candidatos * 0.10), 
        qtd_questao=1, 
        qtd_linhas_questao=30, 
        qtd_linhas_peca=0, 
        qtd_linhas_redacao=0,
        passo=1, 
        out_dir=out_dir
    )

    # exportar_info_vini(df, out_dir)

    #  url= 'https://concurso.idib.org.br/Conteudo.aspx?ID=26010816075041387724488558307753405702228343635357'
    #  html_qrcode = gerar_qr_code(db.edital.nome, url)
    #  exportar_doc(html_qrcode, "qrcode", out_dir=out_dir)

    # exportar_com_codigo(df,f"{out_dir}/Com_Codigo.xlsx")

editais = [
    'PIAUI'	
]

for edital in editais:
    clear_terminal()
    print(f"Gerando documentos do edital: {edital}")
    print()
    gerar_docs(edital)

