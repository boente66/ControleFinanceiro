import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox
)

from core.session import Session
from core.theme_manager import ThemeManager
from core.themes import available_themes
from core.translator_app import TranslatorApp
from controllers.user_controller import UserController

logger = logging.getLogger(__name__)


class ConfiguracoesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = UserController()

        self._init_ui()
        self._load_config()

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # título
        self.titulo_label = QLabel()
        self.titulo_label.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo_label)

        TranslatorApp.text(self.titulo_label, "Configurações")

        # idioma
        self.idioma_label = QLabel()
        self.layout.addWidget(self.idioma_label)

        TranslatorApp.text(self.idioma_label, "Idioma")

        self.idioma_combo = QComboBox()
        self.layout.addWidget(self.idioma_combo)

        TranslatorApp.combo(
            self.idioma_combo,
            ["Português", "Inglês"]
        )

        # tema
        self.tema_label = QLabel()
        self.layout.addWidget(self.tema_label)

        TranslatorApp.text(self.tema_label, "Tema")

        self.tema_combo = QComboBox()
        self.tema_combo.addItems(available_themes())
        self.layout.addWidget(self.tema_combo)

        # aplica tema em tempo real
        self.tema_combo.currentTextChanged.connect(
            lambda tema: ThemeManager.aplicar_tema(tema)
        )

        # moeda
        self.moeda_label = QLabel()
        self.layout.addWidget(self.moeda_label)

        TranslatorApp.text(self.moeda_label, "Moeda")

        self.moeda_combo = QComboBox()
        self.layout.addWidget(self.moeda_combo)

        TranslatorApp.combo(
            self.moeda_combo,
            ["BRL", "USD", "EUR"]
        )

        # botão salvar
        self.salvar_btn = QPushButton()
        self.salvar_btn.setObjectName("primaryButton")
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)
        self.layout.addWidget(self.salvar_btn)

        TranslatorApp.text(self.salvar_btn, "Salvar")

        self.layout.addStretch()

    # ==================================================
    # CARREGAR CONFIG
    # ==================================================
    def _load_config(self):

        idioma = Session.get_config("idioma", "Português")
        tema = ThemeManager.tema_atual()
        moeda = Session.get_config("moeda", "BRL")

        self.idioma_combo.setCurrentText(idioma)
        self.tema_combo.setCurrentText(tema)
        self.moeda_combo.setCurrentText(moeda)

    # ==================================================
    # SALVAR
    # ==================================================
    def salvar_configuracoes(self):

        idioma = self.idioma_combo.currentText()
        tema = self.tema_combo.currentText()
        moeda = self.moeda_combo.currentText()

        try:
            # sessão
            Session.set_config("idioma", idioma)
            Session.set_config("tema", tema)
            Session.set_config("moeda", moeda)

            # persistência
            self.controller.update_preferences(
                tema=tema,
                idioma=idioma
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Configurações"),
                TranslatorApp.get("Configurações salvas com sucesso")
            )

        except Exception:
            logger.exception("Erro ao salvar configurações")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro ao salvar configurações")
            )
