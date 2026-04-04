import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QApplication
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

        # 🔥 título base (auto traduzido)
        self.setWindowTitle("Configurações")

        self._init_ui()
        self._load_config()

        # 🔥 ativa tradução automática global
        TranslatorApp.enable_auto_translation(self)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # =====================
        # TÍTULO
        # =====================
        self.titulo_label = QLabel("Configurações")
        self.titulo_label.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo_label)

        # =====================
        # IDIOMA
        # =====================
        self.idioma_label = QLabel("Idioma")
        self.layout.addWidget(self.idioma_label)

        self.idioma_combo = QComboBox()
        self.layout.addWidget(self.idioma_combo)

        idiomas = ["Português", "Inglês", "Espanhol"]

        self.idioma_combo.blockSignals(True)
        self.idioma_combo.clear()

        for i in idiomas:
            self.idioma_combo.addItem(i, i)

        self.idioma_combo.blockSignals(False)

        self.idioma_combo.currentIndexChanged.connect(self._on_idioma_changed)

        # =====================
        # TEMA
        # =====================
        self.tema_label = QLabel("Tema")
        self.layout.addWidget(self.tema_label)

        self.tema_combo = QComboBox()
        self.layout.addWidget(self.tema_combo)

        self.tema_combo.blockSignals(True)
        self.tema_combo.clear()
        self.tema_combo.addItems(available_themes())
        self.tema_combo.blockSignals(False)

        self.tema_combo.currentTextChanged.connect(self._on_tema_changed)

        # =====================
        # MOEDA
        # =====================
        self.moeda_label = QLabel("Moeda")
        self.layout.addWidget(self.moeda_label)

        self.moeda_combo = QComboBox()
        self.layout.addWidget(self.moeda_combo)

        moedas = ["BRL", "USD", "EUR"]

        for m in moedas:
            self.moeda_combo.addItem(m, m)

        # =====================
        # BOTÃO SALVAR
        # =====================
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.setObjectName("primaryButton")
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)
        self.layout.addWidget(self.salvar_btn)

        self.layout.addStretch()

    # ==================================================
    # EVENTOS
    # ==================================================
    def _on_idioma_changed(self):
        idioma = self.idioma_combo.currentData()

        if not idioma:
            return

        try:
            # 🔥 troca instantânea global
            TranslatorApp.set_language(idioma)
        except Exception:
            logger.exception("Erro ao trocar idioma")

    def _on_tema_changed(self, tema):
        if not tema:
            return

        try:
            # 🔥 aplicação correta (ThemeManager já resolve app internamente)
            ThemeManager.definir_tema(tema)
        except Exception:
            logger.exception("Erro ao trocar tema")

    # ==================================================
    # LOAD CONFIG
    # ==================================================
    def _load_config(self):

        idioma = Session.get_config("idioma", "Português")
        tema = ThemeManager.tema_atual()
        moeda = Session.get_config("moeda", "BRL")

        # 🔥 evita disparar eventos durante load
        self.idioma_combo.blockSignals(True)
        self.tema_combo.blockSignals(True)
        self.moeda_combo.blockSignals(True)

        self._set_combo_by_data(self.idioma_combo, idioma)
        self.tema_combo.setCurrentText(tema)
        self._set_combo_by_data(self.moeda_combo, moeda)

        self.idioma_combo.blockSignals(False)
        self.tema_combo.blockSignals(False)
        self.moeda_combo.blockSignals(False)

    # ==================================================
    # UTIL
    # ==================================================
    def _set_combo_by_data(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    # ==================================================
    # SALVAR
    # ==================================================
    def salvar_configuracoes(self):

        idioma = self.idioma_combo.currentData()
        tema = self.tema_combo.currentText()
        moeda = self.moeda_combo.currentData()

        try:
            # 🔥 persistência local
            Session.set_config("idioma", idioma)
            Session.set_config("moeda", moeda)
            Session.set_config("tema", tema)

            # 🔥 persistência backend
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
