# -*- coding: utf-8 -*-
from database.database import Database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionModel(Database):

    def __init__(self):
        super().__init__()

    # ============================================================
    # CREATE
    # ============================================================
    def add_transaction(self, dados: dict):
        sql = """
            INSERT INTO transacoes (
                ID_Conta,
                Descricao,
                Valor,
                Data,
                Tipo,
                ID_Categoria,
                ID_Favorecido,
                Notas,
                ID_Usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Removido o argumento conn=conn para alinhar com sua nova Database
        self.execute_query(sql, (
            dados.get("ID_Conta"),
            dados["Descricao"],
            dados["Valor"],
            dados["Data"],
            dados["Tipo"],
            dados.get("ID_Categoria"),
            dados.get("ID_Favorecido"),
            dados.get("Notas"),
            dados["ID_Usuario"]
        ))

    # ============================================================
    # READ
    # ============================================================
    def get_transaction_by_id(self, id_transacao, id_usuario):
        return self.fetch_one("""
            SELECT * FROM transacoes 
            WHERE ID_Transacao = ? 
              AND ID_Usuario = ?
        """, (id_transacao, id_usuario))

    def get_transactions_by_account(self, id_conta, id_usuario):
        return self.fetch_all("""
            SELECT *
            FROM transacoes
            WHERE ID_Conta = ?
              AND ID_Usuario = ?
            ORDER BY date(Data) DESC, ID_Transacao DESC
        """, (id_conta, id_usuario))

    def get_transactions_by_account_periodo(
        self,
        id_conta,
        data_inicio,
        data_fim,
        id_usuario
    ):
        return self.fetch_all("""
            SELECT *
            FROM transacoes
            WHERE ID_Conta = ?
              AND ID_Usuario = ?
              AND date(Data) BETWEEN date(?) AND date(?)
            ORDER BY date(Data) DESC, ID_Transacao DESC
        """, (id_conta, id_usuario, data_inicio, data_fim))

    # ============================================================
    # UPDATE
    # ============================================================
    def update_transaction(self, id_transacao, dados, id_usuario):
        sql = """
            UPDATE transacoes
            SET
                Descricao = ?,
                Valor = ?,
                Data = ?,
                ID_Categoria = ?,
                ID_Favorecido = ?,
                Notas = ?
            WHERE ID_Transacao = ?
              AND ID_Usuario = ?
        """

        self.execute_query(sql, (
            dados["Descricao"],
            dados["Valor"],
            dados["Data"],
            dados.get("ID_Categoria"),
            dados.get("ID_Favorecido"),
            dados.get("Notas"),
            id_transacao,
            id_usuario
        ))

    # ============================================================
    # DELETE
    # ============================================================
    def delete_transaction(self, id_transacao, id_usuario):
        self.execute_query("""
            DELETE FROM transacoes
            WHERE ID_Transacao = ?
              AND ID_Usuario = ?
        """, (id_transacao, id_usuario))

    # ============================================================
    # MÉTODOS PARA METAS
    # ============================================================
    def somar_despesas_categoria_periodo(
        self,
        id_categoria,
        id_usuario,
        data_inicio=None,
        data_fim=None
    ):
        sql = """
            SELECT ABS(SUM(Valor)) AS total
            FROM transacoes
            WHERE ID_Categoria = ?
              AND ID_Usuario = ?
              AND Valor < 0
        """
        params = [id_categoria, id_usuario]

        if data_inicio and data_fim:
            sql += " AND date(Data) BETWEEN date(?) AND date(?)"
            params.extend([data_inicio, data_fim])

        resultado = self.fetch_one(sql, tuple(params))
        # Mantendo os nomes originais de retorno
        return float(resultado["total"] or 0)

    def somar_receitas_periodo(
        self,
        id_usuario,
        data_inicio=None,
        data_fim=None
    ):
        sql = """
            SELECT SUM(Valor) AS total
            FROM transacoes
            WHERE ID_Usuario = ?
              AND Valor > 0
        """
        params = [id_usuario]

        if data_inicio and data_fim:
            sql += " AND date(Data) BETWEEN date(?) AND date(?)"
            params.extend([data_inicio, data_fim])

        resultado = self.fetch_one(sql, tuple(params))
        return float(resultado["total"] or 0)

    # ============================================================
    # RESUMO E ANÁLISE (DASHBOARD)
    # ============================================================
    def get_resumo_financeiro(self, user_id):
        sql = """
            SELECT
                SUM(CASE WHEN Valor > 0 THEN Valor ELSE 0 END) AS Receitas,
                SUM(CASE WHEN Valor < 0 THEN ABS(Valor) ELSE 0 END) AS Despesas
            FROM transacoes
            WHERE ID_Usuario = ?
              AND strftime('%Y-%m', Data) = strftime('%Y-%m', 'now')
        """
        return self.fetch_one(sql, (user_id,))

    def get_analise_mensal(self, user_id):
        sql = """
            SELECT
                SUM(CASE WHEN Valor > 0 THEN Valor ELSE 0 END) AS Receitas,
                SUM(CASE WHEN Valor < 0 THEN ABS(Valor) ELSE 0 END) AS Despesas
            FROM transacoes
            WHERE ID_Usuario = ?
              AND strftime('%Y-%m', Data) = strftime('%Y-%m', 'now')
        """
        resultado = self.fetch_one(sql, (user_id,))
        
        receitas = float(resultado["Receitas"] or 0)
        despesas = float(resultado["Despesas"] or 0)

        # Retornando exatamente as chaves originais que você definiu
        return {
            "Saldo_Atual": receitas - despesas,
            "Receitas_A_Receber": receitas,
            "DespesasAPagar": despesas,
            "BalancoParaOMes": receitas - despesas
        }

