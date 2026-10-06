from jinja2 import Environment, FileSystemLoader
import math

from models import Sala
from templates.componentes.header.header import gerar_header
from utils.utils import normalizar_dia_turno

TEMPLATE_DIR = 'templates/lista_presenca'
TEMPLATE_FILE = 'lista_presenca.html'

COMPONENTES_DIR = 'templates/componentes/header/'
HEADER_FILE = 'header.html'


def gerar_lista_presenca(
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
    Retorna o conteúdo HTML da lista de presença com as informações injetadas
    no formato do template 'lista_presenca.html'.

    :param prefeitura_logo: Caminho ou base64 do logo da prefeitura.
    :param instituto_logo: Caminho ou base64 do logo do instituto.
    :param edital: Texto do edital.
    :param nome_escola: Nome da escola.
    :param bloco: Bloco da sala.
    :param andar: Andar da sala.
    :param sala: Nome ou número da sala.
    :param candidatos: Lista de dicionários:
        [
            {
                "inscricao": "123456",
                "numero_ordem": "001",
                "nome": "João da Silva",
                "rg": "12.345.678-9",
                "cpf": "123.456.789-00"
            },
            ...
        ]
    :return: HTML renderizado como string.
    """


    total_candidatos = len(sala.ensalados)

    # dia/turno devem ser consistentes para todos os ensalados da sala
    dia = ""
    turno = ""
    if sala.ensalados:
        ensalado_ref = sala.ensalados[0]
        dia, turno = normalizar_dia_turno(
            dia=getattr(ensalado_ref, "dia", "") or "",
            turno=getattr(ensalado_ref, "turno", "") or "",
            data_prova=getattr(ensalado_ref, "data_prova", None),
        )
    candidatos = []
    for ensalado in sala.ensalados:
        candidatos.append({
            "inscricao": ensalado.candidato.inscricao,
            "numero_ordem": ensalado.carteira,
            "nome": ensalado.candidato.nome,
            "rg": ensalado.candidato.rg,
            "cpf": ensalado.candidato.cpf
        })

    # Carrega o componente de header
    # env_componentes = Environment(loader=FileSystemLoader(COMPONENTES_DIR))
    # header_template = env_componentes.get_template(HEADER_FILE)
    # header_html = header_template.render(
    #     prefeitura_logo=prefeitura_logo,
    #     instituto_logo=instituto_logo,
    #     edital=edital,
    #     nome_arquivo="LISTA DE PRESENÇA"
    # )

    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=edital,
        nome_arquivo="LISTA DE PRESENÇA"
    )

    # Carrega o template principal
    env_principal = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env_principal.get_template(TEMPLATE_FILE)


    # Cálculo de páginas: 1ª página com 10, demais com 14 por página
    if total_candidatos <= 16:
        total_pages = 1
    else:
        restantes = total_candidatos - 16
        total_pages = 1 + math.ceil(restantes / 16)

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
        total_pages=total_pages
    )

    return html 