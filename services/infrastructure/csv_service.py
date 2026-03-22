# infrastructure/csv_service.py

import pandas as pd


class CsvService:

    def ler(self, caminho_csv: str):
        if not caminho_csv:
            raise ValueError("Arquivo CSV não informado.")

        return pd.read_csv(caminho_csv)