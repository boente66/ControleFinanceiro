from PyQt5.QtWidgets import QApplication, QDialog
import sys
import logging

from core.config import carregar_config
from core.session import Session
from core.themes import get_theme

from views.login_dialog import LoginDialog
from views.main_view import MainView


logger = logging.getLogger(__name__)


def aplicar_tema(app, tema):
    
     # Aplica tema com fallback seguro
    
    try:
        style = get_theme(tema)

        if isinstance(style, str) and style.strip():
            app.setStyleSheet(style)
        else:
            logger.warning(f"Tema inválido retornado: {tema}")
            app.setStyleSheet("")

    except Exception:
        logger.exception("Erro ao aplicar tema")
        app.setStyleSheet("")


def main():
    app = QApplication(sys.argv)

    # ==============================
    # CONFIGURAÇÕES
    # ==============================
    config = carregar_config()
    Session.load_config(config)

    # ==============================
    # TEMA INICIAL
    # ==============================
    tema = config.get("tema", "Claro")
    aplicar_tema(app, tema)

    # 🔥 REATIVIDADE DO TEMA
    Session.on_tema_change(lambda novo: aplicar_tema(app, novo))

    # ==============================
    # LOGIN
    # ==============================
    login = LoginDialog()

    if login.exec_() == QDialog.Accepted:
        usuario = login.usuario_logado

        if not usuario:
            logger.error("Login retornou sem usuário")
            sys.exit(0)

        # garante sessão
        Session.set_usuario(usuario)

        try:
            main_window = MainView(usuario)
            main_window.show()
        except Exception:
            logger.exception("Erro ao abrir MainView")
            sys.exit(1)

        sys.exit(app.exec_())

    # cancelado
    sys.exit(0)


if __name__ == "__main__":
    main()
