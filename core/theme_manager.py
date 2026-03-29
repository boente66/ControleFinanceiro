import logging
from PyQt5.QtWidgets import QApplication

from core.themes import get_theme, V, ALIASES
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

            # 🔥 refresh visual garantido
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
    def _resolve_nome(nome: str) -> str:
        """
        Resolve aliases para nome real do tema.
        """
        if not isinstance(nome, str):
            return "Organizze Claro"

        nome = nome.strip()
        return ALIASES.get(nome, nome)

    @staticmethod
    def tema_atual() -> str:
        usuario = Session.get_usuario()

        if usuario and usuario.get("Tema"):
            return usuario["Tema"]

        return Session.get_config("tema", "Claro")

    @staticmethod
    def definir_tema(nome_tema: str) -> bool:
        usuario = Session.get_usuario()

        if usuario:
            usuario["Tema"] = nome_tema

        Session.set_config("tema", nome_tema)

        return ThemeManager.aplicar_tema(nome_tema)

    # ======================================================
    # DARK MODE DETECTION (CORRIGIDO)
    # ======================================================
    @staticmethod
    def is_dark() -> bool:
        nome = ThemeManager._resolve_nome(ThemeManager.tema_atual())

        return any(x in nome.lower() for x in ["dark", "escuro", "vscode"])

    # ======================================================
    # ALTERNAR TEMA (GENÉRICO)
    # ======================================================
    @staticmethod
    def alternar_tema() -> str:
        atual = ThemeManager.tema_atual()
        atual_resolvido = ThemeManager._resolve_nome(atual)

        if ThemeManager.is_dark():
            novo = "Organizze Claro"
        else:
            novo = "Organizze Escuro"

        ThemeManager.definir_tema(novo)
        return novo

    # ======================================================
    # TOKENS VISUAIS
    # ======================================================
    @staticmethod
    def get_color(token: str) -> str:
        tema = ThemeManager.tema_atual()

        chave = (
            f"{token}_dark"
            if ThemeManager.is_dark()
            else f"{token}_light"
        )

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
            return ThemeManager.get_color("success")

        elif tipo == "despesa":
            return ThemeManager.get_color("danger")

        logger.warning(f"Tipo financeiro inválido: {tipo}")
        return "#000000"