import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from models.schedule_model import ScheduleModel
from models.account_model import AccountModel

from services.fatura_service import FaturaService  # 🔥 NOVO

logger = logging.getLogger(__name__)


class ScheduleService:

    def __init__(self):
        self.schedule_model = ScheduleModel()
        self.account_model = AccountModel()
        self.fatura_service = FaturaService()  # 🔥 NOVO

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

            # 🔥 NOVO: se for cartão → cria previsão
            if schedule_data.get("Tipo") == "Cartao":
                self._gerar_previsto_cartao(schedule_data)

            return True

        except Exception as e:
            logger.error("Erro ao adicionar agendamento: %s", e, exc_info=True)
            return False

    # ============================================================
    # EXECUÇÃO
    # ============================================================
    def executar_agendamento(self, schedule_id: int, id_usuario: int) -> bool:

        try:
            ag = self.schedule_model.get_schedule_by_id(
                schedule_id, id_usuario
            )

            if not ag:
                raise ValueError("Agendamento não encontrado.")

            if ag["Status"] != "AGENDADO":
                raise ValueError("Somente agendamentos AGENDADOS podem ser executados.")

            # 🔥 CARTÃO → NÃO gera transação normal
            if ag.get("Tipo") == "Cartao":

                self._gerar_previsto_cartao(ag)

            else:
                # 🔥 fluxo normal (conta)
                pass

            self.schedule_model.update_status(
                schedule_id,
                id_usuario,
                "EXECUTADO"
            )

            # 🔁 recorrência
            if ag.get("Recorrente"):
                nova_data = self._calcular_proxima_data(
                    ag["Data"],
                    ag.get("Periodicidade")
                )

                novo = {
                    **ag,
                    "Data": nova_data,
                    "Status": "AGENDADO",
                    "ID_Pai": ag.get("ID_Pai") or ag["ID_Agendamento"]
                }

                novo.pop("ID_Agendamento", None)

                self.schedule_model.add_schedule(novo)

                # 🔥 gera próximo previsto automaticamente
                if ag.get("Tipo") == "Cartao":
                    self._gerar_previsto_cartao(novo)

            return True

        except Exception as e:
            logger.error("Erro ao executar agendamento: %s", e, exc_info=True)
            return False

    # ============================================================
    # 🔥 NOVO: GERAR LANÇAMENTO PREVISTO NO CARTÃO
    # ============================================================
    def _gerar_previsto_cartao(self, agendamento: dict):

        try:
            cartao_id = agendamento.get("ID_Cartao")
            id_usuario = agendamento.get("ID_Usuario")

            if not cartao_id:
                return

            cartao = self.fatura_service.buscar_cartao_por_id(
                cartao_id,
                id_usuario
            )

            if not cartao:
                return

            dia_fechamento = cartao["Dia_Fechamento"]

            data = agendamento["Data"]

            mes, ano = self.fatura_service.aplicar_fatura(
                data,
                dia_fechamento
            )

            self.fatura_service.registrar_despesa_cartao({
                "Descricao": agendamento.get("Descricao"),
                "Valor": agendamento.get("Valor"),
                "Data": data,
                "ID_Cartao": cartao_id,
                "Parcelas": 1,
                "ID_Categoria": agendamento.get("ID_Categoria"),
                "Previsto": 1,  # 🔥 ESSENCIAL
                "Competencia_Mes": mes,
                "Competencia_Ano": ano
            }, id_usuario)

        except Exception:
            logger.exception("Erro ao gerar lançamento previsto do cartão")

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
    # SALDO PREVISTO
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
    # PRÓXIMA DATA
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


    def get_upcoming_schedules(self, user_id: int):
        try:
            return self.schedule_model.get_upcoming_schedules(user_id)
        except Exception as e:
            logger.error("Erro ao obter próximos agendamentos: %s", e, exc_info=True)
            return []