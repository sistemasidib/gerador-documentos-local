from jinja2 import Environment, FileSystemLoader

from models.escola import Escola
from templates.componentes.header.header import gerar_header

TEMPLATE_DIR = 'templates/cargo_por_sala'
TEMPLATE_FILE = 'cargo_por_sala.html'

COMPONENTES_DIR = 'templates/componentes/header'
HEADER_DIR = 'header.html'

def gerar_cargo_por_sala(
    prefeitura_logo: str,
    instituto_logo: str,
    edital: str,
    escola: Escola,

    turno: str,
    dia: str
) -> str:
    """
    Gera o HTML da distribuição de cargos por sala.
    """

    salas = []
    total_candidatos = 0
    for sala in escola.salas:
        sala_f = {
            'escola': escola.nome,
            'bloco': sala.bloco,
            'andar': sala.andar,
            'sala': sala.sala,
            'qtd_candidatos': len(sala.ensalados),
            'horario': sala.ensalados[0].candidato.cargo.hora_prova,
            'turno': turno,
            'dia': dia
        }
        cargos = {}
        for ensalado in sala.ensalados:
            cargo = ensalado.candidato.cargo
            if cargo.id not in cargos.keys():
                cargos[cargo.id] = {
                    'qtd': 1,
                    'nome': str(cargo.id) +" " + cargo.nome,
                    'nivel': cargo.escolaridade,
                }
            else:
                cargos[cargo.id]['qtd'] += 1
        sala_f['cargos'] = list(cargos.values())
        salas.append(sala_f)

    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=edital,
        nome_arquivo="DISTRIBUIÇÃO DE CANDIDATOS / CARGOS POR SALA"
    )

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)
    html = template.render(
        header=header_html,
        prefeitura_logo=prefeitura_logo,
        instituto_logo=instituto_logo,
        edital=edital,
        salas=salas,
    )
    return html