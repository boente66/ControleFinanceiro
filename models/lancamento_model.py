import logging
from datetime import datetime
from database.database import Database
from models.credito_model import CreditoModel

logger = logging.getLogger(__name__)


class LancamentoModel(Database):
    """
    Modelo responsável pelos lançamentos de cartão.
    A fatura é DERIVADA da coluna Data.
    """

    def __init__(self):
        super().__init__()
        self.credito = CreditoModel()

    # ============================================================
    # CRIAR LANÇAMENTO
    # ============================================================
    def add_lancamento(self, dados: dict) -> bool:

        obrigatorios = [
            "ID_Usuario",
            "ID_Cartao",
            "Descricao",
            "Valor",
            "Data",
        ]

        for campo in obrigatorios:
            if campo not in dados:
                raise ValueError(f"{campo} é obrigatório.")

        cartao = self.credito.get_cartao_by_id(
            dados["ID_Cartao"],
            dados["ID_Usuario"]
        )

        if not cartao:
            raise PermissionError("Cartão não pertence ao usuário.")

        data = dados["Data"]
        if not isinstance(data, str):
            data = data.strftime("%Y-%m-%d")

        sql = """
            INSERT INTO lancamentos (
                ID_Cartao,
                Data,
                Descricao,
                Valor,
                ID_Categoria,
                Parcelado,
                Num_Parcelas,
                Parcela_Atual,
                Paga,
                Notas,
                ID_Usuario,
                ID_Conta,
                ID_Transacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            dados["ID_Cartao"],
            data,
            dados["Descricao"],
            float(dados["Valor"]),
            dados.get("ID_Categoria"),
            int(dados.get("Parcelado", 0)),
            int(dados.get("Num_Parcelas", 1)),
            int(dados.get("Parcela_Atual", 1)),
            int(dados.get("Paga", 0)),
            dados.get("Notas"),
            dados["ID_Usuario"],
            dados.get("ID_Conta"),
            dados.get("ID_Transacao"),
        )

        self.execute_query(sql, params)
        return True

    # ============================================================
    # BUSCAR POR ID
    # ============================================================
    def get_lancamento_by_id(self, id_lancamento, id_usuario):
        sql = """
            SELECT *
            FROM lancamentos
            WHERE ID_Lancamento = ?
              AND ID_Usuario = ?
        """
        return self.fetch_one(sql, (id_lancamento, id_usuario))

    # ============================================================
    # ATUALIZAR
    # ============================================================
    def update_lancamento(self, id_lancamento, dados, id_usuario):

        sql = """
            UPDATE lancamentos
            SET Descricao = ?,
                Valor = ?,
                Data = ?,
                ID_Categoria = ?,
                Parcelado = ?,
                Num_Parcelas = ?,
                Parcela_Atual = ?,
                Notas = ?
            WHERE ID_Lancamento = ?
              AND ID_Usuario = ?
        """

        self.execute_query(sql, (
            dados["Descricao"],
            float(dados["Valor"]),
            dados["Data"],
            dados.get("ID_Categoria"),
            int(dados.get("Parcelado", 0)),
            int(dados.get("Num_Parcelas", 1)),
            int(dados.get("Parcela_Atual", 1)),
            dados.get("Notas"),
            id_lancamento,
            id_usuario
        ))

        return True

    # ============================================================
    # FATURA POR MÊS
    # ============================================================
    def get_lancamentos_por_fatura(self, id_cartao, mes, ano, id_usuario):

        sql = """
            SELECT *
            FROM lancamentos
            WHERE ID_Cartao = ?
              AND ID_Usuario = ?
              AND strftime('%m', Data) = ?
              AND strftime('%Y', Data) = ?
            ORDER BY date(Data)
        """

        mes_str = f"{int(mes):02d}"
        ano_str = str(int(ano))

        return self.fetch_all(
            sql,
            (id_cartao, id_usuario, mes_str, ano_str)
        )

    # ============================================================
    # HISTÓRICO DE FATURAS
    # ============================================================
    def get_all_faturas(self, id_usuario, id_cartao=None):

        sql = """
            SELECT
                ID_Cartao,
                strftime('%m', Data) AS Mes,
                strftime('%Y', Data) AS Ano,
                COUNT(*) AS Quantidade,
                SUM(Valor) AS Total
            FROM lancamentos
            WHERE ID_Usuario = ?
        """

        params = [id_usuario]

        if id_cartao:
            sql += " AND ID_Cartao = ?"
            params.append(id_cartao)

        sql += """
            GROUP BY ID_Cartao, Ano, Mes
            ORDER BY Ano DESC, Mes DESC
        """

        return self.fetch_all(sql, tuple(params))

    # ============================================================
    # NÃO PAGOS
    # ============================================================
    def get_lancamentos_nao_pagos(self, id_cartao, id_usuario):

        sql = """
            SELECT *
            FROM lancamentos
            WHERE ID_Cartao = ?
              AND ID_Usuario = ?
              AND Paga = 0
        """

        return self.fetch_all(sql, (id_cartao, id_usuario))

    # ============================================================
    # MARCAR COMO PAGO
    # ============================================================
    def marcar_como_pago(self, id_lancamento, id_transacao):

        sql = """
            UPDATE lancamentos
            SET Paga = 1,
                ID_Transacao = ?
            WHERE ID_Lancamento = ?
        """

        self.execute_query(sql, (id_transacao, id_lancamento))
        return True

    # ============================================================
    # EXCLUIR
    # ============================================================
    def excluir_lancamento(self, id_lancamento, id_usuario):

        sql = """
            DELETE FROM lancamentos
            WHERE ID_Lancamento = ?
              AND ID_Usuario = ?
        """

        self.execute_query(sql, (id_lancamento, id_usuario))
        return True