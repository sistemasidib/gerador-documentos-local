import os
from jinja2 import Environment, FileSystemLoader
import math

from models.bdFormatado import BdFormatado
from templates.componentes.header.header import gerar_header

# Caminho do diretório onde está o template
TEMPLATE_DIR = 'templates/cargo_por_escola'
TEMPLATE_FILE = 'cargo_por_escola.html'

COMPONENTES_DIR = 'templates/componentes/header'
HEADER_DIR = 'header.html'

def gerar_cargo_por_escola(
    prefeitura_logo: str,
    instituto_logo: str,
    db: BdFormatado

) -> str:
    # Carregar componentes
    header_html = gerar_header(
        edital_logo_path=prefeitura_logo,
        instituto_logo_path=instituto_logo,
        edital=db.edital.nome,
        nome_arquivo="DISTRIBUIÇÃO DE CANDIDATOS / CARGOS POR LOCAL DE PROVA"
    )
    
    escolas = []
    for escola in db.sabado.manha + db.sabado.tarde + db.domingo.manha + db.domingo.tarde:
        escola_f = {
            'nome': escola.nome,
            'horario': escola.salas[0].ensalados[0].candidato.cargo.hora_prova,
            'turno': escola.salas[0].ensalados[0].candidato.cargo.turno,
            'dia':escola.salas[0].ensalados[0].candidato.cargo.dia,
            'qtd_candidatos': 0
        }
        cargos = {}

        for sala in escola.salas:
            escola_f['qtd_candidatos'] += len(sala.ensalados)
            for ensalado in sala.ensalados:
                cargo = ensalado.candidato.cargo
                if cargo.id not in cargos.keys():
                    cargos[cargo.id] = {
                        'qtd': 1,
                        'nome': str(cargo.id) + ' ' + cargo.nome,
                    }
                else:
                    cargos[cargo.id]['qtd'] += 1
                    
        escola_f['cargos'] = list(cargos.values())
        escolas.append(escola_f)

        

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html = template.render(
        header=header_html,
        escolas=escolas

    )

    return html 