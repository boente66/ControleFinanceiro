import logging

from services.argos_service import ArgosService
from core.session import Session
from core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class ConfiguracoesController:

    def __init__(self):
        self.argos_service = ArgosService()

    # ==================================================
    # CONFIG GERAL
    # ==================================================
    def obter_configuracoes(self):
        return {
            "tema": Session.get_config("tema"),
            "idioma": Session.get_config("idioma"),
            "moeda": Session.get_config("moeda")
        }

    # ==================================================
    # TEMA
    # ==================================================
    def set_tema(self, tema, app=None):
        return ThemeManager.definir_tema(tema, app)

    def get_tema(self):
        return Session.get_config("tema")

    # ==================================================
    # IDIOMA (🔥 CORRIGIDO)
    # ==================================================
    def set_idioma(self, idioma):
        try:
            Session.set_config("idioma", idioma)
            return True
        except Exception:
            logger.exception("Erro ao definir idioma")
            return False

    def get_idioma(self):
        return Session.get_config("idioma")

    # ==================================================
    # MOEDA
    # ==================================================
    def set_moeda(self, moeda):
        try:
            Session.set_config("moeda", moeda)
            return True
        except Exception:
            logger.exception("Erro ao definir moeda")
            return False

    def get_moeda(self):
        return Session.get_config("moeda")

    # ==================================================
    # TRADUÇÃO (🔥 CORRETO)
    # ==================================================
    def traduzir(self, texto):

        idioma = self.get_idioma()

        if not texto:
            return ""

        try:
            return self.argos_service.traduzir(
                texto,
                origem="pt",
                destino=idioma
            )
        except Exception:
            logger.exception("Erro ao traduzir texto")
            return texto
