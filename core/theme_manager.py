import logging
from PyQt5.QtWidgets import QApplication

from core.themes import get_theme, THEMES, V
from core.session import Session

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Gerenciador central de temas da aplicação.
    Compatível com: Claro, Escuro, Verde
    """

    DEFAULT = "Claro"

    # ======================================================
    # APLICAÇÃO DE TEMA
    # ======================================================
    @staticmethod
    def aplicar_tema(nome_tema: str = None, app: QApplication = None) -> bool:
        try:
            nome_tema = ThemeManager._normalizar(nome_tema)

            css = get_theme(nome_tema)
            app = app or QApplication.instance()

            if app is None:
                logger.error("Nenhuma instância QApplication ativa.")
                return False

            # 🔥 força refresh visual completo
            app.setStyleSheet("")
            app.setStyleSheet(css)

            logger.info(f"[Theme] Tema aplicado: {nome_tema}")
            return True

        except Exception:
            logger.exception(f"[Theme] Falha ao aplicar tema '{nome_tema}'")
            return False

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================
    @staticmethod
    def _normalizar(nome: str) -> str:
        if not isinstance(nome, str):
            return ThemeManager.tema_atual()

        nome = nome.strip()

        if nome not in THEMES:
            return ThemeManager.DEFAULT

        return nome

    # ======================================================
    # ESTADO DO TEMA
    # ======================================================
    @staticmethod
    def tema_atual() -> str:
        usuario = Session.get_usuario()

        if usuario and usuario.get("Tema"):
            return usuario["Tema"]

        return Session.get_config("tema", ThemeManager.DEFAULT)

    @staticmethod
    def definir_tema(nome_tema: str, app: QApplication = None) -> bool:
        nome_tema = ThemeManager._normalizar(nome_tema)

        usuario = Session.get_usuario()

        if usuario:
            usuario["Tema"] = nome_tema

        Session.set_config("tema", nome_tema)

        return ThemeManager.aplicar_tema(nome_tema, app)

    # ======================================================
    # DETECÇÃO DE TEMA
    # ======================================================
    @staticmethod
    def is_dark() -> bool:
        return ThemeManager.tema_atual() == "Escuro"

    @staticmethod
    def is_light() -> bool:
        return ThemeManager.tema_atual() == "Claro"

    @staticmethod
    def is_green() -> bool:
        return ThemeManager.tema_atual() == "Verde"

    # ======================================================
    # ALTERNAR TEMA
    # ======================================================
    @staticmethod
    def alternar_tema(app: QApplication = None) -> str:
        atual = ThemeManager.tema_atual()

        ordem = ["Claro", "Escuro", "Verde"]

        try:
            idx = ordem.index(atual)
            novo = ordem[(idx + 1) % len(ordem)]
        except ValueError:
            novo = ThemeManager.DEFAULT

        ThemeManager.definir_tema(novo, app)
        return novo

    # ======================================================
    # LISTAGEM
    # ======================================================
    @staticmethod
    def temas_disponiveis() -> list:
        return list(THEMES.keys())

    # ======================================================
    # TOKENS VISUAIS
    # ======================================================
    @staticmethod
    def get_color(token: str) -> str:
        """
        Busca cor baseada no tema atual
        Ex: primary, success, danger, bg, text...
        """

        tema = ThemeManager.tema_atual()

        # 🔥 tema verde usa base light com override
        if tema == "Escuro":
            chave = f"{token}_dark"
        else:
            chave = f"{token}_light"

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
        if tipo == "receita":
            return V.get("success_light", "#16a34a")

        elif tipo == "despesa":
            return V.get("danger_light", "#dc2626")

        logger.warning(f"[Theme] Tipo financeiro inválido: {tipo}")
        return "#000000"