import dataclasses

from models.candidato import Candidato

@dataclasses.dataclass
class Ensalamento:
    candidato: Candidato
    ordem_geral: int
    carteira: int
    turno: str
    dia: str
    data_prova: str
