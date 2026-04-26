from services.transaction_service import TransactionService
from core.session import Session


class TransactionController:

    def __init__(self):
        self.service = TransactionService()

    # ============================================================
    # UTIL
    # ============================================================
    def _get_usuario_id(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise RuntimeError("Usuário não autenticado.")
        return usuario["ID_Usuario"]

    # ============================================================
    # LISTAR TRANSAÇÕES
    # ============================================================
    def get_transactions_by_account_periodo(self, id_conta, periodo):
        id_usuario = self._get_usuario_id()

        return self.service.get_transactions_by_account_periodo(
            id_usuario,
            id_conta,
            periodo
        )

    def get_transaction_by_id(self, id_transacao):
        id_usuario = self._get_usuario_id()

        trans = self.service.get_transaction_by_id(id_transacao, id_usuario)

        if not trans:
            return None

        if trans["ID_Usuario"] != id_usuario:
            return None

        return trans

    # ============================================================
    # CRUD
    # ============================================================
    def add_transaction(self, dados):
        dados["ID_Usuario"] = self._get_usuario_id()
        return self.service.criar_transacao(dados)

    def update_transaction(self, dados):
        dados["ID_Usuario"] = self._get_usuario_id()
        return self.service.atualizar_transacao(dados)

    def delete_transaction(self, id_transacao):
        id_usuario = self._get_usuario_id()
        return self.service.excluir_transacao(id_transacao, id_usuario)

    # ============================================================
    # TRANSFERÊNCIAS
    # ============================================================
    def transferir_saldo(self, id_origem, id_destino, valor, data):
        id_usuario = self._get_usuario_id()

        return self.service.transferir(
            id_origem,
            id_destino,
            valor,
            data,
            id_usuario
        )

    def converter_em_transferencia(self, id_transacao, id_conta_destino):
        id_usuario = self._get_usuario_id()

        return self.service.converter_em_transferencia(
            id_transacao,
            id_conta_destino,
            id_usuario
        )

    # ============================================================
    # RESUMO
    # ============================================================
    def get_resumo_financeiro(self):
        return self.service.get_resumo_financeiro(
            self._get_usuario_id()
        )

    def get_analise_mensal(self):
        return self.service.get_analise_mensal(
            self._get_usuario_id()
        )

    # ============================================================
    # IMPORTAÇÃO EM LOTE
    # ============================================================
    def salvar_lote_importado(self, lista_transacoes: list):
        return self.service.salvar_lote_importado(
            lista_transacoes,
            self._get_usuario_id()
        )