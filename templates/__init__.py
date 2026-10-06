from .ata_sala.ata_sala import gerar_ata_sala
# from .capa_discursiva import gerar_capa_discursiva
from .cargo_por_escola.cargo_por_escola import gerar_cargo_por_escola
from .cargo_por_sala.cargo_por_sala import gerar_cargo_por_sala
from .cargo_por_turno.cargo_por_turno import gerar_cargo_por_turno
from .cartao_resposta.cartao_resposta import gerar_cartao_resposta
from .componentes.header.header import gerar_header 
from .discursiva.discursiva import gerar_discursiva
from .etiqueta.etiqueta import gerar_etiqueta
from .etiqueta_pessoal.etiqueta_pessoal import gerar_etiqueta_pessoal
from .identificacao_sala.identificacao_sala import gerar_identificacao_sala
from .lista_porta_sala.lista_porta_sala import gerar_lista_porta_sala
from .lista_presenca.lista_presenca import gerar_lista_presenca
from .mapa_alocacao.mapa_alocacao import gerar_mapa_alocacao

__all__ = [
    'gerar_ata_sala',
    # 'gerar_capa_discursiva',
    'gerar_cargo_por_escola',
    'gerar_cargo_por_sala',
    'gerar_cargo_por_turno',
    'gerar_cartao_resposta',
    'gerar_header',
    'gerar_discursiva',
    'gerar_etiqueta',
    'gerar_etiqueta_pessoal',
    'gerar_identificacao_sala',
    'gerar_lista_porta_sala',
    'gerar_lista_presenca',
    'gerar_mapa_alocacao',
    ]