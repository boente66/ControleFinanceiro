import re

from models.layouts.banco_brasil_layout import BancoBrasilLayoutModel
from models.layouts.bradesco_layout import BradescoLayoutModel
from models.layouts.itau_layout import ItauLayoutModel
from models.layouts.datani_layout import DataniLayoutModel


class ReconhecimentoService:
    """
    Serviço responsável apenas por decidir qual layout utilizar.

    NÃO lê arquivo.
    NÃO faz parsing.
    NÃO categoriza.

    Apenas decide qual layout deve interpretar o texto.
    """

    def __init__(self):
        self.itau_layout = ItauLayoutModel()
        self.bb_layout = BancoBrasilLayoutModel()
        self.bradesco_layout = BradescoLayoutModel()
        self.datani_layout = DataniLayoutModel()

    # ======================================================
    # MÉTODO PRINCIPAL
    # ======================================================
    def reconhecer_layout(self, texto: str):

        if not texto:
            return None

        texto_lower = texto.lower()

        # --------------------------------------------------
        # ORDEM IMPORTA
        # Mais específico primeiro
        # --------------------------------------------------

        # 🔹 Exportação de sistema (Datani ou similares)
        if self._is_exportacao_sistema(texto_lower):
            return self.datani_layout

        # 🔹 Bancos
        if self._is_itau(texto_lower):
            return self.itau_layout

        if self._is_banco_do_brasil(texto_lower):
            return self.bb_layout

        if self._is_bradesco(texto_lower):
            return self.bradesco_layout

        return None

    # ======================================================
    # REGRAS DE RECONHECIMENTO
    # ======================================================

    # ------------------------------------------------------
    # EXPORTAÇÃO DE SISTEMA (Datani / Sistema interno)
    # ------------------------------------------------------
    def _is_exportacao_sistema(self, texto):

        # Presença clara de coluna Categoria
        if "categoria" in texto and "descrição" in texto:
            return True

        # Estrutura Categoria: Subcategoria
        if re.search(r"\b\w+\s*:\s*\w+", texto):
            return True

        # Marcação explícita de transferência
        if "<transferencia>" in texto:
            return True

        return False

    # ------------------------------------------------------
    # ITAÚ
    # ------------------------------------------------------
    def _is_itau(self, texto):

        # Marca explícita
        if "itaú" in texto or "itau" in texto:
            return True

        linhas = texto.split("\n")

        for linha in linhas[:40]:

            linha = linha.strip()

            if re.match(
                r"\d{2}/\d{2}/\d{4}\s+.+\s+-?\d+[.,]\d{2}(\s+\d+[.,]\d{2})?$",
                linha
            ):
                # Itaú normalmente NÃO usa D/C no final
                if not linha.endswith((" D", " C")):
                    return True

        return False

    # ------------------------------------------------------
    # BANCO DO BRASIL
    # ------------------------------------------------------
    def _is_banco_do_brasil(self, texto):

        if "banco do brasil" in texto:
            return True

        linhas = texto.split("\n")

        for linha in linhas[:40]:

            linha = linha.strip()

            if re.search(
                r"\d{2}/\d{2}/\d{4}\s+.+\s+-?\d+[.,]\d{2}\s+[DC]$",
                linha
            ):
                return True

        return False

    # ------------------------------------------------------
    # BRADESCO
    # ------------------------------------------------------
    def _is_bradesco(self, texto):

        if "bradesco" in texto or "next" in texto:
            return True

        linhas = texto.split("\n")

        for linha in linhas[:40]:

            linha = linha.strip()

            if re.search(
                r"\d{2}/\d{2}/\d{4}.*R?\$?\s*-?\d+[.,]\d{2}",
                linha
            ):
                return True

        return False
