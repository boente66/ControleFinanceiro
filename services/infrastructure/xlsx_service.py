# infrastructure/xlsx_service.py

import pandas as pd


class XlsxService:

    def ler(self, caminho_xlsx: str):
        if not caminho_xlsx:
            raise ValueError("Arquivo XLSX não informado.")

        return pd.read_excel(caminho_xlsx)