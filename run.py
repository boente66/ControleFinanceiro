# -*- coding: utf-8 -*-
import sys
import logging
import traceback

from PyQt5.QtWidgets import QApplication, QDialog

from core.config import carregar_config
from core.session import Session
from core.themes import get_theme
from core.translator_app import TranslatorApp

from views.login_dialog import LoginDialog
from views.main_view import MainView


# ============================================================
# LOG GLOBAL
# ============================================================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# CAPTURA GLOBAL DE ERRO
# ============================================================
def excecao_global(exctype, value, tb):
    print("\n========== ERRO GLOBAL ==========")
    traceback.print_exception(exctype, value, tb)
    input("\nPressione ENTER para sair...")


sys.excepthook = excecao_global


# ============================================================
# TEMA
# ============================================================
def aplicar_tema(tema, app=None):
    try:
        app = app or QApplication.instance()

        if not isinstance(app, QApplication):
            logger.error("App inválido: %s", type(app))
            return

        style = get_theme(tema)

        if isinstance(style, str) and style.strip():
            app.setStyleSheet(style)
        else:
            logger.warning("Tema inválido: %s", tema)
            app.setStyleSheet("")

    except Exception:
        logger.exception("Erro ao aplicar tema")

        if isinstance(app, QApplication):
            app.setStyleSheet("")


# ============================================================
# MAIN
# ============================================================
def main():
    print(">>> INICIANDO APLICAÇÃO")

    app = QApplication(sys.argv)

    try:
        # ==============================
        # CONFIG
        # ==============================
        print(">>> Carregando config")
        config = carregar_config()
        Session.load_config(config)

        # ==============================
        # TRADUÇÕES
        # ==============================
        print(">>> Carregando traduções")
        TranslatorApp.initialize()

        # ==============================
        # IDIOMA
        # ==============================
        print(">>> Aplicando idioma")
        Session.on_idioma_change(TranslatorApp.set_language)
        TranslatorApp.set_language(
            Session.get_config("idioma", "pt")
        )

        # ==============================
        # TEMA
        # ==============================
        print(">>> Aplicando tema")
        tema = Session.get_config("tema", "Claro")
        aplicar_tema(tema, app)

        def on_theme_change(novo_tema):
            aplicar_tema(novo_tema, app)

        Session.on_tema_change(on_theme_change)

        # ==============================
        # LOGIN
        # ==============================
        print(">>> Abrindo login")
        login = LoginDialog()

        if login.exec_() == QDialog.Accepted:
            print(">>> Login OK")

            usuario = login.usuario_logado

            if not usuario:
                raise ValueError("Login sem usuário")

            Session.set_usuario(usuario)

            print(">>> Abrindo MainView")

            main_window = MainView(usuario)
            main_window.show()

            print(">>> App rodando")

            return app.exec_()

        print(">>> Login cancelado")
        return 0

    except Exception:
        print("\n========== ERRO NO MAIN ==========")
        traceback.print_exc()
        input("\nPressione ENTER para sair...")
        return 1


# ============================================================
# ENTRYPOINT
# ============================================================
if __name__ == "__main__":
    sys.exit(main())
