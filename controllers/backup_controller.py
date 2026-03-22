# backup_controller.py

import logging
from services.backup_service import BackupService


logger = logging.getLogger(__name__)


class BackupController:
    """
    Controller responsável por intermediar View e Service
    """

    def __init__(self):
        self.service = BackupService()

    # ==================================================
    # BACKUP
    # ==================================================
    def criar_backup(self, pasta_destino, senha):
        try:
            return self.service.criar_backup(pasta_destino, senha)
        except Exception as e:
            logger.exception("Erro no controller ao criar backup")
            raise

    # ==================================================
    # RESTAURAÇÃO
    # ==================================================
    def restaurar_backup(self, arquivo, senha):
        try:
            return self.service.restaurar_backup(arquivo, senha)
        except Exception as e:
            logger.exception("Erro no controller ao restaurar backup")
            raise

    # ==================================================
    # VALIDAÇÃO
    # ==================================================
    def validar_backup(self, arquivo, senha):
        try:
            return self.service.validar_backup(arquivo, senha)
        except Exception:
            logger.exception("Erro ao validar backup")
            return False

    # ==================================================
    # LISTAR
    # ==================================================
    def listar_backups(self, diretorio):
        try:
            return self.service.listar_backups(diretorio)
        except Exception:
            logger.exception("Erro ao listar backups")
            return []

    # ==================================================
    # EXCLUIR
    # ==================================================
    def excluir_backup(self, arquivo):
        try:
            return self.service.excluir_backup(arquivo)
        except Exception as e:
            logger.exception("Erro ao excluir backup")
            raise
