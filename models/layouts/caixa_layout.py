import re
from datetime import datetime
from models.layouts.base_layout import BaseLayout


class CaixaLayoutModel(BaseLayout):
    """
    Layout responsável por interpretar extrato da Caixa Econômica Federal.

    NÃO reconhece banco.
    NÃO lê PDF.
    Apenas transforma texto em estrutura padronizada.
    """

    tipo_documento = "extrato_bancario"

    # =====================================================
    # PARSE PRINCIPAL
    # =====================================================

    def parse(self, texto: str) -> list:
        lancamentos = []

        if not texto:
            return lancamentos

        for linha in texto.split("\n"):
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
            "AGÊNCIA",
            "CONTA",
            "CAIXA ECONÔMICA",
            "EXTRATO"
        ]

        return any(p in linha_upper for p in palavras_ignorar)

    # =====================================================
    # PARSE DE CADA LINHA
    # =====================================================

    def _parse_linha(self, linha: str) -> dict | None:
        """
        Suporta padrões como:

        01/02/2024 DESCRICAO QUALQUER 1.234,56 C
        01/02/2024 DESCRICAO QUALQUER 500,00 D
        01/02/2024 DESCRICAO QUALQUER 150,00
        """

        padrao = re.match(
            r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})(?:\s*([CD]))?$",
            linha
        )

        if not padrao:
            return None

        data_raw, descricao_raw, valor_raw, tipo_cd = padrao.groups()

        data = self._parse_data(data_raw)
        if not data:
            return None

        valor = self._parse_valor(valor_raw)

        # Se houver D/C explícito
        if tipo_cd:
            if tipo_cd.upper() == "D":
                valor = -abs(valor)
            else:
                valor = abs(valor)

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
                data_str, "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
        except Exception:
            return None

    def _parse_valor(self, valor_str: str) -> float:
        valor_str = valor_str.replace(".", "").replace(",", ".")
        return float(valor_str)