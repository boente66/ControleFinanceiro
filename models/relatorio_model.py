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
            SELECT 
                t.Data,
                c.Nome AS Categoria,
                SUM(CASE WHEN t.Valor > 0 THEN t.Valor ELSE 0 END) AS Receita,
                SUM(CASE WHEN t.Valor < 0 THEN ABS(t.Valor) ELSE 0 END) AS Despesa,
                SUM(t.Valor) AS Economia
            FROM transacoes t
            LEFT JOIN categorias c ON c.ID_Categoria = t.ID_Categoria
            WHERE date(t.Data) >= date('now', ?)
              AND t.ID_Usuario = ?
            GROUP BY t.Data, c.Nome
            ORDER BY t.Data DESC
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
            SELECT 
                strftime('%m', t.Data) AS Mes,
                c.Nome AS Categoria,
                SUM(CASE WHEN LOWER(t.Tipo) = 'receita' THEN t.Valor ELSE 0 END) AS Receita,
                SUM(CASE WHEN LOWER(t.Tipo) = 'despesa' THEN ABS(t.Valor) ELSE 0 END) AS Despesa,
                SUM(t.Valor) AS Economia
            FROM transacoes t
            LEFT JOIN categorias c ON c.ID_Categoria = t.ID_Categoria
            WHERE strftime('%Y', t.Data) = ?
              AND t.ID_Usuario = ?
            GROUP BY Mes, c.Nome
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
            SELECT *
            FROM transacoes
            WHERE strftime('%Y', Data) = ?
              AND ID_Usuario = ?
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
            SELECT 
                f.Nome AS Fonte,
                f.CNPJ,
                SUM(t.Valor) AS Valor
            FROM transacoes t
            JOIN favorecido f ON t.ID_Favorecido = f.ID_Favorecido
            WHERE strftime('%Y', t.Data) = ?
              AND LOWER(t.Tipo) = 'receita'
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
            SELECT 
                f.Nome AS Fonte,
                f.CNPJ,
                SUM(t.Valor) AS Valor
            FROM transacoes t
            JOIN favorecido f ON t.ID_Favorecido = f.ID_Favorecido
            WHERE strftime('%Y', t.Data) = ?
              AND LOWER(t.Tipo) = 'despesa'
              AND t.ID_Usuario = ?
            GROUP BY f.Nome, f.CNPJ
            """
            return self.fetch_all(query, (str(ano), id_usuario)) or []
        except sqlite3.Error:
            return []