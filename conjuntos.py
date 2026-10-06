from models import Edital, Escola, Sala

from models.bdFormatado import BdFormatado
from templates import gerar_ata_sala, gerar_cartao_resposta, gerar_identificacao_sala, gerar_lista_porta_sala, gerar_lista_presenca, gerar_discursiva
from templates.capa_discursiva.capa_discursiva import gerar_capa_discursiva, gerar_capa_discursiva_branco
from templates.discursiva.discursiva import gerar_discursiva_styles, gerar_folha_discursiva_branco
from templates.etiqueta.etiqueta import gerar_etiqueta
from templates.etiqueta_pessoal.etiqueta_pessoal import gerar_etiqueta_pessoal
from templates.mapa_alocacao.mapa_alocacao import gerar_mapa_alocacao
from utils.utils import get_edital_base64, get_logo_base64


def _nome_edital(edital: Edital, *cargos) -> str:
    """
    Usa o edital do cargo quando todos os cargos do escopo pertencem ao mesmo
    edital. Se o escopo misturar editais, mantém o edital geral da planilha.
    """
    nomes = {
        str(cargo.edital.nome).strip()
        for cargo in cargos
        if cargo.edital and str(cargo.edital.nome).strip().lower() not in ('', 'nan')
    }

    return nomes.pop() if len(nomes) == 1 else edital.nome


def _cargos_da_sala(sala: Sala) -> list:
    return [ensalado.candidato.cargo for ensalado in sala.ensalados]


def _cargos_da_escola(escola: Escola) -> list:
    return [cargo for sala in escola.salas for cargo in _cargos_da_sala(sala)]


