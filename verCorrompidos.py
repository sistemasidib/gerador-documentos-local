import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyPDF2 import PdfReader
from tqdm import tqdm

caracteres = [
    '‡',
    'ƒ',
    '‰'
]

def pdf_contem_caractere(caminho_pdf, caractere='‰'):
    """Verifica se o PDF contém o caractere especificado."""
    try:
        leitor = PdfReader(caminho_pdf)
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ""
            if caractere in texto:
                return caminho_pdf  # retorna caminho se encontrou
    except Exception:
        pass
    return None


def encontrar_pdfs_com_caractere(diretorio_base, caractere='‰'):
    """Percorre todas as pastas e subpastas e lista PDFs com o caractere."""
    if not os.path.exists(diretorio_base):
        print(f"[AVISO] Diretório não encontrado: {diretorio_base}")
        return

    print(f"\n🔍 Verificando diretório: {diretorio_base}")

    # Coleta todos os PDFs
    pdfs = []
    for raiz, _, arquivos in os.walk(diretorio_base):
        for arquivo in arquivos:
            if arquivo.lower().endswith(".pdf"):
                pdfs.append(os.path.join(raiz, arquivo))

    total_pdfs = len(pdfs)
    if total_pdfs == 0:
        print("Nenhum PDF encontrado.")
        return

    print(f"📄 {total_pdfs} PDFs encontrados. Iniciando verificação...\n")

    encontrados = []
    with ProcessPoolExecutor() as executor:
        futuros = {executor.submit(pdf_contem_caractere, pdf, caractere): pdf for pdf in pdfs}
        for futuro in tqdm(as_completed(futuros), total=total_pdfs, desc="Analisando PDFs", ncols=80):
            resultado = futuro.result()
            if resultado:
                print(f"✅ Encontrado em: {resultado}")
                encontrados.append(resultado)

    print(f"\n🔎 Total encontrados: {len(encontrados)}")

    if encontrados:
        with open("pdfs_com_caractere.txt", "w", encoding="utf-8") as f:
            for item in encontrados:
                f.write(item + "\n")
        print("📁 Lista salva em: pdfs_com_caractere.txt")


if __name__ == "__main__":
    # Proteção obrigatória no Windows para multiprocessing
    editais = [
        # 'JEQUIE 1',
        # 'JEQUIE 3',
        'FEIRA DE SANTANA - PEDAGOGO',
        # 'JEQUIE 2',
    ]

    for edital in editais:
        encontrar_pdfs_com_caractere(f'concursos/{edital}/docs')

