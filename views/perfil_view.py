import logging
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

from core.session import Session
from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class PerfilView(QWidget):
    """
    Tela de perfil do usuário logado.
    """

    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado.")

        # 🔥 título base
        self.setWindowTitle("Perfil do Usuário")

        self._init_ui()

        # 🔥 reatividade necessária (dados dinâmicos)
        TranslatorApp.bind(self._on_translate, self)

        self._update_user_info()

    # --------------------------------------------------
    # REATIVIDADE
    # --------------------------------------------------
    def _on_translate(self, *_):
        self._update_user_info()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # TÍTULO
        self.titulo = QLabel("Perfil do Usuário")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo)

        # GRUPO
        self.grupo = QGroupBox("Dados da Conta")
        self.g_layout = QVBoxLayout(self.grupo)
        self.layout.addWidget(self.grupo)

        # Labels dinâmicos
        self.lbl_nome = QLabel()
        self.lbl_login = QLabel()
        self.lbl_email = QLabel()
        self.lbl_nivel = QLabel()

        self.g_layout.addWidget(self.lbl_nome)
        self.g_layout.addWidget(self.lbl_login)
        self.g_layout.addWidget(self.lbl_email)
        self.g_layout.addWidget(self.lbl_nivel)

        # BOTÃO LOGOUT
        self.btn_logout = QPushButton("Encerrar Sessão")
        self.btn_logout.setObjectName("deleteButton")
        self.btn_logout.clicked.connect(self._confirmar_logout)
        self.layout.addWidget(self.btn_logout)

        self.layout.addStretch()

    # --------------------------------------------------
    # DADOS DINÂMICOS
    # --------------------------------------------------
    def _update_user_info(self):

        self.lbl_nome.setText(
            f"{TranslatorApp.get('Nome')}: {self.usuario.get('Nome', '-')}"
        )
        self.lbl_login.setText(
            f"{TranslatorApp.get('Login')}: {self.usuario.get('Login', '-')}"
        )
        self.lbl_email.setText(
            f"{TranslatorApp.get('E-mail')}: {self.usuario.get('Email', '-')}"
        )
        self.lbl_nivel.setText(
            f"{TranslatorApp.get('Nível de Acesso')}: "
            f"{self.usuario.get('Nivel_Acesso', '-')}"
        )

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    def _confirmar_logout(self):

        confirm = QMessageBox.question(
            self,
            TranslatorApp.get("Encerrar Sessão"),
            TranslatorApp.get("Deseja realmente sair do sistema?"),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            self.logout_requested.emit()
