import base64
from jinja2 import Environment, FileSystemLoader
import segno

from models import Sala, Ensalamento

TEMPLATE_DIR = 'templates/cartao_resposta'
TEMPLATE_FILE = 'cartao_resposta.html'


def gerar_cartao_resposta(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    nome_escola: str,

    sala: Sala,

    ensalado: Ensalamento,
) -> str:
    """
    Retorna o conteúdo HTML do cartão-resposta com as informações e QR Code injetados.
    """
    # Gerar QR code com o conteúdo sendo o ID da inscrição
    qr_code_svg_inline = segno.make(ensalado.candidato.inscricao, error='H').svg_inline(
        dark='#000000', scale=4, border=0
    )

    # Carregar template Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        prefeitura_logo=prefeitura_logo,
        instituto_logo=instituto_logo,
        edital=edital,
        ordem_geral = ensalado.ordem_geral,
        id_inscricao=ensalado.candidato.inscricao,
        qr_code=qr_code_svg_inline,
        candidato_cpf=ensalado.candidato.cpf,
        nome_candidato=ensalado.candidato.nome,
        ordem=ensalado.carteira,
        candidato_rg=ensalado.candidato.rg,
        nome_escola=nome_escola,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,
        nome_cargo=ensalado.candidato.cargo.nome,
        turno=ensalado.candidato.cargo.turno,
        questoes=ensalado.candidato.cargo.qtd_questoes_prova,

        dia=ensalado.candidato.cargo.dia,
        id_cargo=ensalado.candidato.cargo.id,
        min=min,
    )

    return html


def gerar_cartao_resposta_branco(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    questoes: int
) -> str:
    """
    Retorna o conteúdo HTML do cartão-resposta com as informações e QR Code injetados.
    """

    # Carregar template Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        prefeitura_logo=prefeitura_logo,
        instituto_logo=instituto_logo,
        edital=edital,
        nome_escola='',
        bloco='',
        andar='',
        turno='',
        nome_sala='',
        ordem='',
        nome_cargo='',
        id_cargo='',
        id_inscricao='',
        nome_candidato='',
        candidato_cpf='',
        questoes=questoes,
        qr_code='',
        min=min,
    )

    return html