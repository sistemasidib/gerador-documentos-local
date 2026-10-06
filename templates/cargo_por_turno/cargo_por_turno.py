import os
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

from models.bdFormatado import BdFormatado
from models.escola import Escola
from templates.componentes.header.header import gerar_header

# Caminho do diretório onde está o template
TEMPLATE_DIR = 'templates/cargo_por_turno'
TEMPLATE_FILE = 'cargo_por_turno.html'

def formatar_turno(escolas: list[Escola]):
    if len(escolas) == 0:
        return

    turno = {
        'turno': escolas[0].salas[0].ensalados[0].candidato.cargo.turno,
        'dia': escolas[0].salas[0].ensalados[0].candidato.cargo.dia,
        'horario': escolas[0].salas[0].ensalados[0].candidato.cargo.hora_prova,
        'qtd_candidatos': 0,
        'cargos': [],
    }
    cargos = {}

    for escola in escolas:
        for sala in escola.salas:
            for ensalado in sala.ensalados:
                cargo = ensalado.candidato.cargo
                if cargo.id not in cargos.keys():
                    cargos[cargo.id] = {
                        'qtd': 1,
                        'nome': cargo.nome,
                        'nivel': cargo.escolaridade,
                    }
                else:
                    cargos[cargo.id]['qtd'] += 1

                turno['qtd_candidatos'] += 1

    turno['cargos'] = list(cargos.values())

    return turno

    

def gerar_cargo_por_turno(
    prefeitura_logo: str,
    instituto_logo: str,
    db: BdFormatado,
) -> str:
    """
    Retorna o HTML renderizado como string com os dados injetados no template.
    """

    manha_sabado = formatar_turno(db.sabado.manha)
    tarde_sabado = formatar_turno(db.sabado.tarde)

    manha_domingo = formatar_turno(db.domingo.manha)
    tarde_domingo = formatar_turno(db.domingo.tarde)
   
    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=db.edital.nome,
        nome_arquivo="DISTRIBUIÇÃO DE CANDIDATOS / CARGOS POR TURNO"
    )

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        header=header_html,
        turnos=[manha_sabado, tarde_sabado, manha_domingo, tarde_domingo],
    )

    return html 