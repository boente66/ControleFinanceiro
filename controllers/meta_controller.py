import logging
from core.session import Session
from services.meta_service import MetaService

logger = logging.getLogger(__name__)


class MetaController:
    """
    Controlador de Metas
    Orquestra View ↔ Service
    """

    def __init__(self):
        self.service = MetaService()

    # ==================================================
    # UTIL
    # ==================================================
    def _get_usuario_id(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise RuntimeError("Usuário não autenticado")
        return usuario["ID_Usuario"]

    # ==================================================
    # CREATE
    # ==================================================
    def criar_meta(self, dados):

        id_usuario = self._get_usuario_id()
        dados["ID_Usuario"] = id_usuario

        return self.service.criar_meta(dados)

    # ==================================================
    # READ
    # ==================================================
    def listar_metas_ativas(self):

        id_usuario = self._get_usuario_id()
        return self.service.listar_metas_com_progresso(
            id_usuario,
            status="ATIVA"
        )

    def listar_metas_concluidas(self):

        id_usuario = self._get_usuario_id()
        return self.service.listar_metas_com_progresso(
            id_usuario,
            status="CONCLUIDA"
        )

    # ==================================================
    # UPDATE STATUS
    # ==================================================
    def concluir_meta(self, id_meta):

        id_usuario = self._get_usuario_id()
        self.service.alterar_status(
            id_meta,
            "CONCLUIDA",
            id_usuario
        )

    def cancelar_meta(self, id_meta):

        id_usuario = self._get_usuario_id()
        self.service.alterar_status(
            id_meta,
            "CANCELADA",
            id_usuario
        )

    def reativar_meta(self, id_meta):

        id_usuario = self._get_usuario_id()
        self.service.alterar_status(
            id_meta,
            "ATIVA",
            id_usuario
        )

    # ==================================================
    # DELETE
    # ==================================================
    def excluir_meta(self, id_meta):

        id_usuario = self._get_usuario_id()
        self.service.excluir_meta(
            id_meta,
            id_usuario
        )