import os
import uuid


def _caminho_absoluto(path: str) -> str:
    return os.path.abspath(os.path.normpath(path))


def _caminho_windows_estendido(path: str) -> str:
    """Prefixo \\\\?\\ para ultrapassar o limite de 260 caracteres no Windows."""
    path = _caminho_absoluto(path)
    if os.name != "nt" or path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


class PDFExporter:
    def __init__(self):
        self.playwright = None
        self.browser = None

    def _prepare_html(self, html_content: str) -> str:
        """
        Garante que o HTML tenha DOCTYPE, <html>, <head> com charset UTF-8
        e evita duplicar meta charset em conteúdos que já o possuem.
        """
        content_lower = html_content.lower()

        # Caso o template já tenha <html> definido
        if "<html" in content_lower:
            if "charset" in content_lower:
                return html_content

            # injeta meta charset logo após a tag <head>
            head_index = content_lower.find("<head")
            if head_index != -1:
                close_head_tag_index = content_lower.find(">", head_index)
                if close_head_tag_index != -1:
                    insert_at = close_head_tag_index + 1
                    return (
                        html_content[:insert_at]
                        + '\n<meta charset="utf-8">\n'
                        + html_content[insert_at:]
                    )

            # se não achou <head>, apenas insere meta no começo
            return '<meta charset="utf-8">\n' + html_content

        # Conteúdo sem <html>: montamos um documento completo
        has_body = "<body" in content_lower
        meta = '<meta charset="utf-8">'

        if has_body:
            # já tem <body>, apenas criamos o envelope HTML
            return (
                "<!DOCTYPE html>\n"
                '<html lang="pt-BR">\n'
                "<head>\n"
                f"{meta}\n"
                "</head>\n"
                f"{html_content}\n"
                "</html>\n"
            )

        # fragmento puro: criamos <body> também
        return (
            "<!DOCTYPE html>\n"
            '<html lang="pt-BR">\n'
            "<head>\n"
            f"{meta}\n"
            "</head>\n"
            "<body>\n"
            f"{html_content}\n"
            "</body>\n"
            "</html>\n"
        )

    def __enter__(self):
        from playwright.sync_api import sync_playwright, Error as PlaywrightError

        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.launch(headless=True)
        except PlaywrightError as exc:
            # garante que recursos sejam liberados antes de propagar o erro
            self.close()
            raise RuntimeError(
                "Falha ao iniciar o navegador do Playwright. "
                "Provavelmente os navegadores não estão instalados. "
                "No terminal do ambiente virtual execute: "
                "\"playwright install chromium\"."
            ) from exc

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def exportar(self, html_content: str, output_path: str, deitado: bool = False, etiqueta: bool = False, pessoal: bool = False):
        # normaliza o HTML para um documento completo em UTF-8
        html_content = self._prepare_html(html_content)

        output_path = _caminho_absoluto(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        temp_path = os.path.join(
            os.path.dirname(output_path),
            f"temp_{uuid.uuid4().hex}.html",
        )
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        pdf_path = _caminho_windows_estendido(output_path)

        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            f.flush()
            os.fsync(f.fileno())

        page = self.browser.new_page()

        # aumentar timeout (60s ou mais)
        temp_url = temp_path.replace("\\", "/")
        page.goto(f"file:///{temp_url}", wait_until="load", timeout=120000)
        if etiqueta:
            page.pdf(
                path=pdf_path,
                width='216mm',
                height='216mm' if not pessoal else '108mm',
                print_background=True,
            )
        else:
            page.pdf(
                path=pdf_path,
                format="A4",
                landscape=deitado,
                print_background=True,
            )
        page.close()

        # remove o html temporário
        os.remove(temp_path)

    def close(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
