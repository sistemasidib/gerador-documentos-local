from jinja2 import Environment, FileSystemLoader


COMPONENTES_DIR = 'templates/componentes/header'
HEADER_DIR = 'header.html'

def gerar_header (
        edital_logo_path: str,
        instituto_logo_path: str,
        edital: str,
        nome_arquivo: str
 ) -> str:
    env = Environment(loader=FileSystemLoader(COMPONENTES_DIR))
    header = env.get_template(HEADER_DIR)

    header_html = header.render(
        edital_logo=edital_logo_path,
        instituto_logo=instituto_logo_path,
        edital=edital,
        nome_arquivo=nome_arquivo
    )

    return header_html