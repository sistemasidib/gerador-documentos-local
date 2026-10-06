import dataclasses

from models import Cargo

@dataclasses.dataclass
class Candidato:
    inscricao: int
    nome: str
    rg: str
    cpf: str
    tipo: str
    solicitacao: str
    cargo: Cargo