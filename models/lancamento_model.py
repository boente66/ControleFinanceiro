import logging
from database.database import Database
from models.credito_model import CreditoModel

logger = logging.getLogger(__name__)


class LancamentoModel(Database):

    def __init__(self):
        super().__init__()
        self.credito = CreditoModel()

    # ============================================================
    # CRIAR LANÇAMENTO (SEM LÓGICA)
    # ============================================================
    def add_lancamento(self, dados: dict) -> bool:

        obrigatorios = [
            "ID_Usuario",
            "ID_Cartao",
            "Descricao",
            "Valor",
            "Data",
            "Competencia_Mes",
            "Competencia_Ano"
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

        # Normalizar data
        data = dados["Data"]
        if not isinstance(data, str):
            data = data.strftime("%Y-%m-%d")

        sql = """
            INSERT INTO lancamentos (
                ID_Cartao,
                Data,
                Competencia_Mes,
                Competencia_Ano,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            dados["ID_Cartao"],
            data,
            int(dados["Competencia_Mes"]),
            int(dados["Competencia_Ano"]),
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
    # ATUALIZAR (SEM LÓGICA)
    # ============================================================
    def update_lancamento(self, id_lancamento, dados, id_usuario):

        obrigatorios = [
            "Descricao",
            "Valor",
            "Data",
            "Competencia_Mes",
            "Competencia_Ano"
        ]

        for campo in obrigatorios:
            if campo not in dados:
                raise ValueError(f"{campo} é obrigatório.")

        cartao = self.credito.get_cartao_by_id(
            dados["ID_Cartao"],
            id_usuario
        )

        if not cartao:
            raise PermissionError("Cartão inválido.")

        data = dados["Data"]
        if not isinstance(data, str):
            data = data.strftime("%Y-%m-%d")

        sql = """
            UPDATE lancamentos
            SET Descricao = ?,
                Valor = ?,
                Data = ?,
                Competencia_Mes = ?,
                Competencia_Ano = ?,
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
            data,
            int(dados["Competencia_Mes"]),
            int(dados["Competencia_Ano"]),
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
    # FATURA (SQL LIMPO E RÁPIDO)
    # ============================================================
    def get_lancamentos_por_fatura(self, id_cartao, mes, ano, id_usuario):

        sql = """
            SELECT *
            FROM lancamentos
            WHERE ID_Cartao = ?
              AND ID_Usuario = ?
              AND Competencia_Mes = ?
              AND Competencia_Ano = ?
            ORDER BY Data
        """

        return self.fetch_all(
            sql,
            (id_cartao, id_usuario, int(mes), int(ano))
        )

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