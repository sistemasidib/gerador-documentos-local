from jinja2 import Environment, FileSystemLoader
import segno

from templates.componentes.header.header import gerar_header
from utils.utils import get_edital_base64, get_logo_base64

TEMPLATE_DIR = 'templates/qrcode'
COMPONENTES_DIR = 'templates/componentes/header'
HEADER_FILE = 'header.html'

def gerar_qr_code(
            edital: str,
            url: str
        ) -> str:

    header_html = gerar_header(
        edital_logo_path=get_edital_base64(),
        instituto_logo_path=get_logo_base64(),
        edital=edital,
        nome_arquivo="CONSULTAR LOCAL DE PROVA"
    )

    qr_code_svg_inline = segno.make(url).svg_inline(
        dark='#000000', scale=15, border=0
    )

    # Carregar template principal
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('qrcode.html')
    
    html = template.render(
        header=header_html,
        qr_code=qr_code_svg_inline
    )

    return html