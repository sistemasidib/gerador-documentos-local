import dataclasses

from models.sala import Sala

@dataclasses.dataclass
class Escola:
    id: int
    tag: str
    nome: str
    cidade: str
    uf: str
    salas: list[Sala]