from jinja2 import Environment, FileSystemLoader
import segno
import math

from models import Ensalamento
from utils.criptografia import mascarar_numero

# Caminhos dos diretórios
TEMPLATE_DIR = 'templates/discursiva'
ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def gerar_discursiva(
        edital: str,
        escola: str,
        ensalado: Ensalamento,
        tipo: str,
        qtd_linhas: int,
        questao: int = 0,
) -> str:

    qr_code = segno.make(mascarar_numero(ensalado.candidato.inscricao), error='H' ).svg_inline(
        dark='#000000', scale=3, border=0
    )

    qr_code_ordem = segno.make(ensalado.ordem_geral, error='H').svg_inline(
        dark='#000000', scale=3, border=0
    )

    # Carregar template principal
    # env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = ENV.get_template('body.html')
    
    html = template.render(
        edital=edital,
        escola=escola,
        cargo=ensalado.candidato.cargo.nome,
        tipo=tipo,
        questao= "" if questao == 0 else f"Resposta - Questão {questao}",
        
        qtd_linhas=qtd_linhas,
        qr_code=qr_code,
        qr_code_ordem = qr_code_ordem,
        min=min,
        ceil=math.ceil
    )
    
    return html

def gerar_discursiva_styles() -> str:
    # Carregar template principal
    # env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = ENV.get_template('style.html')
    
    html = template.render()  

    return html


def gerar_folha_discursiva_branco(
        edital: str,
        id: int,
        tipo: str,
        qtd_linhas: int,
        questao: int = 0,
) -> str:

    qr_code = segno.make(mascarar_numero(id), error='H' ).svg_inline(
        dark='#000000', scale=3, border=0
    )

    # qr_code_ordem = segno.make(str(ensalado.ordem_geral).center(24)).svg_inline(
    #     dark='#000000', scale=3, border=0
    # )

    # Carregar template principal
    # env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = ENV.get_template('body.html')
    
    html = template.render(
        edital=edital,
        escola='',
        cargo='',
        tipo=tipo,
        questao= "" if questao == 0 else f"Resposta - Questão {questao}",
        
        qtd_linhas=qtd_linhas,
        qr_code=qr_code,
        qr_code_ordem = '',
        min=min,
        ceil=math.ceil
    )
    
    return html