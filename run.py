from PyQt5.QtWidgets import QApplication, QDialog
import sys
import logging

from core.config import carregar_config
from core.session import Session
from core.themes import get_theme

from views.login_dialog import LoginDialog
from views.main_view import MainView


logger = logging.getLogger(__name__)


def main():
    app = QApplication(sys.argv)

    # ==============================
    # CARREGAR CONFIGURAÇÕES
    # ==============================
    config = carregar_config()
    Session.load_config(config)

    # ==============================
    # APLICAR TEMA
    # ==============================
    tema = config.get("tema", "Claro")

    try:
        style = get_theme(tema)

        # Garantia de segurança
        if isinstance(style, str) and style.strip():
            app.setStyleSheet(style)
        else:
            logger.warning(f"Tema inválido retornado: {tema}")

    except Exception as e:
        logger.exception("Erro ao aplicar tema")
        print("Erro ao aplicar tema:", e)

    # ==============================
    # LOGIN
    # ==============================
    login = LoginDialog()

    if login.exec_() == QDialog.Accepted:
        usuario = login.usuario_logado

        # Segurança extra: garantir que Session tenha o usuário
        Session.set_usuario(usuario)

        main_window = MainView(usuario)
        main_window.show()

        sys.exit(app.exec_())

    else:
        # Se usuário cancelar login, encerra aplicação
        sys.exit(0)


if __name__ == "__main__":
    main()
