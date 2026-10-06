import fitz  # PyMuPDF
import os
import shutil

from utils.limpar_terminal import clear_terminal

def verificar_identificacao_sala(page):
    """Verifica se a página contém 'IDENTIFICAÇÃO DE SALA'"""
    try:
        text = page.get_text()
        return "IDENTIFICAÇÃO DE SALA" in text.upper()
    except:
        return False

def processar_todos_pdfs(edital: str):
    """Processa todos os PDFs da pasta discursiva e salva em discursivas_a3"""
    pasta_entrada = f"concursos/{edital}/docs/discursiva"
    pasta_saida = f"concursos/{edital}/docs/discursivas_a3"
    
    if os.path.exists(pasta_saida):
        shutil.rmtree(pasta_saida)
    os.makedirs(pasta_saida)
    
    for item in os.listdir(pasta_entrada):
        caminho_item = os.path.join(pasta_entrada, item)
        
        if os.path.isdir(caminho_item):
            print(f"Processando pasta: {item}")
            
            pasta_saida_item = os.path.join(pasta_saida, item)
            os.makedirs(pasta_saida_item)
            
            for arquivo in os.listdir(caminho_item):
                if arquivo.lower().endswith('.pdf'):
                    caminho_pdf_entrada = os.path.join(caminho_item, arquivo)
                    nome_arquivo_saida = arquivo  
                    caminho_pdf_saida = os.path.join(pasta_saida_item, nome_arquivo_saida)
                    
                    print(f"  Processando: {arquivo}")
                    try:
                        juntar_em_a3(caminho_pdf_entrada, caminho_pdf_saida)
                        print(f"  ✓ Concluído: {nome_arquivo_saida}")
                    except Exception as e:
                        print(f"  ✗ Erro ao processar {arquivo}: {e}")
    
    print(f"\nProcessamento concluído! Arquivos salvos em: {pasta_saida}")

def juntar_em_a3(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    
    total_paginas = len(doc)
    
    a4_width = 595
    a4_height = 842
    a3_width = a4_width * 2
    a3_height = a4_height
    
    new_doc = fitz.open()
    
    for i in range(total_paginas):
        page = new_doc.new_page(width=a3_width, height=a3_height)
        
        page_a4 = doc[i]
        rect = fitz.Rect(a3_width - a4_width, 0, a3_width, a4_height)
        page.show_pdf_page(rect, doc, i)
        
        if verificar_identificacao_sala(page_a4):
            print(f"Página {i+1} contém 'IDENTIFICAÇÃO DE SALA' - adicionando folha em branco")
            blank_page = new_doc.new_page(width=a3_width, height=a3_height)
    
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()


editais = [
    'BombeirosDF geral duplicados',
    'BombeirosDF SAUDE duplicado',
]

for edital in editais:
    clear_terminal()
    print(f"Gerando documentos do edital: {edital}")
    print()
    processar_todos_pdfs(edital)