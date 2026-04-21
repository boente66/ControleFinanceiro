from PyQt5.QtWidgets import QApplication, QDialog
import sys
import logging

from core.config import carregar_config
from core.session import Session
from core.themes import get_theme

from views.login_dialog import LoginDialog
from views.main_view import MainView

logger = logging.getLogger(__name__)


def aplicar_tema(tema, app=None):
    try:
        app = app or QApplication.instance()

        if not isinstance(app, QApplication):
            logger.error(f"App inválido: {type(app)}")
            return

        style = get_theme(tema)

        if isinstance(style, str) and style.strip():
            app.setStyleSheet(style)
        else:
            logger.warning(f"Tema inválido: {tema}")
            app.setStyleSheet("")

    except Exception:
        logger.exception("Erro ao aplicar tema")
        if isinstance(app, QApplication):
            app.setStyleSheet("")


def main():
    app = QApplication(sys.argv)

    # CONFIG
    config = carregar_config()
    Session.load_config(config)

    # TEMA INICIAL
    tema = Session.get_config("tema", "Claro")
    aplicar_tema(tema, app)

    # 🔥 CALLBACK SEGURO
    def on_theme_change(novo_tema):
        aplicar_tema(novo_tema, app)

    Session.on_tema_change(on_theme_change)

    # LOGIN
    login = LoginDialog()

    if login.exec_() == QDialog.Accepted:
        usuario = login.usuario_logado

        if not usuario:
            logger.error("Login sem usuário")
            sys.exit(0)

        Session.set_usuario(usuario)

        try:
            main_window = MainView(usuario)
            main_window.show()
        except Exception:
            logger.exception("Erro ao abrir MainView")
            sys.exit(1)

        sys.exit(app.exec_())

    sys.exit(0)


if __name__ == "__main__":
    main()
