import logging
from core.session import Session
from services.account_service import AccountService

logger = logging.getLogger(__name__)


class AccountController:
    """Controlador de contas (orquestra Service ↔ View)."""

    def __init__(self):
        self.service = AccountService()

    # -------------------------------------------
    # UTIL
    # -------------------------------------------
    def get_usuario_id(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise RuntimeError("Usuário não autenticado.")
        return usuario["ID_Usuario"]

    # -------------------------------------------
    # CREATE
    # -------------------------------------------
    def create_account(self, dados_conta):
        dados_conta["ID_Usuario"] = self.get_usuario_id()
        return self.service.criar_conta(dados_conta)

    # -------------------------------------------
    # READ
    # -------------------------------------------
    def get_all_accounts(self):
        return self.service.listar_contas(self.get_usuario_id())

    def get_account_by_id(self, id_conta):
        return self.service.buscar_por_id(id_conta, self.get_usuario_id())

    def get_account_by_name(self, nome):
        return self.service.buscar_por_nome(nome, self.get_usuario_id())

    # -------------------------------------------
    # UPDATE
    # -------------------------------------------
    def update_account(self, id_conta, dados_editados):
        return self.service.atualizar_conta(
            id_conta,
            dados_editados,
            self.get_usuario_id()
        )

    def update_account_balance(self, id_conta, novo_saldo):
        return self.service.atualizar_saldo(
            id_conta,
            novo_saldo,
            self.get_usuario_id()
        )

    def ajustar_saldo(self, id_conta, novo_saldo):
        return self.service.ajustar_saldo(
            id_conta,
            novo_saldo,
            self.get_usuario_id()
        )

    # -------------------------------------------
    # DELETE
    # -------------------------------------------
    def delete_account(self, id_conta):
        return self.service.deletar_conta(
            id_conta,
            self.get_usuario_id()
        )


    # -------------------------------------------
    # SALDO DA CONTA
    # ------------------------------------------

    def get_account_balance(self, id_conta):
        return self.service.obter_saldo(
            id_conta,
            self.get_usuario_id()
        )
     

    # =================================
    # RECALCULAR SALDO
    # =================================
    
    def recalcular_saldo(self, id_conta):
        return self.service.atualiza_saldo(
            id_conta,
            self.get_usuario_id()
        )