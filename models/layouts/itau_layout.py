import re
from datetime import datetime
from models.layouts.base_layout import BaseLayout


class ItauLayoutModel(BaseLayout):
    """
    Layout responsável por interpretar extrato do Itaú.

    NÃO faz reconhecimento.
    NÃO lê PDF.
    Apenas transforma texto já extraído em estrutura padronizada.
    """

    tipo_documento = "extrato_bancario"

    # =====================================================
    # PARSE PRINCIPAL
    # =====================================================

    def parse(self, texto: str) -> list:
        lancamentos = []

        if not texto:
            return lancamentos

        linhas = texto.split("\n")

        for linha in linhas:
            linha = linha.strip()

            if not linha:
                continue

            if self._linha_ignorada(linha):
                continue

            lanc = self._parse_linha(linha)

            if lanc:
                lancamentos.append(lanc)

        return lancamentos

    # =====================================================
    # FILTRO DE LINHAS
    # =====================================================

    def _linha_ignorada(self, linha: str) -> bool:
        linha_upper = linha.upper()

        palavras_ignorar = [
            "SALDO DO DIA",
            "SALDO ANTERIOR",
            "POSIÇÃO CONSOLIDADA",
            "ITAU",
            "AGÊNCIA",
            "CONTA",
            "EXTRATO",
        ]

        return any(p in linha_upper for p in palavras_ignorar)

    # =====================================================
    # PARSE DE CADA LINHA
    # =====================================================

    def _parse_linha(self, linha: str) -> dict | None:
        """
        Suporta padrões reais Itaú:

        01/01/2024 DESCRICAO QUALQUER -123,45
        01/01/2024 DESCRICAO QUALQUER 123,45
        01/01/2024 DESCRICAO QUALQUER -123,45 1.500,00
        """

        padrao = re.match(
            r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})(?:\s+\d{1,3}(?:\.\d{3})*,\d{2})?$",
            linha
        )

        if not padrao:
            return None

        data_raw, descricao_raw, valor_raw = padrao.groups()

        data = self._parse_data(data_raw)
        if not data:
            return None

        valor = self._parse_valor(valor_raw)

        return {
            "Data": data,
            "Descricao": descricao_raw.strip(),
            "Valor": valor,
        }

    # =====================================================
    # CONVERSÕES
    # =====================================================

    def _parse_data(self, data_str: str) -> str | None:
        try:
            return datetime.strptime(
                data_str,
                "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
        except Exception:
            return None

    def _parse_valor(self, valor_str: str) -> float:
        valor_str = valor_str.replace(".", "").replace(",", ".")
        return float(valor_str)