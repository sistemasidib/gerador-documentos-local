from jinja2 import Environment, FileSystemLoader
import segno

from models.ensalamento import Ensalamento
from models.sala import Sala

TEMPLATE_DIR = 'templates/etiqueta_pessoal'
TEMPLATE_FILE = 'etiqueta_pessoal.html'


def gerar_etiqueta_pessoal(
    edital: str,
    nome_escola: str,
    escola_tag: str,
    local: str,

    ensalado: Ensalamento,

    sala: Sala
) -> str:
    # Gerar QR code com o conteúdo sendo o ID da inscrição
    qr_code_svg_inline = segno.make(
        ensalado.candidato.inscricao, error='H', mode='numeric',
    ).svg_inline(dark='#000000', scale=8, border=0)

    # Dia/turno corretos vêm do ensalamento (cargo.dia fica preso no 1º registro do cargo)
    dia = str(getattr(ensalado, "dia", "") or "").strip()
    turno = str(getattr(ensalado, "turno", "") or "").strip().upper()
    if turno == "MADRUGADA":
        turno = "MANHÃ"

    # Carregar template Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        edital=edital,
        cargo=ensalado.candidato.cargo.nome,
        nome_escola=nome_escola,
        escola_tag=escola_tag,
        local=local,
        nome_candidato=ensalado.candidato.nome,
        turno=turno,
        dia=dia,
        numero_ordem=ensalado.carteira,
        id_inscricao=ensalado.candidato.inscricao,
        rg=ensalado.candidato.cpf,
        qr_code_data_uri=qr_code_svg_inline,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,
        horario=ensalado.candidato.cargo.hora_prova,
    )

    return html
