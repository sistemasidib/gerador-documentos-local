import os
from jinja2 import Environment, FileSystemLoader

from models.escola import Escola
from templates.componentes.header.header import gerar_header

# Caminhos dos diretórios
TEMPLATE_DIR = 'templates/mapa_alocacao'
COMPONENTES_DIR = 'templates/componentes/header'
HEADER_FILE = 'header.html'

def gerar_mapa_alocacao(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    escola: Escola,

    turno: str,
    dia: str
) -> str:
    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=edital,
        nome_arquivo="RELATÓRIO DE SALAS"
    )

    salas = {}
    total_candidatos = 0
    for sala in escola.salas:
        for ensalado in sala.ensalados:
            cargo_sala = str(ensalado.candidato.cargo.id) +'_'+ str(sala.id)
            total_candidatos += 1
            if cargo_sala not in salas.keys():
                salas[cargo_sala] = {
                    "bloco": sala.bloco,
                    "andar": sala.andar,
                    "nome": sala.sala,
                    "min_carteira": ensalado.ordem_geral,
                    "max_carteira": ensalado.ordem_geral,
                    "primeiro_candidato": ensalado.candidato.nome,
                    "ultimo_candidato": ensalado.candidato.nome,
                    "cargo": str(ensalado.candidato.cargo.id) +" " + ensalado.candidato.cargo.nome,
                    "quantidade_candidatos": 1
                }
            else:
                salas[cargo_sala]["max_carteira"] = ensalado.ordem_geral
                salas[cargo_sala]["ultimo_candidato"] = ensalado.candidato.nome
                salas[cargo_sala]["quantidade_candidatos"] += 1
        

    # Carregar template principal
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('mapa_alocacao.html')
    
    html = template.render(
        header=header_html,
        escola=escola.nome,
        local_prova=escola.cidade,
        turno=turno,
        dia=dia,
        salas=list(salas.values()),
        total_candidatos=total_candidatos
    )
    
    return html