# models/ia_aprendizado_model.py

class IAAprendizadoModel:
    """
    Modelo responsável por sugerir categorias com base em descrição.
    Evolutivo: pode futuramente aprender com histórico do usuário.
    """

    def __init__(self):
        # regras iniciais (heurística)
        self.regras = [
            (["salário", "provento", "pagamento", "contracheque"], "Renda", "Receita"),
            (["supermercado", "mercado", "carrefour", "atacad"], "Alimentação", "Despesa"),
            (["farmácia", "droga", "drogaria"], "Saúde", "Despesa"),
            (["aluguel", "locação"], "Moradia", "Despesa"),
            (["luz", "energia"], "Energia", "Despesa"),
            (["água", "saneamento"], "Água", "Despesa"),
            (["internet", "claro", "vivo", "tim", "oi"], "Internet", "Despesa"),
            (["pix", "ted", "doc", "transferência"], "Transferência", "Despesa"),
        ]

    def sugerir_categoria(self, descricao: str):
        """
        Retorna:
            (categoria, tipo, confianca)
        """
        if not descricao:
            return "Outros", "Despesa", 0.1

        texto = descricao.lower()

        for palavras, categoria, tipo in self.regras:
            for p in palavras:
                if p in texto:
                    return categoria, tipo, 0.85

        return "Outros", "Despesa", 0.3