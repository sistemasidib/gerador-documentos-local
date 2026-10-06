from jinja2 import Environment, FileSystemLoader

from models import Sala
from templates.componentes.header.header import gerar_header
from utils.utils import normalizar_dia_turno

TEMPLATE_DIR = 'templates/lista_porta_sala'
TEMPLATE_FILE = 'lista_porta_sala.html'

COMPONENTES_DIR = './templates/componentes/header/'
HEADER_FILE = 'header.html'


def gerar_lista_porta_sala(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    nome_escola: str,
    cidade: str,

    sala: Sala,

    # bloco: str,
    # andar: str,
    # sala: str,
    # candidatos: list[dict]
) -> str:
    """
    Retorna o conteúdo HTML da lista de porta de sala com as informações injetadas
    no formato do template 'lista_porta_sala_ref.html'.
    
    :param prefeitura_logo: Caminho ou base64 do logo da prefeitura.
    :param instituto_logo: Caminho ou base64 do logo do instituto.
    :param edital: Texto do edital.
    :param nome_escola: Nome da escola.
    :param bloco: Bloco da sala.
    :param andar: Andar da sala.
    :param sala: Nome ou número da sala.
    :param candidatos: Lista de dicionários:
        [
            {"id": "123456", "nome": "João da Silva", "cargo": "Professor"},
            ...
        ]
    """

    candidatos = []

    # dia/turno vêm do primeiro ensalado (todos da sala devem compartilhar)
    dia = ""
    turno = ""
    if sala.ensalados:
        ensalado_ref = sala.ensalados[0]
        dia, turno = normalizar_dia_turno(
            dia=getattr(ensalado_ref, "dia", "") or "",
            turno=getattr(ensalado_ref, "turno", "") or "",
            data_prova=getattr(ensalado_ref, "data_prova", None),
        )
    for ensalado in sala.ensalados:
        candidatos.append({
            "inscricao": ensalado.candidato.inscricao,
            "numero_ordem": ensalado.carteira,
            "nome": ensalado.candidato.nome,
            "cargo": ensalado.candidato.cargo.nome,
        })
    
    # Carrega o componente de header
    # env_componentes = Environment(loader=FileSystemLoader(COMPONENTES_DIR))
    # header_template = env_componentes.get_template(HEADER_FILE)
    
    # header_html = header_template.render(
    #     prefeitura_logo=prefeitura_logo,
    #     instituto_logo=instituto_logo,
    #     edital=edital,
    #     nome_arquivo="LISTA PORTA DE SALA"
    # )

    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=edital,
        nome_arquivo="LISTA GERAL"
    )

    # Carrega o template principal
    env_principal = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env_principal.get_template(TEMPLATE_FILE)

    html = template.render(
        header=header_html,
        nome_escola=nome_escola,
        cidade=cidade,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,
        dia=dia,
        turno=turno,
        candidatos=candidatos,
        total_candidatos=len(sala.ensalados)
    )

    return html
