import dataclasses

from models.edital import Edital
from models.escola import Escola


@dataclasses.dataclass
class DiaBD:
    manha: list[Escola]
    tarde: list[Escola]

@dataclasses.dataclass
class BdFormatado:
    edital: Edital
    sabado: DiaBD
    domingo: DiaBD

