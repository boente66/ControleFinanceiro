from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QApplication
)

from core.session import Session
from core.i18n import t
from core.theme_manager import ThemeManager
from controllers.user_controller import UserController


class ConfiguracoesView(QWidget):
    """
    Tela de Configurações do Usuário

    Responsável por:
    - Idioma
    - Tema
    - Moeda
    - Persistência por usuário (BD)
    - Aplicação dinâmica do tema
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado")

        self.usuario_id = self.usuario["ID_Usuario"]
        self.controller = UserController()

        self._init_ui()

        # escuta mudança de idioma em tempo real
        Session.on_idioma_change(self._retranslate_ui)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # título
        self.titulo_label = QLabel()
        self.titulo_label.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo_label)

        # -------------------------
        # Idioma
        # -------------------------
        self.idioma_label = QLabel()
        self.layout.addWidget(self.idioma_label)

        self.idioma_combo = QComboBox()
        self.idioma_combo.addItems(["Português", "Inglês"])
        self.idioma_combo.setCurrentText(
            Session.get_config("idioma", "Português")
        )
        self.layout.addWidget(self.idioma_combo)

        # -------------------------
        # Tema
        # -------------------------
        self.tema_label = QLabel()
        self.layout.addWidget(self.tema_label)

        self.tema_combo = QComboBox()
        self.tema_combo.addItems(["Claro", "Escuro"])
        self.tema_combo.setCurrentText(
            Session.get_config("tema", "Claro")
        )
        self.layout.addWidget(self.tema_combo)

        # -------------------------
        # Moeda
        # -------------------------
        self.moeda_label = QLabel()
        self.layout.addWidget(self.moeda_label)

        self.moeda_combo = QComboBox()
        self.moeda_combo.addItems(["BRL", "USD", "EUR"])
        self.moeda_combo.setCurrentText(
            Session.get_config("moeda", "BRL")
        )
        self.layout.addWidget(self.moeda_combo)

        # -------------------------
        # Botão salvar
        # -------------------------
        self.salvar_btn = QPushButton()
        self.salvar_btn.setObjectName("primaryButton")
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)
        self.layout.addWidget(self.salvar_btn)

        self.layout.addStretch()

        # aplica textos iniciais
        self._retranslate_ui(Session.get_config("idioma"))

    # --------------------------------------------------
    # TRADUÇÃO DINÂMICA
    # --------------------------------------------------
    def _retranslate_ui(self, idioma):
        self.titulo_label.setText(t("Configurações", idioma))
        self.idioma_label.setText(t("Idioma", idioma))
        self.tema_label.setText(t("Tema", idioma))
        self.moeda_label.setText(t("Moeda", idioma))
        self.salvar_btn.setText(t("Salvar", idioma))

    # --------------------------------------------------
    # SALVAR CONFIGURAÇÕES
    # --------------------------------------------------
    def salvar_configuracoes(self):
        idioma = self.idioma_combo.currentText()
        tema = self.tema_combo.currentText()
        moeda = self.moeda_combo.currentText()

        # -------------------------
        # Atualiza sessão (memória)
        # -------------------------
        Session.set_config("idioma", idioma)
        Session.set_config("tema", tema)
        Session.set_config("moeda", moeda)

        # -------------------------
        # Persiste no banco (usuário)
        # -------------------------
        sucesso = self.controller.update_preferences(
            self.usuario_id,
            tema=tema,
            idioma=idioma
        )

        if not sucesso:
            QMessageBox.critical(
                self,
                t("Erro", idioma),
                t("Erro ao salvar configurações", idioma)
            )
            return

        # -------------------------
        # Aplica tema global
        # -------------------------
        app = QApplication.instance()
        if app:
            ThemeManager.aplicar_tema(tema, app)

        QMessageBox.information(
            self,
            t("Configurações", idioma),
            t("Configurações salvas com sucesso", idioma)
        )
