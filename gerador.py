import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from conjuntos import gerar_conjunto_discursiva_branco, gerar_controle
from models.bdFormatado import BdFormatado
from templates.cartao_resposta.cartao_resposta import gerar_cartao_resposta, gerar_cartao_resposta_branco
from templates.discursiva.discursiva import gerar_discursiva, gerar_discursiva_styles, gerar_folha_discursiva_branco
from utils.criptografia import mascarar_numero
from utils.pdfExporter import PDFExporter
from PyPDF2 import PdfMerger
import pandas as pd

from utils.utils import get_edital_base64, get_logo_base64

# trava global para escrita no terminal (pra não embaralhar prints)
print_lock = threading.Lock()


def remover_arquivo_com_retry(path: str, tentativas: int = 25, espera_s: float = 0.2):
    """
    Remove arquivo com retry para contornar lock temporário no Windows.
    """
    ultimo_erro = None
    espera_atual = espera_s
    for _ in range(tentativas):
        try:
            if os.path.exists(path):
                os.remove(path)
            return
        except (PermissionError, OSError) as exc:
            ultimo_erro = exc
            time.sleep(espera_atual)
            espera_atual = min(1.0, espera_atual * 1.25)

    if ultimo_erro is not None:
        raise ultimo_erro

def move_cursor(row, col=0):
    """move cursor para linha/coluna específicas"""
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


def clear_line():
    """limpa a linha atual"""
    sys.stdout.write("\033[K")
    sys.stdout.flush()


def _slug_texto(valor, max_len: int | None = None) -> str:
    texto = str(valor or "").strip().lower()
    texto = re.sub(r"\s+", "_", texto)
    texto = re.sub(r"[^a-z0-9_]", "", texto)
    texto = texto or "vazio"
    if max_len is not None and len(texto) > max_len:
        texto = texto[:max_len].rstrip("_") or "vazio"
    return texto


def _hora_da_escola(escola) -> str:
    if escola.salas and escola.salas[0].ensalados:
        return str(escola.salas[0].ensalados[0].candidato.cargo.hora_prova or "").strip()
    return ""


def _slug_horario(hora: str) -> str:
    hora = str(hora or "").strip()
    if not hora:
        return ""
    partes = hora.replace(".", ":").split(":")
    if len(partes) >= 2:
        hora = f"{partes[0]}_{partes[1]}"
    return _slug_texto(hora)


def _agrupar_escolas_por_horario(escolas):
    grupos: dict[str, list] = {}
    for escola in escolas:
        hora = _hora_da_escola(escola)
        grupos.setdefault(hora, []).append(escola)
    return grupos


