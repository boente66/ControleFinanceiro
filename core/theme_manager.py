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

            if not isinstance(app, QApplication):
                raise TypeError(f"Aplicação inválida: {type(app)}")
            

            app.setStyleSheet(css or "")

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
            return ThemeManager.DEFAUT

        nome = nome.strip()

        if nome not in THEMES:
            return ThemeManager.DEFAULT

        return nome

    # ======================================================
    # ESTADO
    # ======================================================
    @staticmethod
    def tema_atual() -> str:
        usuario = Session.get_usuario()

        tema = None

        if isinstance(usuario, dict):
            tema = usuario.get("Tema")
        if not isinstance(tema, str) or not tema.strip():
            tema = Session.get_config("tema", ThemeManager.DEFAULT)

        if tema not in THEMES:
            tema = ThemeManager.DEFAULT

        return tema

    @staticmethod
    def definir_tema(nome_tema: str, app: QApplication = None) -> bool:
        nome_tema = ThemeManager._normalizar(nome_tema)

        usuario = Session.get_usuario()


        if usuario:
            usuario["Tema"] = nome_tema

        Session.set_config("tema", nome_tema)

        return ThemeManager.aplicar_tema(nome_tema, app)

    # ======================================================
    # DETECÇÃO
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
    # ALTERNAR
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
    # 🎨 TOKEN UNIVERSAL
    # ======================================================
    @staticmethod
    def get_color(token: str) -> str:
        """
        Retorna cor baseada no tema atual
        """

        tema = ThemeManager.tema_atual()

        # direto do dicionário
        if token in V:
            return V[token]

        # variação por tema
        if tema == "Escuro":
            chave = f"{token}_dark"
        else:
            chave = f"{token}_light"

        cor = V.get(chave)

        if cor:
            return cor

        logger.warning(f"[Theme] Token não encontrado: {token}")
        return "#000000"

    # ======================================================
    # 💰 CORES FINANCEIRAS
    # ======================================================
    @staticmethod
    def get_finance_color(tipo: str) -> str:
        tipo = (tipo or "").lower()

        if tipo in ("receita", "entrada", "ganho"):
            return ThemeManager.get_color("success")

        elif tipo in ("despesa", "saida", "gasto"):
            return ThemeManager.get_color("danger")

        elif tipo in ("saldo", "info", "neutro"):
            return ThemeManager.get_color("primary")

        logger.warning(f"[Theme] Tipo financeiro inválido: {tipo}")
        return "#000000"

    # ======================================================
    # 📊 CORES PARA GRÁFICOS
    # ======================================================
    @staticmethod
    def get_chart_colors() -> dict:
        """
        Paleta padrão para gráficos baseada no tema
        """

        tema = ThemeManager.tema_atual()

        if tema == "Escuro":
            return {
                "receita": "#22c55e",
                "despesa": "#ef4444",
                "saldo": "#3b82f6",
                "grid": "#2a2f3a",
                "text": "#e6eef8"
            }

        elif tema == "Verde":
            return {
                "receita": "#16a34a",
                "despesa": "#dc2626",
                "saldo": "#14532d",
                "grid": "#d1fae5",
                "text": "#052e16"
            }

        # Claro (default)
        return {
            "receita": "#16a34a",
            "despesa": "#dc2626",
            "saldo": "#2563eb",
            "grid": "#e5e7eb",
            "text": "#111827"
        }