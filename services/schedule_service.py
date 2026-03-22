from datetime import date, datetime
import logging
from dateutil.relativedelta import relativedelta

from models.schedule_model import ScheduleModel
from models.account_model import AccountModel

logger = logging.getLogger(__name__)


class ScheduleService:
    """
    Serviço responsável por TODA a regra de agendamentos,
    incluindo recorrência, versionamento e projeções.
    """

    def __init__(self):
        self.schedule_model = ScheduleModel()
        self.account_model = AccountModel()

    # ============================================================
    # CRIAÇÃO
    # ============================================================
    def add_schedule(self, schedule_data: dict) -> bool:
        try:
            if not schedule_data:
                raise ValueError("schedule_data não pode ser vazio.")

            if "ID_Usuario" not in schedule_data:
                raise ValueError("ID_Usuario é obrigatório.")

            schedule_data.setdefault("Recorrente", 0)
            schedule_data.setdefault("Periodicidade", None)
            schedule_data.setdefault("Ativo", 1)
            schedule_data.setdefault("Status", "AGENDADO")

            self.schedule_model.add_schedule(schedule_data)
            return True

        except Exception as e:
            logger.error("Erro ao adicionar agendamento: %s", e, exc_info=True)
            return False

    # ============================================================
    # ATUALIZAÇÃO
    # ============================================================
    def update_schedule(self, schedule_id: int, schedule_data: dict) -> bool:
        try:
            if not schedule_id:
                raise ValueError("schedule_id é obrigatório.")
            if "ID_Usuario" not in schedule_data:
                raise ValueError("ID_Usuario é obrigatório.")

            agendamento = self.schedule_model.get_schedule_by_id(
                schedule_id, schedule_data["ID_Usuario"]
            )

            if not agendamento:
                raise ValueError("Agendamento não encontrado.")

            if agendamento["Status"] != "AGENDADO":
                raise PermissionError(
                    "Somente agendamentos AGENDADOS podem ser editados."
                )

            # NÃO recorrente → edita direto
            if not agendamento.get("Recorrente"):
                self.schedule_model.update_schedule(schedule_id, schedule_data)
                return True

            # RECORRENTE → versiona
            self._versionar_agendamento_recorrente(
                agendamento_atual=agendamento,
                novos_dados=schedule_data
            )
            return True

        except Exception as e:
            logger.error("Erro ao atualizar agendamento %s: %s",
                         schedule_id, e, exc_info=True)
            return False

    # ============================================================
    # VERSIONAMENTO
    # ============================================================
    def _versionar_agendamento_recorrente(
        self,
        agendamento_atual: dict,
        novos_dados: dict
    ) -> None:

        id_usuario = agendamento_atual["ID_Usuario"]

        # 1️⃣ desativa atual
        self.schedule_model.set_inactive(
            agendamento_atual["ID_Agendamento"],
            id_usuario
        )

        # 2️⃣ cria novo
        novo = agendamento_atual.copy()
        novo.pop("ID_Agendamento", None)

        novo.update(novos_dados)

        novo["Status"] = "AGENDADO"
        novo["Ativo"] = 1
        novo["Recorrente"] = 1
        novo["ID_Usuario"] = id_usuario

        self.schedule_model.add_schedule(novo)

    # ============================================================
    # EXECUÇÃO
    # ============================================================
    def executar_agendamento(self, schedule_id: int, id_usuario: int) -> bool:
        """
        Executa agendamento e gera nova ocorrência se recorrente.
        """

        try:
            ag = self.schedule_model.get_schedule_by_id(
                schedule_id, id_usuario
            )

            if not ag:
                raise ValueError("Agendamento não encontrado.")

            if ag["Status"] != "AGENDADO":
                raise ValueError("Somente agendamentos AGENDADOS podem ser executados.")

            # Marca como executado
            self.schedule_model.update_status(
                schedule_id,
                id_usuario,
                "EXECUTADO"
            )

            # Se recorrente → gerar próximo
            if ag.get("Recorrente"):
                nova_data = self._calcular_proxima_data(
                    ag["Data"],
                    ag.get("Periodicidade")
                )

                novo = {
                    "Tipo": ag["Tipo"],
                    "Descricao": ag["Descricao"],
                    "ID_Conta": ag["ID_Conta"],
                    "ID_Favorecido": ag["ID_Favorecido"],
                    "ID_Categoria": ag["ID_Categoria"],
                    "Valor": ag["Valor"],
                    "Data": nova_data,
                    "Recorrente": 1,
                    "Periodicidade": ag.get("Periodicidade"),
                    "Ativo": 1,
                    "Status": "AGENDADO",
                    "ID_Pai": ag.get("ID_Pai") or ag["ID_Agendamento"],
                    "ID_Usuario": id_usuario
                }

                self.schedule_model.add_schedule(novo)

            return True

        except Exception as e:
            logger.error("Erro ao executar agendamento: %s", e, exc_info=True)
            return False

    # ============================================================
    # CANCELAMENTO
    # ============================================================
    def cancel_schedule(self, schedule_id: int, id_usuario: int) -> bool:
        try:
            ag = self.schedule_model.get_schedule_by_id(
                schedule_id, id_usuario
            )

            if not ag:
                raise ValueError("Agendamento não encontrado.")

            if ag["Status"] != "AGENDADO":
                raise PermissionError(
                    "Somente agendamentos AGENDADOS podem ser cancelados."
                )

            self.schedule_model.cancel_schedule(schedule_id, id_usuario)
            return True

        except Exception as e:
            logger.error("Erro ao cancelar agendamento %s: %s",
                         schedule_id, e, exc_info=True)
            return False

    # ============================================================
    # CONSULTAS
    # ============================================================
    def get_schedule_by_id(self, schedule_id: int, id_usuario: int):
        return self.schedule_model.get_schedule_by_id(schedule_id, id_usuario)

    def get_all_schedules(self, id_usuario: int) -> list:
        return self.schedule_model.get_all_schedules(id_usuario)

    def get_upcoming_schedules(self, id_usuario: int) -> list:
        return self.schedule_model.get_upcoming_schedules(id_usuario)

    # ============================================================
    # ATRASOS
    # ============================================================
    def mark_overdue(self, id_usuario: int) -> None:
        hoje = date.today().isoformat()
        self.schedule_model.mark_as_overdue(id_usuario, hoje)

    # ============================================================
    # SALDO PREVISTO POR CONTA
    # ============================================================
    def calcular_saldo_previsto_conta(self, id_conta: int, id_usuario: int) -> float:
        try:
            conta = self.account_model.get_account_by_id(id_conta, id_usuario)

            if not conta:
                raise ValueError("Conta não encontrada.")

            saldo_atual = float(conta.get("Saldo_Atual", 0))

            agendamentos = self.schedule_model.get_agendamentos_ativos_por_conta(
                id_conta,
                id_usuario
            )

            total_pagar = 0.0
            total_receber = 0.0

            for ag in agendamentos:
                valor = float(ag.get("Valor", 0))

                if ag.get("Tipo") == "Contas a Pagar":
                    total_pagar += valor
                elif ag.get("Tipo") == "Contas a Receber":
                    total_receber += valor

            return saldo_atual - total_pagar + total_receber

        except Exception as e:
            logger.error(
                "Erro ao calcular saldo previsto da conta %s: %s",
                id_conta,
                e,
                exc_info=True
            )
            return 0.0

    # ============================================================
    # CÁLCULO DE PRÓXIMA DATA
    # ============================================================
    def _calcular_proxima_data(self, data_str, periodicidade):

        data = datetime.strptime(data_str, "%Y-%m-%d")

        if periodicidade == "Mensal":
            nova = data + relativedelta(months=1)
        elif periodicidade == "Anual":
            nova = data + relativedelta(years=1)
        else:
            nova = data

        return nova.strftime("%Y-%m-%d")