import logging
from services.schedule_service import ScheduleService
from core.session import Session

logger = logging.getLogger(__name__)


class ScheduleController:
    """
    Controller de Agendamentos.
    Responsável apenas por:
    - Validar sessão
    - Encaminhar dados ao Service
    """

    def __init__(self):
        self.schedule_service = ScheduleService()

    # ============================================================
    # CRIAR AGENDAMENTO
    # ============================================================
    def add_schedule(self, schedule_data: dict) -> bool:
        """
        Cria um novo agendamento para o usuário logado.
        A decisão de recorrência acontece na criação.
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        schedule_data["ID_Usuario"] = usuario["ID_Usuario"]

        return self.schedule_service.add_schedule(schedule_data)

    # ============================================================
    # PRÓXIMOS AGENDAMENTOS
    # ============================================================
    def get_upcoming_schedules(self) -> list:
        """
        Retorna os próximos agendamentos ativos do usuário logado.
        Usado em dashboards / sidebar.
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        return self.schedule_service.get_upcoming_schedules(
            usuario["ID_Usuario"]
        )

    # ============================================================
    # ATUALIZAR AGENDAMENTO
    # ============================================================
    def update_schedule(self, schedule_id: int, schedule_data: dict) -> bool:
        """
        Atualiza um agendamento do usuário logado.

        IMPORTANTE:
        - Se NÃO recorrente → edita normalmente
        - Se recorrente → Service versiona automaticamente
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        schedule_data["ID_Usuario"] = usuario["ID_Usuario"]

        return self.schedule_service.update_schedule(
            schedule_id,
            schedule_data
        )

    # ============================================================
    # BUSCAR AGENDAMENTO POR ID
    # ============================================================
    def get_schedule_by_id(self, schedule_id: int):
        """
        Retorna um agendamento específico do usuário logado.
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        return self.schedule_service.get_schedule_by_id(
            schedule_id,
            usuario["ID_Usuario"]
        )

    # ============================================================
    # BUSCAR TODOS OS AGENDAMENTOS
    # ============================================================
    def get_all_schedules(self) -> list:
        """
        Retorna todos os agendamentos do usuário logado.
        Inclui ativos, inativos e históricos.
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        return self.schedule_service.get_all_schedules(
            usuario["ID_Usuario"]
        )

    # ============================================================
    # CANCELAR AGENDAMENTO
    # ============================================================
    def cancel_schedule(self, schedule_id: int) -> bool:
        """
        Cancela (encerra) um agendamento do usuário logado.
        Não remove histórico.
        """
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")

        return self.schedule_service.cancel_schedule(
            schedule_id,
            usuario["ID_Usuario"]
        )
