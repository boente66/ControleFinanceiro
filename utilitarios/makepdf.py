from datetime import datetime
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader
import pytesseract
import pdf2image
import re


class MakePDF:
    """
    Classe de INFRAESTRUTURA para manipulação de PDF.

    Responsabilidades:
    - Ler PDF
    - Extrair texto
    - Aplicar OCR
    - Gerar PDF
    """

    # ==========================================================
    # LEITURA SIMPLES (PyPDF2)
    # ==========================================================
    @staticmethod
    def importar_pdf(caminho_arquivo):
        try:
            reader = PdfReader(caminho_arquivo)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
            return texto
        except Exception as e:
            print(f"Erro ao importar PDF: {e}")
            return None

    # ==========================================================
    # LEITURA AVANÇADA (pdfplumber + OCR)
    # ==========================================================
    @staticmethod
    def ler_pdf(caminho_arquivo):
        try:
            texto = ""

            with pdfplumber.open(caminho_arquivo) as pdf:
                for pagina in pdf.pages:

                    # Tenta extrair tabela
                    tabela = pagina.extract_table()
                    if tabela:
                        for linha in tabela:
                            if linha:
                                linha_formatada = "  ".join(
                                    str(c).strip() for c in linha if c
                                )
                                texto += linha_formatada + "\n"
                    else:
                        texto_bruto = pagina.extract_text()
                        if texto_bruto:
                            texto += texto_bruto + "\n"

            # Se não conseguiu extrair texto, tenta OCR
            if not texto.strip():
                imagens = pdf2image.convert_from_path(caminho_arquivo)
                for img in imagens:
                    texto += pytesseract.image_to_string(img, lang="por") + "\n"

            return texto.strip() or None

        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
            return None

    # ==========================================================
    # VISUALIZAÇÃO
    # ==========================================================
    @staticmethod
    def visualizar_pdf(caminho_arquivo):
        return MakePDF.importar_pdf(caminho_arquivo)

    # ==========================================================
    # GERAR PDF COM TEXTO
    # ==========================================================
    @staticmethod
    def gerar_pdf(caminho_arquivo, titulo, conteudo):
        try:
            c = canvas.Canvas(caminho_arquivo, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, titulo)

            c.setFont("Helvetica", 12)
            y = height - 80

            for linha in conteudo.split("\n"):
                c.drawString(50, y, linha)
                y -= 18
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            return True

        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False

    # ==========================================================
    # GERAR PDF SIMPLES A PARTIR DE LISTA
    # ==========================================================
    @staticmethod
    def create_pdf_from_data(data, file_path):
        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Relatório")

            c.setFont("Helvetica", 10)
            y = height - 80

            for item in data:
                c.drawString(50, y, str(item))
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            return True

        except Exception as e:
            print(f"Erro ao criar PDF: {e}")
            return False
