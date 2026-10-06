
import base64
from datetime import datetime
import mimetypes
import os
import re

from utils.pdfExporter import PDFExporter

exporter = PDFExporter()

# Variável global para armazenar o diretório do arquivo de ensalamento
_diretorio_ensalamento = None

def set_diretorio_ensalamento(diretorio: str):
    """
    Define o diretório do arquivo de ensalamento para uso na busca da logo.
    """
    global _diretorio_ensalamento
    _diretorio_ensalamento = diretorio

def exportar_cartao_para_pdf(html_content: str, output_path: str, deitado: bool = False):
    """
    Gera um arquivo PDF a partir do conteúdo HTML usando Playwright.
    """
    exporter.exportar(html_content, output_path, deitado)

def carregar_imagem_base64(caminho_imagem: str) -> str:
    """
    Lê uma imagem do disco e retorna como Data URL (base64) para uso direto em HTML.
    """
    mime_type, _ = mimetypes.guess_type(caminho_imagem)
    if not mime_type:
        raise ValueError(f"Não foi possível detectar o tipo da imagem: {caminho_imagem}")

    with open(caminho_imagem, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"

def get_logo_base64(diretorio_ensalamento: str = None) -> str:
    """
    Carrega a logo em base64. Se diretorio_ensalamento for fornecido,
    procura a logo no diretório do arquivo de ensalamento.
    Se não fornecido, usa a variável global _diretorio_ensalamento se disponível.
    Caso contrário, usa o caminho padrão.
    """
    # Usa o parâmetro fornecido ou a variável global
    diretorio = diretorio_ensalamento or _diretorio_ensalamento
    
    if diretorio:
        # Lista de nomes possíveis para a logo
        nomes_logo = ['logo.png', 'logo.jpg', 'logo.jpeg', 'idib.png', 'idib.jpg', 'idib.jpeg']
        
        # Procura a logo no diretório do ensalamento
        for nome_logo in nomes_logo:
            caminho_logo = os.path.join(diretorio, nome_logo)
            if os.path.exists(caminho_logo):
                return carregar_imagem_base64(caminho_logo)
        
        # Se não encontrou, usa o caminho padrão
        return carregar_imagem_base64('assets/logo.png')
    
    # Se não foi fornecido diretório, usa o caminho padrão
    return carregar_imagem_base64('assets/logo.png')

def get_edital_base64(diretorio_ensalamento: str = None) -> str:
    """
    Carrega a logo do edital em base64. Se diretorio_ensalamento for fornecido,
    procura a logo do edital no diretório do arquivo de ensalamento.
    Se não fornecido, usa a variável global _diretorio_ensalamento se disponível.
    Caso contrário, usa o caminho padrão.
    """
    # Usa o parâmetro fornecido ou a variável global
    diretorio = diretorio_ensalamento or _diretorio_ensalamento
    
    if diretorio:
        # Lista de nomes possíveis para a logo do edital
        nomes_edital = ['edital.png', 'edital.jpg', 'edital.jpeg', 'logo_edital.png', 
                        'logo_edital.jpg', 'logo_edital.jpeg', 'habilitacaoSargento.jpg',
                        'habilitacaoSargento.png']
        
        # Procura a logo do edital no diretório do ensalamento
        for nome_edital in nomes_edital:
            caminho_edital = os.path.join(diretorio, nome_edital)
            if os.path.exists(caminho_edital):
                return carregar_imagem_base64(caminho_edital)
        
        # Se não encontrou, usa o caminho padrão
        return carregar_imagem_base64('assets/habilitacaoSargento.jpg')
    
    # Se não foi fornecido diretório, usa o caminho padrão
    return carregar_imagem_base64('assets/habilitacaoSargento.jpg')


def safe_filename(name: str) -> str:
    """
    Transforma uma string em um nome seguro para arquivos/pastas no Windows/Linux.
    Remove caracteres inválidos e espaços extras.
    """
    # Remove caracteres proibidos
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Substitui múltiplos espaços por um só
    name = re.sub(r'\s+', ' ', name)
    # Remove espaços do início e fim
    return name.strip()

def normalizar_cpf(valor) -> str:
    """
    Retorna o CPF apenas com dígitos, com 11 posições.
    Planilhas costumam trazer o campo como número, o que adiciona o sufixo
    '.0' e remove os zeros à esquerda.
    """
    texto = re.sub(r'\.0+$', '', str(valor).strip())
    digitos = re.sub(r'\D', '', texto)

    if not digitos:
        return ''

    return digitos.zfill(11)


def definir_horarios(row):
    concurso = row['CONCURSO']
    cargo = row['CARGO']

    if 'EDITAL 01' in concurso:
        if 'NÍVEL MÉDIO' in cargo.upper():
            return '15h', '19h'
        else:
            return '15h', '20h'
    elif 'EDITAL 02' in concurso:
        return '08h', '12h'
    elif 'EDITAL 03' in concurso:
        return '15h', '20h'
    else:
        return None, None


def normalizar_dia_turno(dia: str, turno: str, data_prova=None) -> tuple[str, str]:
    """
    Normaliza o texto de dia/turno para exibição:
    - MADRUGADA -> MANHÃ
    - SABADO/DOMINGO -> data da prova (dd/mm), quando disponível
    """
    dia_fmt = str(dia or "").strip()
    turno_fmt = str(turno or "").strip().upper()

    if turno_fmt == "MADRUGADA":
        turno_fmt = "MANHÃ"

    data_fmt = ""
    if data_prova is not None and data_prova != "":
        if hasattr(data_prova, "strftime"):
            data_fmt = data_prova.strftime("%d/%m")
        else:
            texto_data = str(data_prova).strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    data_fmt = datetime.strptime(texto_data, fmt).strftime("%d/%m")
                    break
                except ValueError:
                    continue

    if dia_fmt.upper() in {"SABADO", "SÁBADO", "DOMINGO"} and data_fmt:
        dia_fmt = data_fmt

    return dia_fmt, turno_fmt