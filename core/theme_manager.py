import logging
from PyQt5.QtWidgets import QApplication
from core.themes import get_theme, V
from core.session import Session

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Gerenciador central de temas da aplicação.
    Controla aplicação visual e fornece acesso a tokens semânticos.
    """

    # ======================================================
    # APLICAÇÃO DE TEMA
    # ======================================================

    @staticmethod
    def aplicar_tema(nome_tema: str, app: QApplication = None) -> bool:
        try:
            css = get_theme(nome_tema)
            app = app or QApplication.instance()

            if app is None:
                logger.error("Nenhuma instância QApplication ativa.")
                return False

            app.setStyleSheet(css)
            logger.info(f"Tema aplicado: {nome_tema}")
            return True

        except Exception:
            logger.exception(f"Falha ao aplicar tema '{nome_tema}'")
            return False

    # ======================================================
    # ESTADO DO TEMA
    # ======================================================

    @staticmethod
    def tema_atual() -> str:
        usuario = Session.get_usuario()
        if not usuario:
            return "Claro"
        return usuario.get("Tema", "Claro")

    @staticmethod
    def definir_tema(nome_tema: str) -> bool:
        usuario = Session.get_usuario()
        if not usuario:
            return False

        usuario["Tema"] = nome_tema
        return ThemeManager.aplicar_tema(nome_tema)

    @staticmethod
    def alternar_tema() -> str:
        atual = ThemeManager.tema_atual()
        novo = "Escuro" if atual == "Claro" else "Claro"

        ThemeManager.definir_tema(novo)
        return novo

    # ======================================================
    # TOKENS VISUAIS (ACESSO SEMÂNTICO)
    # ======================================================

    @staticmethod
    def get_color(token: str) -> str:
        """
        Retorna cor baseada no tema atual.
        Exemplo:
            ThemeManager.get_color("success")
            ThemeManager.get_color("border")
        """
        tema = ThemeManager.tema_atual()

        if tema == "Escuro":
            return V.get(f"{token}_dark")
        return V.get(f"{token}_light")

    # ======================================================
    # CORES FINANCEIRAS (USO LOCAL)
    # ======================================================

    @staticmethod
    def get_finance_color(tipo: str) -> str:
        """
        Retorna cor financeira baseada no tema atual.
        tipo:
            - "receita"
            - "despesa"
        """
        if tipo not in ("receita", "despesa"):
            logger.warning(f"Tipo financeiro inválido: {tipo}")
            return None

        tema = ThemeManager.tema_atual()

        if tema == "Escuro":
            return V.get(f"{tipo}_dark")
        return V.get(f"{tipo}_light")