import dataclasses

from models.edital import Edital

@dataclasses.dataclass
class Cargo:
    id: int
    nome: str
    turno: str
    dia: str
    hora_prova: str
    data_prova: str
    escolaridade: str
    qtd_questoes_prova: int
    peca: int
    qtd_questoes_discursiva: int
    qtd_linhas_discursiva: int
    redacao: int
    edital: Edital
