import os
from services.infrastructure.pdf_service import PdfService


class ExtractorService:

    def __init__(self):
        self.pdf_service = PdfService()

    def extrair(self, caminho_arquivo: str):

        extensao = os.path.splitext(caminho_arquivo)[1].lower()

        if extensao == ".pdf":
            return self.pdf_service.ler_texto(caminho_arquivo)

        elif extensao == ".csv":
            try:
                import pandas as pd
            except ImportError as exc:
                raise RuntimeError(
                    "Dependência 'pandas' ausente. Instale o ambiente "
                    "completo para extrair arquivos CSV."
                ) from exc

            df = pd.read_csv(caminho_arquivo)
            return df.to_string(index=False)

        elif extensao in (".xlsx", ".xls"):
            try:
                import pandas as pd
            except ImportError as exc:
                raise RuntimeError(
                    "Dependência 'pandas' ausente. Instale o ambiente "
                    "completo para extrair arquivos XLSX."
                ) from exc

            df = pd.read_excel(caminho_arquivo)
            return df.to_string(index=False)

        elif extensao == ".txt":
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return f.read()

        else:
            raise ValueError("Formato não suportado.")
