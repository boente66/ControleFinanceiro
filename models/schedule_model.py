from database.database import Database
import logging

logger = logging.getLogger(__name__)


class ScheduleModel(Database):
    def __init__(self):
        super().__init__()

    # ------------------------------------------------------------------
    # ADD
    # ------------------------------------------------------------------
    def add_schedule(self, schedule_data: dict) -> None:
        """
        Adiciona um novo agendamento no banco de dados.
        """
        query = """
        INSERT INTO agendamentos (
            Tipo, Data, Valor, Descricao, Status,
            ID_Favorecido, ID_Conta, ID_Usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.execute_query(
                query,
                (
                    schedule_data["Tipo"],
                    schedule_data["Data"],
                    schedule_data["Valor"],
                    schedule_data["Descricao"],
                    "AGENDADO",  # status inicial
                    schedule_data.get("ID_Favorecido"),
                    schedule_data.get("ID_Conta"),
                    schedule_data["ID_Usuario"],
                ),
            )
        except Exception as e:
            logger.error("Erro ao adicionar agendamento: %s", e, exc_info=True)
            raise

    # ------------------------------------------------------------------
    # SELECT TODOS (tabela principal)
    # ------------------------------------------------------------------
    def get_all_schedules(self, id_usuario: int) -> list:
        """
        Retorna todos os agendamentos do usuário.
        """
        query = """
        SELECT
            a.ID_Agendamento,
            a.Tipo,
            a.Data,
            a.Valor,
            a.Descricao,
            a.Status,
            f.Nome AS Favorecido,
            c.Nome_Conta AS Conta
        FROM agendamentos a
        LEFT JOIN favorecido f ON a.ID_Favorecido = f.ID_Favorecido
        LEFT JOIN contas c ON a.ID_Conta = c.ID_Conta
        WHERE a.ID_Usuario = ?
        ORDER BY a.Data
        """

        try:
            return self.fetch_all(query, (id_usuario,))
        except Exception as e:
            logger.error(
                "Erro ao carregar agendamentos do usuário %s: %s",
                id_usuario,
                e,
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # SELECT PRÓXIMOS (sidebar / dashboard)
    # ------------------------------------------------------------------
    def get_upcoming_schedules(self, id_usuario: int) -> list:
        """
        Retorna os próximos 5 agendamentos AGENDADOS do usuário.
        """
        query = """
        SELECT
            a.ID_Agendamento,
            a.Data,
            a.Valor,
            a.Descricao
        FROM agendamentos a
        WHERE a.ID_Usuario = ?
          AND a.Status = 'AGENDADO'
          AND a.Data >= date('now')
        ORDER BY a.Data
        LIMIT 5
        """

        try:
            return self.fetch_all(query, (id_usuario,))
        except Exception as e:
            logger.error(
                "Erro ao obter próximos agendamentos do usuário %s: %s",
                id_usuario,
                e,
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # SELECT POR ID
    # ------------------------------------------------------------------
    def get_schedule_by_id(self, schedule_id: int, id_usuario: int) -> dict | None:
        """
        Retorna um agendamento específico do usuário.
        """
        query = """
        SELECT
            a.*,
            f.Nome AS Favorecido,
            c.Nome_Conta AS Conta
        FROM agendamentos a
        LEFT JOIN favorecido f ON a.ID_Favorecido = f.ID_Favorecido
        LEFT JOIN contas c ON a.ID_Conta = c.ID_Conta
        WHERE a.ID_Agendamento = ?
          AND a.ID_Usuario = ?
        """

        try:
            return self.fetch_one(query, (schedule_id, id_usuario))
        except Exception as e:
            logger.error(
                "Erro ao buscar agendamento %s do usuário %s: %s",
                schedule_id,
                id_usuario,
                e,
                exc_info=True,
            )
            return None

    # ------------------------------------------------------------------
    # UPDATE STATUS (genérico)
    # ------------------------------------------------------------------
    def update_status(self, schedule_id: int, id_usuario: int, status: str) -> None:
        """
        Atualiza o status de um agendamento.
        """
        query = """
        UPDATE agendamentos
        SET Status = ?
        WHERE ID_Agendamento = ?
          AND ID_Usuario = ?
        """

        try:
            self.execute_query(query, (status, schedule_id, id_usuario))
        except Exception as e:
            logger.error(
                "Erro ao atualizar status do agendamento %s: %s",
                schedule_id,
                e,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # CANCELAR (soft delete)
    # ------------------------------------------------------------------
    def cancel_schedule(self, schedule_id: int, id_usuario: int) -> None:
        """
        Cancela um agendamento (soft delete).
        """
        query = """
        UPDATE agendamentos
        SET Status = 'CANCELADO'
        WHERE ID_Agendamento = ?
          AND ID_Usuario = ?
        """

        try:
            self.execute_query(query, (schedule_id, id_usuario))
        except Exception as e:
            logger.error(
                "Erro ao cancelar agendamento %s: %s",
                schedule_id,
                e,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # MARCAR ATRASADOS (batch)
    # ------------------------------------------------------------------
    def mark_as_overdue(self, id_usuario: int, data_hoje: str) -> None:
        """
        Marca agendamentos vencidos como ATRASADO.
        """
        query = """
        UPDATE agendamentos
        SET Status = 'ATRASADO'
        WHERE ID_Usuario = ?
          AND Status = 'AGENDADO'
          AND Data < ?
        """

        try:
            self.execute_query(query, (id_usuario, data_hoje))
        except Exception as e:
            logger.error(
                "Erro ao marcar agendamentos atrasados do usuário %s: %s",
                id_usuario,
                e,
                exc_info=True,
            )
            raise

    def set_inactive(self, schedule_id: int, id_usuario: int) -> None:
        """
        Marca um agendamento como inativo (encerra a recorrência),
        sem apagar o registro.
        """
        try:
            query = """
                UPDATE agendamentos
                SET
                    Ativo = 0,
                    Status = 'INATIVO'
                WHERE
                    ID_Agendamento = ?
                    AND ID_Usuario = ?
            """
            self.execute_query(query, (schedule_id, id_usuario))
        except Exception as e:
            logger.error(
                "Erro ao marcar agendamento %s como inativo: %s",
                schedule_id,
                e,
                exc_info=True,
            )
            raise

    def get_agendamentos_ativos_por_conta(self, id_conta, id_usuario) -> list:
        """
        Retorna agendamentos ativos e com status AGENDADO
        vinculados a uma conta específica.
        """
        try:
            query = """
                SELECT Tipo, Valor
                FROM agendamentos
                WHERE ID_Conta = ?
                AND ID_Usuario = ?
                AND Ativo = 1
                AND Status = 'AGENDADO'
            """

            return self.fetch_all(query, (id_conta, id_usuario))

        except Exception as e:
            logger.error("Erro ao buscar agendamentos da conta: %s", e, exc_info=True)
            return []
