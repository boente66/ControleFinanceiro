import re
from datetime import datetime


class DataniLayoutModel:
    """
    Layout responsável por interpretar exportação do sistema Datani.

    NÃO reconhece documento.
    NÃO lê PDF.
    NÃO categoriza.
    Apenas converte texto em estrutura padronizada.
    """

    tipo_documento = "exportacao_sistema"

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
        linha_lower = linha.lower()

        # Ignorar cabeçalhos
        if "data" in linha_lower and "categoria" in linha_lower:
            return True

        if "descrição" in linha_lower:
            return True

        return False

    # =====================================================
    # PARSE DE LINHA
    # =====================================================

    def _parse_linha(self, linha: str) -> dict | None:
        """
        Suporta formatos como:

        10/06/2025 Salário 310,31 C Fontes de renda:Salário
        10/06/2025 Compra (26,89) D Alimentação:Restaurante
        """

        padrao = re.match(
            r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\(?-?\d+[.,]\d{2}\)?)\s+([DC])?\s+(.+)$",
            linha
        )

        if not padrao:
            return None

        data_raw, descricao, valor_raw, tipo_dc, categoria_raw = padrao.groups()

        data = self._parse_data(data_raw)
        valor = self._parse_valor(valor_raw)

        # Ajuste sinal pelo C/D (se existir)
        if tipo_dc:
            if tipo_dc == "D":
                valor = -abs(valor)
            elif tipo_dc == "C":
                valor = abs(valor)

        categoria_raw = categoria_raw.strip()

        # Remove C ou D perdido no início da categoria
        categoria_raw = re.sub(r"^[DC]\s+", "", categoria_raw)

        categoria_pai, subcategoria = self._parse_categoria(categoria_raw)

        return {
            "Data": data,
            "Descricao": descricao.strip(),
            "Valor": valor,
            "CategoriaPai": categoria_pai,
            "Subcategoria": subcategoria,
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
        """
        Suporta:
        310,31
        -26,89
        (26,89)
        """

        valor_str = valor_str.strip()

        negativo = False

        # Detecta valor entre parênteses
        if valor_str.startswith("(") and valor_str.endswith(")"):
            negativo = True
            valor_str = valor_str[1:-1]

        # Remove separador de milhar
        valor_str = valor_str.replace(".", "").replace(",", ".")

        try:
            valor = float(valor_str)
        except ValueError:
            return 0.0

        if negativo:
            valor = -abs(valor)

        return valor

    # =====================================================
    # TRATAMENTO DE CATEGORIA
    # =====================================================

    def _parse_categoria(self, categoria_str: str):

        categoria_str = categoria_str.strip()

        # Não automatiza transferência — apenas interpreta
        if "<transferencia>" in categoria_str.lower():
            return "Transferência", None

        # Categoria multinível: Pai:Sub:Sub2
        if ":" in categoria_str:
            partes = [p.strip() for p in categoria_str.split(":")]

            categoria_pai = partes[0]
            subcategoria = ":".join(partes[1:]) if len(partes) > 1 else None

            return categoria_pai, subcategoria

        return categoria_str, None