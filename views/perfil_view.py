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
from core.i18n import t


class PerfilView(QWidget):
    """
    Tela de perfil do usuário logado.
    Exibe apenas informações da sessão atual.
    """

    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado.")

        # referências para retradução
        self._labels = {}

        self._init_ui()

        # reage à mudança de idioma
        Session.on_idioma_change(self._retranslate)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        # Título
        self.titulo = QLabel()
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setObjectName("pageTitle")
        self.layout.addWidget(self.titulo)

        # Grupo de dados
        self.grupo = QGroupBox()
        self.g_layout = QVBoxLayout(self.grupo)

        self.lbl_nome = QLabel()
        self.lbl_login = QLabel()
        self.lbl_email = QLabel()
        self.lbl_nivel = QLabel()

        self.g_layout.addWidget(self.lbl_nome)
        self.g_layout.addWidget(self.lbl_login)
        self.g_layout.addWidget(self.lbl_email)
        self.g_layout.addWidget(self.lbl_nivel)

        self.layout.addWidget(self.grupo)

        # Botão logout
        self.btn_logout = QPushButton()
        self.btn_logout.setObjectName("deleteButton")
        self.btn_logout.clicked.connect(self._confirmar_logout)
        self.layout.addWidget(self.btn_logout)

        self.layout.addStretch()

        # texto inicial
        self._retranslate(Session.get_config("idioma", "Português"))

    # --------------------------------------------------
    # TRADUÇÃO DINÂMICA
    # --------------------------------------------------
    def _retranslate(self, idioma):
        self.titulo.setText(t("Perfil do Usuário", idioma))
        self.grupo.setTitle(t("Dados da Conta", idioma))

        self.lbl_nome.setText(
            f"{t('Nome', idioma)}: {self.usuario.get('Nome', '-')}"
        )
        self.lbl_login.setText(
            f"{t('Login', idioma)}: {self.usuario.get('Login', '-')}"
        )
        self.lbl_email.setText(
            f"{t('E-mail', idioma)}: {self.usuario.get('Email', '-')}"
        )
        self.lbl_nivel.setText(
            f"{t('Nível de Acesso', idioma)}: {self.usuario.get('Nivel_Acesso', '-')}"
        )

        self.btn_logout.setText(t("Encerrar Sessão", idioma))

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    def _confirmar_logout(self):
        idioma = Session.get_config("idioma", "Português")

        confirm = QMessageBox.question(
            self,
            t("Encerrar Sessão", idioma),
            t("Deseja realmente sair do sistema?", idioma),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            self.logout_requested.emit()