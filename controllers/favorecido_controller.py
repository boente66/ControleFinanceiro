import logging
from core.session import Session
from services.favorecido_service import FavorecidoService

logger = logging.getLogger(__name__)


class FavorecidoController:
    """
    Controller responsável por orquestrar operações relacionadas a Favorecidos.
    NÃO contém regras de negócio.
    """

    def __init__(self):
        self.service = FavorecidoService()

    # -------------------------------------------
    # LISTAR
    # -------------------------------------------
    def listar_favorecidos(self):
        try:
            return self.service.listar(self.get_id_usuario())
        except Exception as e:
            logger.error("Erro ao listar favorecidos: %s", e, exc_info=True)
            return []

    # -------------------------------------------
    # OBTER POR ID
    # -------------------------------------------
    def obter_favorecido(self, id_favorecido):
        try:
            return self.service.obter(id_favorecido, self.get_id_usuario())
        except Exception as e:
            logger.error("Erro ao obter favorecido: %s", e, exc_info=True)
            return None

    # -------------------------------------------
    # CRIAR
    # -------------------------------------------
    def adicionar_favorecido(self, dados):
        try:
            return self.service.criar(dados, self.get_id_usuario())
        except Exception as e:
            logger.error("Erro ao adicionar favorecido: %s", e, exc_info=True)
            raise e  # 🔥 não esconder erro

    # -------------------------------------------
    # ATUALIZAR
    # -------------------------------------------
    def atualizar_favorecido(self, id_favorecido, dados):
        try:
            return self.service.atualizar(
                id_favorecido,
                dados,
                self.get_id_usuario()
            )
        except Exception as e:
            logger.error("Erro ao atualizar favorecido: %s", e, exc_info=True)
            raise e

    # -------------------------------------------
    # DELETAR
    # -------------------------------------------
    def remover_favorecido(self, id_favorecido):
        try:
            return self.service.deletar(
                id_favorecido,
                self.get_id_usuario()
            )
        except Exception as e:
            logger.error("Erro ao remover favorecido: %s", e, exc_info=True)
            raise e

    # -------------------------------------------
    # RESOLVER (IA / IMPORTAÇÃO)
    # -------------------------------------------
    def resolver_favorecido(self, dados):
        try:
            return self.service.resolver_favorecido(
                dados,
                self.get_id_usuario()
            )
        except Exception as e:
            logger.error("Erro ao resolver favorecido: %s", e, exc_info=True)
            return None

    # -------------------------------------------
    # SESSION
    # -------------------------------------------
    def get_id_usuario(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")
        return usuario["ID_Usuario"]