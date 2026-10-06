from jinja2 import Environment, FileSystemLoader

from models import Sala

TEMPLATE_DIR = 'templates/etiqueta'
TEMPLATE_FILE = 'etiqueta.html'


def gerar_etiqueta(
    edital: str,
    
    tipo: str,
    escola: str,
    cidade: str,

    sala: Sala,
    
    quantidade: int,
    cargos_dict: dict,
    ensalado_ref=None,
) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    ref = ensalado_ref or sala.ensalados[0]

    html = template.render(
        concurso=edital,
        data_hora=str(ref.candidato.cargo.data_prova)+" "+str(ref.candidato.cargo.hora_prova),
        cidade=cidade,
        tipo=tipo,
        escola=escola,
        cargo=ref.candidato.cargo.nome,
        bloco=sala.bloco,
        andar=sala.andar,
        sala=sala.sala,
        turno=ref.candidato.cargo.turno,
        dia=ref.candidato.cargo.dia,
        envelope=sala.envelope,
        quantidade=quantidade,
        cargos_dict=cargos_dict
    )

    return html 