def processar_escola(escola, edital, gerador, tipo, turno, out_dir, line_index, chunk_size=5,deitado: bool = False, etiqueta: bool = False, pessoal: bool = False):
    total = len(escola.salas)

    # status inicial
    with print_lock:
        move_cursor(line_index, 0)
        print(f"{escola.tag}: 0/{total}", end="")
        move_cursor(0, 0)

    chunk_paths = []
    # inclui dia/turno de origem para evitar colisões (ex.: MANHÃ x MADRUGADA)
    dia_origem = ""
    turno_origem = ""
    hora_origem = ""
    if escola.salas and escola.salas[0].ensalados:
        ensalado_ref = escola.salas[0].ensalados[0]
        dia_origem = _slug_texto(getattr(ensalado_ref, "dia", ""))
        turno_origem = _slug_texto(getattr(ensalado_ref, "turno", ""))
        hora_origem = _slug_horario(_hora_da_escola(escola))

    partes_slug = [
        str(escola.id),
        _slug_texto(escola.tag, max_len=40),
        dia_origem,
        turno_origem,
    ]
    if hora_origem:
        partes_slug.append(hora_origem)
    escola_slug = "_".join(p for p in partes_slug if p)
    path = os.path.abspath(os.path.join(out_dir, tipo, escola_slug))
    os.makedirs(path, exist_ok=True)

    with PDFExporter() as exporter:
        current_chunk = []
        chunk_i = 0

        for index, sala in enumerate(escola.salas, start=1):
            html = gerador(edital, escola, sala)
            current_chunk.append(html)

            # atualizar progresso
            with print_lock:
                move_cursor(line_index, 0)
                print(f"{escola.tag}: {index}/{total}", end="")
                move_cursor(0, 0)

            if len(current_chunk) >= chunk_size or index == total:
                html_concat = "".join(current_chunk)
                if html_concat:
                    chunk_file = os.path.join(path, f"chunk{chunk_i}.pdf")
                    exporter.exportar(html_concat, chunk_file, deitado, etiqueta, pessoal)
                    chunk_paths.append(chunk_file)
                    chunk_i += 1
                current_chunk = []

    # Sem conteúdo (ex.: escola sem redação/peça/discursiva) — não gera PDF vazio
    if not chunk_paths:
        try:
            if os.path.isdir(path) and not os.listdir(path):
                os.rmdir(path)
        except OSError:
            pass

        with print_lock:
            move_cursor(line_index, 0)
            clear_line()
            print(f"⏭️ Escola sem conteúdo: {escola.tag}")
            move_cursor(0, 0)
        return

    # juntar chunks em um único PDF
    final_pdf = os.path.join(path, f"escola_{escola.id}.pdf")
    merger = PdfMerger()
    for p in chunk_paths:
        merger.append(p)
    merger.write(final_pdf)
    merger.close()

    # apagar arquivos temporários
    for p in chunk_paths:
        remover_arquivo_com_retry(p)

    # mensagem final na mesma linha
    with print_lock:
        move_cursor(line_index, 0)
        clear_line()
        print(f"✅ Escola finalizada: {escola.tag}")
        move_cursor(0, 0)


def _executar_relatorios_grupo(
    escolas,
    edital,
    gerador,
    tipo,
    turno,
    out_dir="docs",
    max_workers=4,
    deitado: bool = False,
    etiqueta: bool = False,
    pessoal: bool = False,
):
    if not escolas:
        return

    print("\n" * (len(escolas) + 6))

    move_cursor(0, 0)
    clear_line()
    print(f"Relatórios {tipo} - {turno}:")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, escola in enumerate(escolas, start=1):
            futures.append(executor.submit(
                processar_escola,
                escola,
                edital,
                gerador,
                tipo,
                turno,
                out_dir,
                i + 1,
                deitado=deitado,
                etiqueta=etiqueta,
                pessoal=pessoal,
            ))

        for f in futures:
            f.result()

    move_cursor(len(escolas) + 5, 0)
    print("✅ Relatórios finalizados.")


def executar_relatorios(escolas, edital, gerador, tipo, turno, out_dir="docs", max_workers=4, deitado: bool = False, etiqueta: bool = False, pessoal: bool = False):
    """
    Executa relatórios em paralelo para várias escolas.
    Quando há mais de um horário no mesmo turno, gera pastas separadas por horário.
    """
    if not escolas:
        return

    grupos = _agrupar_escolas_por_horario(escolas)
    multi_horario = len(grupos) > 1

    for hora in sorted(grupos.keys()):
        escolas_grupo = grupos[hora]
        hora_slug = _slug_horario(hora)
        tipo_exec = tipo
        turno_exec = turno
        if multi_horario and hora_slug:
            tipo_exec = f"{tipo}/{turno}_{hora_slug}"
            turno_exec = f"{turno} — {hora}" if hora else turno

        _executar_relatorios_grupo(
            escolas_grupo,
            edital,
            gerador,
            tipo_exec,
            turno_exec,
            out_dir,
            max_workers=max_workers,
            deitado=deitado,
            etiqueta=etiqueta,
            pessoal=pessoal,
        )
    
