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

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # TÍTULO
        self.titulo = QLabel()
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo)

        TranslatorApp.text(self.titulo, "Perfil do Usuário")

        # GRUPO
        self.grupo = QGroupBox()
        self.g_layout = QVBoxLayout(self.grupo)

        # Labels dinâmicos
        self.lbl_nome = QLabel()
        self.lbl_login = QLabel()
        self.lbl_email = QLabel()
        self.lbl_nivel = QLabel()

        self.g_layout.addWidget(self.lbl_nome)
        self.g_layout.addWidget(self.lbl_login)
        self.g_layout.addWidget(self.lbl_email)
        self.g_layout.addWidget(self.lbl_nivel)

        self.layout.addWidget(self.grupo)

        # 🔥 título do grupo traduzível
        TranslatorApp._bind(lambda idioma: self.grupo.setTitle(
            TranslatorApp.get("Dados da Conta")
        ))

        # 🔥 dados do usuário traduzíveis
        TranslatorApp._bind(self._update_user_info)

        # BOTÃO LOGOUT
        self.btn_logout = QPushButton()
        self.btn_logout.setObjectName("deleteButton")
        self.btn_logout.clicked.connect(self._confirmar_logout)
        self.layout.addWidget(self.btn_logout)

        TranslatorApp.text(self.btn_logout, "Encerrar Sessão")

        self.layout.addStretch()

    # --------------------------------------------------
    # DADOS DINÂMICOS (REATIVO)
    # --------------------------------------------------
    def _update_user_info(self, idioma):

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
            f"{TranslatorApp.get('Nível de Acesso')}: {self.usuario.get('Nivel_Acesso', '-')}"
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