def gerar_conjunto_logistica(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()

    nome_edital = _nome_edital(edital, *_cargos_da_sala(sala))

    html: str = ''

    html += gerar_identificacao_sala(
        edital_64,
        logo_64,
        nome_edital,
        escola.nome,
        escola.tag,
        escola.cidade,
        sala
    )
    
    html += gerar_lista_porta_sala(
        edital_64,
        logo_64,
        nome_edital,
        escola.nome,
        escola.cidade,
        sala

    )

    html += gerar_lista_presenca(
        edital_64,
        logo_64,
        nome_edital,
        escola.nome,
        escola.cidade,
        sala

    )
    
    html += gerar_ata_sala(
        edital_64,
        logo_64,
        nome_edital,
        escola.nome,
        sala
    )

    return html

def gerar_conjunto_lista_geral(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()
    
    html: str = ''
    
    html += gerar_lista_porta_sala(
        edital_64,
        logo_64,
        _nome_edital(edital, *_cargos_da_sala(sala)),
        escola.nome,
        escola.cidade,
        sala
    )

    return html

def gerar_conjunto_lista_presenca(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()
    
    html: str = ''
    
    html += gerar_lista_presenca(
        edital_64,
        logo_64,
        _nome_edital(edital, *_cargos_da_sala(sala)),
        escola.nome,
        escola.cidade,
        sala

    )

    return html

def gerar_conjunto_cartao_resposta(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()
    
    html: str = ''

    html += gerar_identificacao_sala(
        edital_64,
        logo_64,
        _nome_edital(edital, *_cargos_da_sala(sala)),
        escola.nome,
        escola.tag,
        escola.cidade,
        sala
    )

    for ensalado in sala.ensalados:
        html += gerar_cartao_resposta(
            edital_64,
            logo_64,
            _nome_edital(edital, ensalado.candidato.cargo),
            escola.nome,
            sala,
            ensalado
        )

    return html

def gerar_conjunto_discursiva(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()
    
    html: str = ''

    # html += gerar_discursiva_styles()

    for ensalado in sala.ensalados:
        ensalado_html = ''
        discursiva = ensalado.candidato.cargo.qtd_questoes_discursiva
        nome_edital = _nome_edital(edital, ensalado.candidato.cargo)

        for questao in range(1, discursiva + 1):
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="DISCURSIVA",
                qtd_linhas=ensalado.candidato.cargo.qtd_linhas_discursiva,
                questao=questao
            )

        if ensalado.candidato.cargo.redacao > 0:
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="REDAÇÃO",
                qtd_linhas=ensalado.candidato.cargo.redacao
            )

        if ensalado.candidato.cargo.peca > 0:
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="PEÇA PROCESSUAL",
                qtd_linhas=ensalado.candidato.cargo.peca
            )

        # se tiver vazio, ignora
        if not ensalado_html:
            continue

        html += gerar_capa_discursiva(
            edital_logo=edital_64,
            edital=nome_edital,
            escola=escola.nome,
            sala=sala,
            ensalado=ensalado,
        ) + ensalado_html
        

    if html:
        capa= ''
        capa = gerar_identificacao_sala(
            edital_64,
            logo_64,
            _nome_edital(edital, *_cargos_da_sala(sala)),
            escola.nome,
            escola.tag,
            escola.cidade,
            sala
        )
        header = gerar_discursiva_styles()

        html = capa + header + html

    return html


def gerar_conjunto_discursiva_sem_capa(edital: Edital, escola: Escola, sala: Sala) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()
    
    html: str = ''

    # html += gerar_discursiva_styles()

    for ensalado in sala.ensalados:
        ensalado_html = ''
        discursiva = ensalado.candidato.cargo.qtd_questoes_discursiva
        nome_edital = _nome_edital(edital, ensalado.candidato.cargo)

        for questao in range(1, discursiva + 1):
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="DISCURSIVA",
                qtd_linhas=ensalado.candidato.cargo.qtd_linhas_discursiva,
                questao=questao
            )

        if ensalado.candidato.cargo.redacao > 0:
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="REDAÇÃO",
                qtd_linhas=ensalado.candidato.cargo.redacao
            )

        if ensalado.candidato.cargo.peca > 0:
            ensalado_html += gerar_discursiva(
                edital=nome_edital,
                escola=escola.nome,
                ensalado=ensalado,
                tipo="PEÇA PROCESSUAL",
                qtd_linhas=ensalado.candidato.cargo.peca
            )

        # se tiver vazio, ignora
        if not ensalado_html:
            continue

        html += gerar_capa_discursiva(
            edital_logo=edital_64,
            edital=nome_edital,
            escola=escola.nome,
            sala=sala,
            ensalado=ensalado,
        ) + ensalado_html
        

    if html:
        capa= ''
        # capa = gerar_identificacao_sala(
        #     edital_64,
        #     logo_64,
        #     edital.nome,
        #     escola.nome,
        #     escola.tag,
        #     escola.cidade,
        #     sala
        # )
        header = gerar_discursiva_styles()

        html = capa + header + html

    return html

def gerar_etiquetas(edital: Edital, escola: Escola, sala: Sala, tipo: str) -> str:
    html: str = ''

    quantidade = 0
    cargos = {}
    for ensalado in sala.ensalados:
        if ensalado.candidato.cargo.nome in cargos.keys():
            cargos[ensalado.candidato.cargo.nome] += 1
        else:
            cargos[ensalado.candidato.cargo.nome] = 1

        quantidade += 1

    html += gerar_etiqueta(
        edital=_nome_edital(edital, *_cargos_da_sala(sala)),
        tipo=tipo,
        escola=escola.nome,
        cidade=escola.uf,

        sala=sala,
        cargos_dict=cargos,
        quantidade=quantidade
    )



    return html

def gerar_etiqueta_prova(edital: Edital, escola: Escola, sala: Sala) -> str:
    return gerar_etiquetas(edital, escola, sala, 'CADERNO DE PROVA')

def gerar_etiqueta_respostas(edital: Edital, escola: Escola, sala: Sala) -> str:
    return gerar_etiquetas(edital, escola, sala, 'FOLHAS DE RESPOSTAS')

def _tem_discursiva(ensalado) -> bool:
    cargo = ensalado.candidato.cargo
    return (
        (cargo.qtd_questoes_discursiva or 0) > 0
        or (cargo.redacao or 0) > 0
        or (cargo.peca or 0) > 0
    )

