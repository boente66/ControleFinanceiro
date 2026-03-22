class BaseLayout:
    """
    Classe base para todos os layouts de importação.
    Define contrato obrigatório.
    """

    tipo_documento = "extrato_bancario"  # padrão

    def parse(self, texto: str) -> list:
        """
        Deve retornar lista de dict no padrão:

        [
            {
                "Data": "YYYY-MM-DD",
                "Descricao": "...",
                "Valor": float,
                # Opcional:
                "CategoriaPai": str,
                "Subcategoria": str
            }
        ]
        """
        raise NotImplementedError(
            "Layout deve implementar método parse()"
        )