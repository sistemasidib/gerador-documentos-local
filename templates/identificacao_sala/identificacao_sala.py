import os
from jinja2 import Environment, FileSystemLoader

from models import Sala
from utils.utils import normalizar_dia_turno

# Caminho do diretório onde está o template
TEMPLATE_DIR = 'templates/identificacao_sala'
TEMPLATE_FILE = 'identificacao_sala.html'

COMPONENTES_DIR = 'templates/componentes/header/'
HEADER_DIR = 'header.html'

def gerar_identificacao_sala(
    edital_logo: str,
    instituto_logo: str,

    edital: str,
    nome_escola: str,
    escola_tag: str,
    cidade: str,
    
    # bloco: str,
    # andar: str,
    # sala: str,
    # sala_id: int,
    
    sala: Sala,
    
    # shift: str,
    # cargos: dict
) -> str:
    """
    Retorna o HTML renderizado como string com os dados injetados no template.
    """

    # pegar infos restantes
    dia = ""
    shift = ""
    if sala.ensalados:
        ensalado_ref = sala.ensalados[0]
        dia, shift = normalizar_dia_turno(
            dia=getattr(ensalado_ref, "dia", "") or "",
            turno=getattr(ensalado_ref, "turno", "") or "",
            data_prova=getattr(ensalado_ref, "data_prova", None),
        )

    cargos = {}
    for ensalado in sala.ensalados:
        cargo = ensalado.candidato.cargo
        if cargo.nome not in cargos.keys():
            cargos[cargo.nome] = {
                "id": cargo.id,
                "nome": cargo.nome,
                "qtde": 1
                }
        else:
            cargos[cargo.nome]["qtde"] += 1


    # Carregar componentes
    env = Environment(loader=FileSystemLoader(COMPONENTES_DIR))
    header = env.get_template(HEADER_DIR)

    header_html = header.render(
        edital_logo=edital_logo,
        instituto_logo=instituto_logo,
        edital=edital,
        nome_arquivo="IDENTIFICAÇÃO DE SALA"
    )

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        header=header_html,
        edital=edital,
        nome_escola=nome_escola,
        bloco=sala.bloco,
        andar=sala.andar,
        shift=shift,
        dia=dia,
        sala=sala.sala,
        envelope=sala.envelope,
        cargos=cargos,  # Dicionário com os cargos
        escola_tag = escola_tag,
        cidade = cidade
    )

    return html