def gerar_etiqueta_discursiva(edital: Edital, escola: Escola, sala: Sala) -> str:
    # Mesmo critério da discursiva: só gera se houver redação/peça/questão discursiva
    ensalados = [e for e in sala.ensalados if _tem_discursiva(e)]
    if not ensalados:
        return ''

    quantidade = 0
    cargos = {}
    for ensalado in ensalados:
        nome_cargo = ensalado.candidato.cargo.nome
        cargos[nome_cargo] = cargos.get(nome_cargo, 0) + 1
        quantidade += 1

    return gerar_etiqueta(
        edital=_nome_edital(edital, *(e.candidato.cargo for e in ensalados)),
        tipo='ETIQUETA DE DISCURSIVAS',
        escola=escola.nome,
        cidade=escola.uf,
        sala=sala,
        cargos_dict=cargos,
        quantidade=quantidade,
        ensalado_ref=ensalados[0],
    )

def gerar_etiquetas_pessoais(edital: Edital, escola: Escola, sala: Sala) -> str:
    html: str = ''

    for ensalado in sala.ensalados:
        html += gerar_etiqueta_pessoal(
            edital=_nome_edital(edital, ensalado.candidato.cargo),
            nome_escola=escola.nome,
            escola_tag=escola.tag,
            local=escola.uf,
            ensalado=ensalado,
            sala=sala
        )

    return html

# conjuntos por escola
def gerar_controle(db: BdFormatado, documento) -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()

    html: str = ''

    for escola in db.sabado.manha:
        html += documento(
            edital_64,
            logo_64,
            edital=_nome_edital(db.edital, *_cargos_da_escola(escola)),
            escola=escola,
            turno='MANHÃ',
            dia='SABADO'
        )

    for escola in db.sabado.tarde:
        html += documento(
            edital_64,
            logo_64,
            edital=_nome_edital(db.edital, *_cargos_da_escola(escola)),
            escola=escola,
            turno='TARDE',
            dia='SABADO'
        )

    for escola in db.domingo.manha:
        html += documento(
            edital_64,
            logo_64,
            edital=_nome_edital(db.edital, *_cargos_da_escola(escola)),
            escola=escola,
            turno='MANHÃ',
            dia='DOMINGO'
        )

    for escola in db.domingo.tarde:
        html += documento(
            edital_64,
            logo_64,
            edital=_nome_edital(db.edital, *_cargos_da_escola(escola)),
            escola=escola,
            turno='TARDE',
            dia='DOMINGO'
        )

    return html



def gerar_conjunto_discursiva_branco(
    db: BdFormatado,
    id: int,
    qtd_questao: int,
    qtd_linhas_questao: int,
    qtd_linhas_redacao: int,
    qtd_linhas_peca: int,
)-> str:
    
    edital_64 = get_edital_base64()
    
    # html: str = gerar_discursiva_styles()
    
    html = gerar_capa_discursiva_branco(
        edital_logo=edital_64,
        edital=db.edital.nome,
        id=id
    )
    ensalado_html: str = ''
    
    for questao in range(1, qtd_questao + 1):
        ensalado_html += gerar_folha_discursiva_branco(
            edital=db.edital.nome,
            id=id,
            tipo="DISCURSIVA",
            qtd_linhas=qtd_linhas_questao,
            questao=questao
        )

    if qtd_linhas_redacao > 0:
        ensalado_html += gerar_folha_discursiva_branco(
            edital=db.edital.nome,
            id=id,
            tipo="REDAÇÃO",
            qtd_linhas=qtd_linhas_redacao
        )

    if qtd_linhas_peca > 0:
        ensalado_html += gerar_folha_discursiva_branco(
            edital=db.edital.nome,
            id=id,
            tipo="PEÇA PROCESSUAL",
            qtd_linhas=qtd_linhas_peca
        )
        
    return html + ensalado_html