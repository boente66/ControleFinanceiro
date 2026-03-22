from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QApplication
)
from PyQt5.QtCore import Qt
import logging

from controllers.backup_controller import BackupController
from core.session import Session
from core.i18n import t


class BackupView(QWidget):
    """
    Tela de Backup e Restauração do Sistema
    """

    def __init__(self, parent=None, usuario=None, *args, **kwargs):
        super().__init__(parent)

        self.usuario = (
            usuario
            or Session.get_usuario()
            or getattr(parent, "usuario", None)
            or {}
        )

        self.logger = logging.getLogger(__name__)
        self.controller = BackupController()

        self.setMinimumWidth(420)

        self._init_ui()
        Session.on_idioma_change(self._retranslate)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        self.titulo = QLabel()
        self.titulo.setObjectName("pageTitle")
        self.titulo.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.titulo)

        self.label_senha = QLabel()

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("********")

        self.layout.addWidget(self.label_senha)
        self.layout.addWidget(self.senha_input)

        botoes = QHBoxLayout()

        self.btn_backup = QPushButton()
        self.btn_backup.setObjectName("primaryButton")
        self.btn_backup.clicked.connect(self.gerar_backup)

        self.btn_restaurar = QPushButton()
        self.btn_restaurar.setObjectName("secondaryButton")
        self.btn_restaurar.clicked.connect(self.restaurar_backup)

        botoes.addWidget(self.btn_backup)
        botoes.addWidget(self.btn_restaurar)

        self.layout.addLayout(botoes)
        self.layout.addStretch()

        self._retranslate(Session.get_config("idioma", "Português"))

    # -------------------------------------------------
    # TRADUÇÃO
    # -------------------------------------------------
    def _retranslate(self, idioma):
        self.titulo.setText(t("Backup e Restauração", idioma))
        self.label_senha.setText(t("Senha do Backup", idioma))
        self.btn_backup.setText(t("Gerar Backup", idioma))
        self.btn_restaurar.setText(t("Restaurar Backup", idioma))

    # -------------------------------------------------
    # UTIL
    # -------------------------------------------------
    def _bloquear_ui(self, estado=True):
        self.setEnabled(not estado)
        QApplication.setOverrideCursor(Qt.WaitCursor if estado else Qt.ArrowCursor)

    def _limpar_senha(self):
        self.senha_input.clear()

    # -------------------------------------------------
    # BACKUP
    # -------------------------------------------------
    def gerar_backup(self):
        idioma = Session.get_config("idioma", "Português")
        senha = self.senha_input.text().strip()

        if not senha:
            QMessageBox.warning(
                self,
                t("Aviso", idioma),
                t("Informe uma senha para o backup.", idioma),
            )
            return

        destino = QFileDialog.getExistingDirectory(
            self,
            t("Selecionar pasta para salvar o backup", idioma),
        )

        if not destino:
            return

        self._bloquear_ui(True)

        try:
            arquivo = self.controller.criar_backup(destino, senha)

            QMessageBox.information(
                self,
                t("Sucesso", idioma),
                t("Backup gerado com sucesso", idioma) + f":\n{arquivo}",
            )

        except Exception as e:
            self.logger.exception("Erro ao gerar backup")
            QMessageBox.critical(self, t("Erro", idioma), str(e))

        finally:
            self._bloquear_ui(False)
            self._limpar_senha()

    # -------------------------------------------------
    # RESTAURAÇÃO
    # -------------------------------------------------
    def restaurar_backup(self):
        idioma = Session.get_config("idioma", "Português")
        senha = self.senha_input.text().strip()

        if not senha:
            QMessageBox.warning(
                self,
                t("Aviso", idioma),
                t("Informe a senha do backup.", idioma),
            )
            return

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            t("Selecionar arquivo de backup", idioma),
            "",
            "Backup (*.kp);;Todos os arquivos (*)",
        )

        if not arquivo:
            return

        confirm = QMessageBox.question(
            self,
            t("Confirmação", idioma),
            t(
                "Restaurar um backup irá substituir os dados atuais.\nDeseja continuar?",
                idioma,
            ),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm != QMessageBox.Yes:
            return

        self._bloquear_ui(True)

        try:
            self.controller.restaurar_backup(arquivo, senha)

            QMessageBox.information(
                self,
                t("Sucesso", idioma),
                t("Backup restaurado com sucesso.\nReinicie o sistema.", idioma),
            )

        except Exception as e:
            self.logger.exception("Erro ao restaurar backup")
            QMessageBox.critical(self, t("Erro", idioma), str(e))

        finally:
            self._bloquear_ui(False)
            self._limpar_senha()
