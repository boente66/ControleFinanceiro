import logging
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QInputDialog, QWidget, QHBoxLayout,
    QToolButton
)
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QIcon

from views.cadastro_usuario_dialog import CadastroUsuarioDialog
from controllers.user_controller import UserController
from utilitarios.ion_path import IonPath
from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 🔥 título base
        self.setWindowTitle("Login")

        self.setMinimumSize(360, 300)
        self.setModal(True)

        self.controller = UserController()
        self.usuario_logado = None

        self._icon_cache = {}

        self._build_ui()
        self._connect_events()

        self.login_input.setFocus()

        
        TranslatorApp.bind(self._atualizar_textos,self)
        self._atualizar_textos()


    def _atualizar_textos(self, *_):

        self.setWindowTitle(
            TranslatorApp.get("Login")
        )

        self.lbl_login.setText(
            TranslatorApp.get("Usuário ou e-mail:")
        )

        self.login_input.setPlaceholderText(
            TranslatorApp.get("Login ou e-mail")
        )

        self.lbl_senha.setText(
            TranslatorApp.get("Senha:")
        )

        self.senha_input.setPlaceholderText(
            TranslatorApp.get("Digite sua senha")
        )

        self.btn_login.setText(
            TranslatorApp.get("Entrar")
        )

        self.btn_cadastrar.setText(
            TranslatorApp.get("Cadastrar")
        )

        self.btn_recuperar.setText(
            TranslatorApp.get("Esqueci minha senha")
        )

    

    # =====================================================
    # ICON
    # =====================================================
    def _icon(self, nome):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        try:
            path = IonPath.resource("assets", "icons", f"{nome}.svg")
            icon = QIcon(path) if os.path.exists(path) else QIcon()

            self._icon_cache[nome] = icon
            return icon

        except Exception:
            logger.exception(f"Erro ao carregar ícone: {nome}")
            return QIcon()

    # =====================================================
    # UI
    # =====================================================
    def _build_ui(self):

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # LOGIN
        self.lbl_login = QLabel("Usuário ou e-mail:")
        layout.addWidget(self.lbl_login)

        container_login = QWidget()
        login_layout = QHBoxLayout(container_login)
        login_layout.setContentsMargins(0, 0, 0, 0)

        icon_user = QLabel()
        icon_user.setPixmap(self._icon("user").pixmap(16, 16))

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Login ou e-mail")
        

        login_layout.addWidget(icon_user)
        login_layout.addWidget(self.login_input)
        layout.addWidget(container_login)

        # SENHA
        self.lbl_senha = QLabel("Senha:")
        layout.addWidget(self.lbl_senha)

        container_senha = QWidget()
        senha_layout = QHBoxLayout(container_senha)
        senha_layout.setContentsMargins(0, 0, 0, 0)

        icon_lock = QLabel()
        icon_lock.setPixmap(self._icon("lock").pixmap(16, 16))

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Digite sua senha")
        

        self.btn_toggle = QToolButton()
        self.btn_toggle.setIcon(self._icon("eye"))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("border: none;")
        self.btn_toggle.setIconSize(QSize(18, 18))
        

        senha_layout.addWidget(icon_lock)
        senha_layout.addWidget(self.senha_input)
        senha_layout.addWidget(self.btn_toggle)

        layout.addWidget(container_senha)

        # BOTÕES
        self.btn_login = QPushButton("Entrar")
        self.btn_login.setObjectName("primaryButton")
        self.btn_login.setIcon(self._icon("login"))
        self.btn_login.setIconSize(QSize(18, 18))
        layout.addWidget(self.btn_login)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("secondaryButton")
        self.btn_cadastrar.setIcon(self._icon("add_user"))
        self.btn_cadastrar.setIconSize(QSize(18, 18))
        layout.addWidget(self.btn_cadastrar)

        self.btn_recuperar = QPushButton("Esqueci minha senha")
        self.btn_recuperar.setFlat(True)
        self.btn_recuperar.setCursor(Qt.PointingHandCursor)
        self.btn_recuperar.setStyleSheet("text-align:left;")
        layout.addWidget(self.btn_recuperar)

    def _connect_events(self):
        self.login_input.returnPressed.connect(self._autenticar)
        self.senha_input.returnPressed.connect(self._autenticar)

        self.btn_toggle.clicked.connect(self._toggle_password)
        self.btn_login.clicked.connect(self._autenticar)
        self.btn_cadastrar.clicked.connect(self._abrir_cadastro)
        self.btn_recuperar.clicked.connect(self._recuperar_senha)
        

    # =====================================================
    # TOGGLE PASSWORD
    # =====================================================
    def _toggle_password(self):
        if self.senha_input.echoMode() == QLineEdit.Password:
            self.senha_input.setEchoMode(QLineEdit.Normal)
            self.btn_toggle.setIcon(self._icon("eye_off"))
        else:
            self.senha_input.setEchoMode(QLineEdit.Password)
            self.btn_toggle.setIcon(self._icon("eye"))

    # =====================================================
    # AUTENTICAÇÃO
    # =====================================================
    @pyqtSlot()
    def _autenticar(self):

        login = self.login_input.text().strip()
        senha = self.senha_input.text().strip()

        if not login or not senha:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Por favor, preencha todos os campos.")
            )
            return

        try:
            usuario = self.controller.authenticate_user(login, senha)

            if usuario:
                self.usuario_logado = usuario
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Erro"),
                    TranslatorApp.get("Usuário ou senha inválidos.")
                )

        except Exception:
            logger.exception("Erro ao autenticar usuário")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro interno ao autenticar usuário.")
            )

    # =====================================================
    # CADASTRO
    # =====================================================
    def _abrir_cadastro(self):
        dialog = CadastroUsuarioDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.login_input.clear()
            self.senha_input.clear()

    # =====================================================
    # RECUPERAÇÃO
    # =====================================================
    def _recuperar_senha(self):

        login_or_email, ok = QInputDialog.getText(
            self,
            TranslatorApp.get("Recuperar Senha"),
            TranslatorApp.get("Digite seu login ou e-mail:")
        )

        if not ok or not login_or_email.strip():
            return

        try:
            token = self.controller.request_password_reset(
                login_or_email.strip()
            )

            if not token:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Erro"),
                    TranslatorApp.get("Usuário não encontrado ou erro ao gerar token.")
                )
                return

            QMessageBox.information(
                self,
                TranslatorApp.get("Token Gerado"),
                f"{TranslatorApp.get('Token gerado')}: \n\n{token}"
            )

            token_digitado, ok = QInputDialog.getText(
                self,
                TranslatorApp.get("Confirmar Token"),
                TranslatorApp.get("Digite o token recebido:")
            )

            if not ok:
                return

            nova_senha, ok = QInputDialog.getText(
                self,
                TranslatorApp.get("Nova Senha"),
                TranslatorApp.get("Digite sua nova senha:"),
                QLineEdit.Password
            )

            if not ok:
                return

            sucesso = self.controller.reset_password_with_token(
                token_digitado.strip(),
                nova_senha.strip()
            )

            if sucesso:
                QMessageBox.information(
                    self,
                    TranslatorApp.get("Sucesso"),
                    TranslatorApp.get("Senha redefinida com sucesso.")
                )
            else:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Erro"),
                    TranslatorApp.get("Token inválido ou expirado.")
                )

        except Exception:
            logger.exception("Erro ao recuperar senha")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro interno ao recuperar senha.")
            )
    def closeEvent(self, event):

        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)