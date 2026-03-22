# models/ia_export_model.py

import pandas as pd
from utilitarios.makepdf import MakePDF


class IAExportModel:
    """
    Model responsável SOMENTE por escrever arquivos.
    """

    def __init__(self):
        self.data = []

    def set_data(self, data: list):
        self.data = data

    def export_to_csv(self, file_path: str) -> bool:
        df = pd.DataFrame(self.data)
        df.to_csv(file_path, index=False)
        return True

    def export_to_xlsx(self, file_path: str) -> bool:
        df = pd.DataFrame(self.data)
        df.to_excel(file_path, index=False)
        return True

    def export_to_pdf(self, file_path: str, titulo: str) -> bool:
        MakePDF.exportar_tabela(self.data, titulo, file_path)
        return True