def gerar_relatorios_controle_escola(db: BdFormatado, gerador, tipo: str, out_dir="docs", deitado: bool = False):
    print(f"Relatórios {tipo}...", end='\r')
    html = ''
    html += gerar_controle(db, gerador)

    path = f"./{out_dir}/controle/{tipo}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # cria apenas a pasta

    with PDFExporter() as exporter:
        exporter.exportar(html, path, deitado=deitado)
            
    print(f"Relatórios {tipo} gerado! ✅")


def gerar_relatorios_controle(db: BdFormatado, gerador, tipo: str, out_dir="docs", deitado: bool = False):
    print(f"Relatórios {tipo}...", end='\r')

    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()

    html = gerador(
        logo_64,
        edital_64,
        db
        )

    path = f"./{out_dir}/controle/{tipo}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # cria apenas a pasta

    with PDFExporter() as exporter:
        exporter.exportar(html, path, deitado=deitado)
            
    print(f"Relatórios {tipo} gerado! ✅")


def gerar_cartao_branco(db: BdFormatado,n_questoes: list[int], out_dir="docs") -> str:
    logo_64 = get_logo_base64()
    edital_64 = get_edital_base64()

    html = ''

    for questao in n_questoes:
        html += gerar_cartao_resposta_branco(
            edital_64,
            logo_64,
            db.edital.nome,
            questao
        )

    path = f"./{out_dir}/zerado/cartão_resposta.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # cria apenas a pasta

    with PDFExporter() as exporter:
        exporter.exportar(html, path)
            
    print(f"Relatórios cartão_resposta gerado! ✅")

    
def gerar_discursiva_branco(
    db: BdFormatado,
    edital_id: int,
    qtd_candidatos: int,
    qtd_questao: int,
    qtd_linhas_questao: int,
    qtd_linhas_redacao: int,
    qtd_linhas_peca: int,
    passo: int,
    out_dir="docs"
):
    
    html: str = gerar_discursiva_styles()

    for candidato in range(1 + passo, qtd_candidatos + 1 + passo):
        html += gerar_conjunto_discursiva_branco(
            db=db,
            id=int(str(edital_id) + "000" + str(candidato)),
            qtd_questao=qtd_questao,
            qtd_linhas_questao=qtd_linhas_questao,
            qtd_linhas_redacao=qtd_linhas_redacao,
            qtd_linhas_peca=qtd_linhas_peca
        )

    path = f"./{out_dir}/zerado/discursiva.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # cria apenas a pasta

    with PDFExporter() as exporter:
        exporter.exportar(html, path)
            
    print(f"Relatórios discursiva gerado! ✅")


def exportar_doc(html, tipo,out_dir = "docs", deitado: bool = False,):
    path = f"./{out_dir}/controle/{tipo}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # cria apenas a pasta

    with PDFExporter() as exporter:
        exporter.exportar(html, path, deitado=deitado)
            
    print(f"Relatórios {tipo} gerado! ✅")


# def exportar_com_codigo(df: pd.DataFrame, caminho_saida: str):
#     df['CODIGO'] = df['INSC'].apply(mascarar_numero)

#     # Exporta para Excel
#     df.to_excel(caminho_saida, index=False)
#     print(f"Arquivo exportado com sucesso para: {caminho_saida}")
#     return df

def exportar_com_codigo(df: pd.DataFrame, caminho_saida: str):
    if 'INSC' not in df.columns:
        raise ValueError(f"Coluna 'INSC' não encontrada! Colunas disponíveis: {df.columns.tolist()}")

    df['CODIGO'] = df['INSC'].apply(mascarar_numero)

    # 🔍 Mostra prévia antes de exportar
    print("Prévia do DataFrame resultante:")
    print(df.head())

    # 💾 Exporta para Excel
    df.to_excel(caminho_saida, index=False)
    print(f"Arquivo exportado com sucesso para: {caminho_saida}")
    return df
