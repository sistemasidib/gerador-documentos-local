import dataclasses

from models.ensalamento import Ensalamento

@dataclasses.dataclass
class Sala: 
    id: int
    bloco: str
    andar: str
    sala: str
    envelope: str
    ensalados: list[Ensalamento]
