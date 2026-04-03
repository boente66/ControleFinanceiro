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

        self._is_bound = False

        # título
        TranslatorApp.window_title(self, "Perfil do Usuário")

        self._init_ui()
        self._apply_translation()
        self._update_user_info()

        # 🔥 bind correto
        if not self._is_bound:
            TranslatorApp.bind(self._on_translate)
            self._is_bound = True

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

        # GRUPO
        self.grupo = QGroupBox()
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
        self.btn_logout = QPushButton()
        self.btn_logout.setObjectName("deleteButton")
        self.btn_logout.clicked.connect(self._confirmar_logout)
        self.layout.addWidget(self.btn_logout)

        self.layout.addStretch()

    # --------------------------------------------------
    # TRADUÇÃO
    # --------------------------------------------------
    def _on_translate(self, *_):
        self._apply_translation()
        self._update_user_info()

    def _apply_translation(self):
        TranslatorApp.text(self.titulo, "Perfil do Usuário")
        TranslatorApp.group(self.grupo, "Dados da Conta")
        TranslatorApp.text(self.btn_logout, "Encerrar Sessão")

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
