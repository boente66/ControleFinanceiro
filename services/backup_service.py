# services/backup_service.py

import logging
import os
from typing import List, Dict

from core.config import DB_PATH
from backup.backup_model import BackupModel


logger = logging.getLogger(__name__)


class BackupService:
    """
    Camada de serviço responsável por:
    - validações de negócio
    - orquestração entre View e Model
    - regras de segurança
    """

    def __init__(self):
        self.model = BackupModel(DB_PATH)

    # =====================================================
    # BACKUP
    # =====================================================
    def criar_backup(self, destino: str, senha: str) -> str:

        if not senha or len(senha) < 4:
            raise ValueError("A senha deve ter pelo menos 4 caracteres.")

        if not destino or not os.path.isdir(destino):
            raise ValueError("Destino inválido.")

        try:
            caminho = self.model.criar_backup(destino, senha)

            logger.info(f"[BACKUP] Criado com sucesso: {caminho}")

            return caminho

        except Exception as e:
            logger.exception("[BACKUP] Erro ao criar")
            raise Exception(f"Falha ao criar backup: {str(e)}")

    # =====================================================
    # RESTAURAÇÃO
    # =====================================================
    def restaurar_backup(self, arquivo: str, senha: str):

        if not os.path.exists(arquivo):
            raise FileNotFoundError("Arquivo de backup não encontrado.")

        if not senha:
            raise ValueError("Senha obrigatória.")

        # 🔥 valida antes
        if not self.model.validar_backup(arquivo, senha):
            raise Exception("Senha inválida ou backup corrompido.")

        pasta_backup = os.path.dirname(arquivo)

        # 🔥 backup preventivo com nome especial
        try:
            logger.info("[RESTORE] Criando backup preventivo...")

            self.model.criar_backup(pasta_backup, senha)

        except Exception:
            logger.warning("[RESTORE] Falha no backup preventivo")

        # 🔥 restauração real
        try:
            self.model.restaurar_backup(arquivo, senha)

            logger.info(f"[RESTORE] Sucesso: {arquivo}")

            return True

        except Exception as e:
            logger.exception("[RESTORE] Erro ao restaurar")
            raise Exception(f"Falha ao restaurar backup: {str(e)}")

    # =====================================================
    # VALIDAÇÃO
    # =====================================================
    def validar_backup(self, arquivo: str, senha: str) -> bool:

        if not os.path.exists(arquivo):
            return False

        try:
            return self.model.validar_backup(arquivo, senha)

        except Exception:
            logger.exception("[VALIDAR] Erro")
            return False

    # =====================================================
    # LISTAGEM
    # =====================================================
    def listar_backups(self, diretorio: str) -> List[Dict]:

        if not os.path.isdir(diretorio):
            return []

        try:
            return self.model.listar_backups(diretorio)

        except Exception:
            logger.exception("[LISTAR] Erro")
            return []

    # =====================================================
    # EXCLUSÃO
    # =====================================================
    def excluir_backup(self, arquivo: str):

        if not os.path.exists(arquivo):
            raise FileNotFoundError("Arquivo não encontrado.")

        try:
            self.model.excluir_backup(arquivo)

            logger.info(f"[DELETE] Backup removido: {arquivo}")

            return True

        except Exception as e:
            logger.exception("[DELETE] Erro")
            raise Exception(f"Falha ao excluir backup: {str(e)}")