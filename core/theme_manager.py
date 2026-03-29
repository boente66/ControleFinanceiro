import logging
from PyQt5.QtWidgets import QApplication
from core.themes import get_theme, V
from core.session import Session

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Gerenciador central de temas da aplicação.
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

            # 🔥 força refresh visual
            app.setStyleSheet("")
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

        if usuario and usuario.get("Tema"):
            return usuario["Tema"]

        # 🔥 fallback global
        return Session.get_config("tema", "Claro")

    @staticmethod
    def definir_tema(nome_tema: str) -> bool:
        usuario = Session.get_usuario()

        if usuario:
            usuario["Tema"] = nome_tema

        # 🔥 também salva globalmente
        Session.set_config("tema", nome_tema)

        return ThemeManager.aplicar_tema(nome_tema)

    @staticmethod
    def alternar_tema() -> str:
        atual = ThemeManager.tema_atual()

        if atual in ("Escuro", "Organizze Escuro", "VSCode"):
            novo = "Claro"
        else:
            novo = "Escuro"

        ThemeManager.definir_tema(novo)
        return novo

    # ======================================================
    # TOKENS VISUAIS
    # ======================================================
    @staticmethod
    def get_color(token: str) -> str:
        """
        Retorna cor baseada no tema atual com fallback seguro.
        """
        tema = ThemeManager.tema_atual()

        chave = f"{token}_dark" if "Escuro" in tema or tema == "VSCode" else f"{token}_light"

        cor = V.get(chave)

        if not cor:
            logger.warning(f"[Theme] Token não encontrado: {chave}")
            return "#000000"

        return cor

    # ======================================================
    # CORES FINANCEIRAS
    # ======================================================
    @staticmethod
    def get_finance_color(tipo: str) -> str:
        """
        Tipo:
            - receita
            - despesa
        """
        if tipo == "receita":
            return ThemeManager.get_color("success")

        elif tipo == "despesa":
            return ThemeManager.get_color("danger")

        logger.warning(f"Tipo financeiro inválido: {tipo}")
        return "#000000"

    # ======================================================
    # UTIL EXTRA (OPCIONAL)
    # ======================================================
    @staticmethod
    def is_dark() -> bool:
        tema = ThemeManager.tema_atual()
        return "Escuro" in tema or tema == "VSCode"