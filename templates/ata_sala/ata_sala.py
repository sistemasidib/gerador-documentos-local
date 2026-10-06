import os
from jinja2 import Environment, FileSystemLoader

from models.sala import Sala
from templates.componentes.header.header import gerar_header
from utils.utils import normalizar_dia_turno

# Caminhos dos diretórios
TEMPLATE_DIR = 'templates/ata_sala'
COMPONENTES_DIR = 'templates/componentes/header/'
HEADER_FILE = 'header.html'

def gerar_ata_sala(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    escola: str,

    sala: Sala,

    # bloco: str,
    # andar: str,
    # sala: str,
    # inscritos: int
) -> str:
    """
    Gera o HTML da Ata de Sala com base nos dados fornecidos.
    
    Args:
        prefeitura_logo: Data URL da logo da prefeitura
        instituto_logo: Data URL da logo do instituto
        edital: Nome do edital
        escola: Nome da escola
        bloco: Bloco da sala
        andar: Andar da sala
        sala: Número da sala
        inscritos: Total de inscritos na sala
        
    Returns:
        HTML renderizado como string
    """
    # Carregar header component
    # env = Environment(loader=FileSystemLoader(COMPONENTES_DIR))
    # header_template = env.get_template(HEADER_FILE)
    # header_html = header_template.render(
    #     prefeitura_logo=prefeitura_logo,
    #     instituto_logo=instituto_logo,
    #     edital=edital,
    #     nome_arquivo="ATA DE SALA"
    # )

    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=edital,
        nome_arquivo="ATA DE SALA"
    )

    # Carregar template principal
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('ata_sala.html')
    
    dia = ""
    turno = ""
    if sala.ensalados:
        ensalado_ref = sala.ensalados[0]
        dia, turno = normalizar_dia_turno(
            dia=getattr(ensalado_ref, "dia", "") or "",
            turno=getattr(ensalado_ref, "turno", "") or "",
            data_prova=getattr(ensalado_ref, "data_prova", None),
        )

    html = template.render(
        header=header_html,
        escola=escola,
        dia=dia,
        turno=turno,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,
        inscritos=len(sala.ensalados)
    )
    
    return html