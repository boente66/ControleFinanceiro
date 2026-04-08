import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

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
    def execute_schedule(self, agendamento_id: int) -> bool:
        try:
            usuario = Session.get_usuario()
            if not usuario:
                raise PermissionError("Usuário não autenticado.")

            usuario_id = usuario["ID_Usuario"]

            agendamento = self.schedule_controller.get_schedule_by_id(
                agendamento_id
            )

            if not agendamento:
                raise ValueError("Agendamento não encontrado.")

            if agendamento["Status"] not in ("AGENDADO", "ATRASADO"):
                raise ValueError("Agendamento não pode ser executado.")

            # ==================================================
            # BASE DO LANÇAMENTO
            # ==================================================
            base_lancamento = {
                "Data": agendamento["Data"],
                "Valor": agendamento["Valor"],
                "Descricao": agendamento.get("Descricao") or "Agendamento",
                "ID_Usuario": usuario_id,
                "ID_Categoria": agendamento.get("ID_Categoria"),
                "ID_Favorecido": agendamento.get("ID_Favorecido"),
                "Tipo": agendamento.get("Tipo"),
                "ID_Agendamento": agendamento_id,
            }

            sucesso = False

            # ==================================================
            # CONTA (normal)
            # ==================================================
            if agendamento.get("ID_Conta"):
                lancamento = base_lancamento.copy()
                lancamento["ID_Conta"] = agendamento["ID_Conta"]

                sucesso = self.transaction_controller.add_transaction(
                    lancamento
                )

            # ==================================================
            # CARTÃO (com parcelas)
            # ==================================================
            elif agendamento.get("ID_Cartao"):

                parcelas = int(agendamento.get("Parcelas", 1))
                valor_total = float(agendamento["Valor"])
                valor_parcela = valor_total / parcelas

                data_base = datetime.fromisoformat(agendamento["Data"])

                for i in range(parcelas):

                    lancamento = base_lancamento.copy()

                    data_parcela = data_base + relativedelta(months=i)

                    lancamento.update({
                        "ID_Cartao": agendamento["ID_Cartao"],
                        "Valor": valor_parcela,
                        "Data": data_parcela.date().isoformat(),
                        "Parcela": i + 1,
                        "Total_Parcelas": parcelas,
                    })

                    ok = self.fatura_controller.registrar_despesa_cartao(
                        lancamento
                    )

                    if not ok:
                        raise RuntimeError(f"Erro ao lançar parcela {i+1}")

                sucesso = True

            else:
                raise ValueError("Agendamento sem conta ou cartão.")

            if not sucesso:
                raise RuntimeError("Falha ao criar lançamento.")

            # ==================================================
            # ATUALIZA STATUS
            # ==================================================
            self.schedule_service.execute_schedule(
                agendamento_id,
                usuario_id
            )

            logger.info(
                "Agendamento %s executado com sucesso para usuário %s",
                agendamento_id, usuario_id
            )

            return True

        except Exception as e:
            logger.error(
                "Erro ao executar agendamento %s para usuário %s: %s",
                agendamento_id,
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