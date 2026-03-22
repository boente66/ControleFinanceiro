from database.database import Database
import sqlite3

class RelatorioModel(Database):
    def __init__(self):
        super().__init__()

    # -------------------------
    # RELATÓRIO DIÁRIO
    # -------------------------
    def get_relatorio_diario(self, dias, id_usuario):
        try:
            query = """
            SELECT Data, Categoria,
                   SUM(CASE WHEN Valor > 0 THEN Valor ELSE 0 END) AS Receita,
                   SUM(CASE WHEN Valor < 0 THEN ABS(Valor) ELSE 0 END) AS Despesa,
                   SUM(Valor) AS Economia
            FROM transacoes
            WHERE date(Data) >= date('now', ?)
              AND ID_Usuario = ?
            GROUP BY Data, Categoria
            ORDER BY Data DESC
            """
            return self.fetch_all(query, (f'-{dias} days', id_usuario)) or []
        except sqlite3.Error:
            return []

    # -------------------------
    # RELATÓRIO ANUAL
    # -------------------------
    def get_relatorio_anual(self, ano, id_usuario):
        try:
            query = """
            SELECT strftime('%m', Data) AS Mes, Categoria,
                   SUM(CASE WHEN Tipo='Receita' THEN Valor ELSE 0 END) AS Receita,
                   SUM(CASE WHEN Tipo='Despesa' THEN Valor ELSE 0 END) AS Despesa,
                   SUM(Valor) AS Economia
            FROM transacoes
            WHERE strftime('%Y', Data) = ? AND ID_Usuario = ?
            GROUP BY Mes, Categoria
            ORDER BY Mes
            """
            return self.fetch_all(query, (str(ano), id_usuario)) or []
        except sqlite3.Error:
            return []

    # -------------------------
    # INFORME COMPLETO (Receita Federal)
    # -------------------------
    def get_transacoes_ano(self, ano, id_usuario):
        try:
            query = """
            SELECT * FROM transacoes
            WHERE strftime('%Y', Data) = ? AND ID_Usuario = ?
            """
            return self.fetch_all(query, (str(ano), id_usuario)) or []
        except sqlite3.Error:
            return []

    # -------------------------
    # RENDIMENTOS (PJ)
    # -------------------------
    def get_informe_rendimentos(self, ano, id_usuario):
        try:
            query = """
            SELECT f.Nome AS Fonte,
                   f.CNPJ,
                   SUM(t.Valor) AS Valor
            FROM transacoes t
            JOIN favorecido f ON t.ID_Favorecido = f.ID_Favorecido
            WHERE strftime('%Y', t.Data) = ?
              AND t.Tipo = 'Receita'
              AND t.ID_Usuario = ?
            GROUP BY f.Nome, f.CNPJ
            """
            return self.fetch_all(query, (str(ano), id_usuario)) or []
        except sqlite3.Error:
            return []

    # -------------------------
    # GASTOS (PF + PJ)
    # -------------------------
    def get_informe_gastos(self, ano, id_usuario):
        try:
            query = """
            SELECT f.Nome AS Fonte,
                   f.CNPJ,
                   SUM(t.Valor) AS Valor
            FROM transacoes t
            JOIN favorecido f ON t.ID_Favorecido = f.ID_Favorecido
            WHERE strftime('%Y', t.Data) = ?
              AND t.Tipo = 'Despesa'
              AND t.ID_Usuario = ?
            GROUP BY f.Nome, f.CNPJ
            """
            return self.fetch_all(query, (str(ano), id_usuario)) or []
        except sqlite3.Error:
            return []