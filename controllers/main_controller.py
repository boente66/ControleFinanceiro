import logging

from core.session import Session
from controllers.fatura_controller import FaturaController
from controllers.transaction_controller import TransactionController
from controllers.schedule_controller import ScheduleController
from services.schedule_service import ScheduleService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MainController:
    """
    Controller central da aplicação.

    Responsabilidades:
    - Orquestrar fluxos entre controllers
    - Usar Session como fonte única do usuário
    - NÃO conter lógica de UI
    - NÃO conter regra de negócio pesada
    """

    def __init__(self):
        self.fatura_controller = FaturaController()
        self.transaction_controller = TransactionController()
        self.schedule_controller = ScheduleController()
        self.schedule_service = ScheduleService()

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
        try:
            usuario_id = self.get_usuario_id()
            if not usuario_id:
                raise PermissionError("Usuário não autenticado.")

            data["ID_Usuario"] = usuario_id

            if data.get("ID_Conta"):
                return self.transaction_controller.add_transaction(data)

            if data.get("ID_Cartao"):
                return self.fatura_controller.registrar_despesa_cartao(data)

            raise ValueError("Informe uma conta (ID_Conta) ou cartão (ID_Cartao).")

        except Exception as e:
            logger.error(
                "Erro ao inserir lançamento para usuário %s: %s",
                self.get_usuario_id(), e, exc_info=True
            )
            return False

    # ======================================================
    # EXECUTAR UM AGENDAMENTO
    # ======================================================
    def _executar_movimento_agendamento(self, agendamento, usuario_id):

        if agendamento.get("ID_Cartao"):
            return self.fatura_controller.registrar_despesa_cartao({
                "Descricao": agendamento.get("Descricao"),
                "Valor": agendamento.get("Valor"),
                "Data": agendamento.get("Data"),
                "ID_Cartao": agendamento.get("ID_Cartao"),
                "ID_Usuario": usuario_id,
                "ID_Categoria": agendamento.get("ID_Categoria"),
                "ID_Favorecido": agendamento.get("ID_Favorecido"),
                "Num_Parcelas": int(agendamento.get("Parcelas", 1)),
                "Previsto": 0,
            })

        if agendamento.get("ID_Conta"):
            tipo = self.schedule_service.MAPA_TIPO_TRANSACAO.get(
                agendamento.get("Tipo")
            )

            if not tipo:
                raise ValueError(
                    f"Tipo de agendamento inválido: {agendamento.get('Tipo')}"
                )

            valor = float(agendamento.get("Valor", 0))

            if tipo == "Despesa":
                valor = -abs(valor)
            elif tipo == "Receita":
                valor = abs(valor)
            elif tipo == "Transferência":
                raise ValueError(
                    "Agendamento de transferência ainda não possui conta origem/destino."
                )

            return self.transaction_controller.add_transaction({
                "ID_Conta": agendamento.get("ID_Conta"),
                "Descricao": agendamento.get("Descricao") or "Agendamento",
                "Valor": valor,
                "Data": agendamento.get("Data"),
                "Tipo": tipo,
                "ID_Usuario": usuario_id,
                "ID_Categoria": agendamento.get("ID_Categoria"),
                "ID_Favorecido": agendamento.get("ID_Favorecido"),
            })

        raise ValueError("Agendamento sem conta e sem cartão.")


    def execute_schedule(self, schedule_id: int) -> bool:
        """
        Executa um agendamento.

        Fluxo:
        1. Busca o agendamento
        2. Executa o movimento financeiro
        3. Marca como executado
        4. Gera recorrência (se existir)
        """

        try:
            usuario_id = self.get_usuario_id()

            if not usuario_id:
                raise PermissionError("Usuário não autenticado.")

            agendamento = self.schedule_controller.get_schedule_by_id(
                schedule_id
            )

            if not agendamento:
                raise ValueError("Agendamento não encontrado.")

            # ---------------------------------------------
            # Movimento financeiro
            # ---------------------------------------------
            resultado = self._executar_movimento_agendamento(
                agendamento,
                usuario_id
            )

            if not resultado:
                return False

            # ---------------------------------------------
            # Atualiza status / recorrência
            # ---------------------------------------------
            return self.schedule_service.execute_schedule(
                schedule_id,
                usuario_id
            )

        except Exception as e:

            logger.error(
                "Erro ao executar agendamento %s para usuário %s: %s",
                schedule_id,
                self.get_usuario_id(),
                e,
                exc_info=True
            )

        return False

    # ======================================================
    # EXECUTAR VÁRIOS
    # ======================================================
    def execute_multiple_schedules(self, agendamento_ids: list[int]):
        sucesso = []
        falha = []

        for ag_id in agendamento_ids:
            if self.execute_schedule(ag_id):
                sucesso.append(ag_id)
            else:
                falha.append(ag_id)

        return sucesso, falha

    # ======================================================
    # EXECUTAR TODOS
    # ======================================================
    def execute_all_schedules(self):
        try:
            agendamentos = self.schedule_controller.get_all_schedules()

            ids = [
                a["ID_Agendamento"]
                for a in agendamentos
                if a["Status"] in ("AGENDADO", "ATRASADO")
            ]

            return self.execute_multiple_schedules(ids)

        except Exception as e:
            logger.error(
                "Erro ao executar todos os agendamentos para usuário %s: %s",
                self.get_usuario_id(),
                e,
                exc_info=True
            )
            return [], []