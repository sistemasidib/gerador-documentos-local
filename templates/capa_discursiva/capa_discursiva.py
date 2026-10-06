import base64
import os
from jinja2 import Environment, FileSystemLoader
import segno

from models import Ensalamento
from models.sala import Sala
from utils.criptografia import mascarar_numero

# Caminhos dos diretórios
TEMPLATE_DIR = 'templates/capa_discursiva'

def gerar_capa_discursiva(
        edital_logo: str,

        edital: str,
        escola: str,
        sala: Sala,
        ensalado: Ensalamento,
) -> str:


    # inscricao_str = str(ensalado.candidato.inscricao)   # converte para string
    # base64_str = base64.b64encode(inscricao_str.encode("utf-8")).decode("utf-8")

    # qr_code_cod = segno.make(base64_str, error='H').svg_inline(
    #     dark='#000000', scale=3, border=0
    # )

    qr_code_cod = segno.make(mascarar_numero(ensalado.candidato.inscricao), error='H' ).svg_inline(
        dark='#000000', scale=3, border=0
    )

    qr_code = segno.make(
        ensalado.candidato.inscricao, error='H',
    ).svg_inline(dark='#000000', scale=4, border=0)

    # Carregar template principal
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('capa_discursiva.html')
    
    html = template.render(
        prefeitura_logo=edital_logo,
        edital=edital,
        sequencial= ensalado.ordem_geral,
        inscricao=ensalado.candidato.inscricao,
        nome_candidato=ensalado.candidato.nome,
        rg=ensalado.candidato.rg,

        cargo=ensalado.candidato.cargo.nome,
        escola=escola,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,

        turno=ensalado.candidato.cargo.turno,
        dia=ensalado.candidato.cargo.dia,

        carteira=ensalado.carteira,
        
        qr_code=qr_code,
        qr_code_cod=qr_code_cod
    )
    
    return html


def gerar_capa_discursiva_branco(
        edital_logo: str,
        edital:str,
        id: int

) -> str:

    qr_code_cod = segno.make(mascarar_numero(id), error='H' ).svg_inline(
        dark='#000000', scale=3, border=0
    )


    qr_code = segno.make(id, error='H').svg_inline(
        dark='#000000', scale=4.5, border=0
    )

    # Carregar template principal
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('capa_discursiva.html')
    
    html = template.render(
        prefeitura_logo=edital_logo,
        edital=edital,
        sequencial= '',
        inscricao='',
        nome_candidato='',
        rg='',

        cargo='',
        escola='',
        bloco='',
        andar='',
        sala='',

        turno='',

        carteira='',
        
        qr_code=qr_code,
        qr_code_cod=qr_code_cod
    )
    
    return html