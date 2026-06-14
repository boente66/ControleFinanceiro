# -*- coding: utf-8 -*-
import logging

from core.session import Session
from controllers.fatura_controller import FaturaController
from controllers.transaction_controller import TransactionController

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MainController:
    """
    Controller central da aplicação.

    Responsabilidades:
    - Orquestrar fluxos gerais da aplicação
    - Usar Session como fonte única do usuário
    - NÃO conter lógica de UI
    - NÃO conter regra de negócio pesada

    Observação:
    - Baixa de agendamento pertence ao ScheduleController + PaymentService.
    """

    def __init__(self):
        self.fatura_controller = FaturaController()
        self.transaction_controller = TransactionController()

    # ======================================================
    # USUÁRIO
    # ======================================================
    def get_usuario(self):
        return Session.get_usuario()

    def get_usuario_id(self):
        usuario = Session.get_usuario()

        if not usuario:
            return None

        return usuario.get("ID_Usuario")

    # ======================================================
    # LANÇAMENTOS MANUAIS
    # ======================================================
    def inserir_lancamento(self, data: dict) -> bool:
        """
        Insere lançamento manual.

        Pode ser:
        - lançamento em conta
        - lançamento em cartão
        """

        try:
            usuario_id = self.get_usuario_id()

            if not usuario_id:
                raise PermissionError("Usuário não autenticado.")

            data["ID_Usuario"] = usuario_id

            if data.get("ID_Conta"):
                return self.transaction_controller.add_transaction(data)

            if data.get("ID_Cartao"):
                return self.fatura_controller.registrar_despesa_cartao(data)

            raise ValueError(
                "Informe uma conta (ID_Conta) ou cartão (ID_Cartao)."
            )

        except Exception as e:
            logger.error(
                "Erro ao inserir lançamento para usuário %s: %s",
                self.get_usuario_id(),
                e,
                exc_info=True
            )
            return False