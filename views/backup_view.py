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
from core.translator_app import TranslatorApp


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

        # 🔥 título base
        self.setWindowTitle("Backup e Restauração")

        # 🔥 tradução automática global
        TranslatorApp.enable_auto_translation(self)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def _init_ui(self):
        self.layout = QVBoxLayout(self)

        self.titulo = QLabel("Backup e Restauração")
        self.titulo.setObjectName("pageTitle")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.titulo)

        self.label_senha = QLabel("Senha do Backup")

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Digite a senha")

        self.layout.addWidget(self.label_senha)
        self.layout.addWidget(self.senha_input)

        botoes = QHBoxLayout()

        self.btn_backup = QPushButton("Gerar Backup")
        self.btn_backup.setObjectName("primaryButton")
        self.btn_backup.clicked.connect(self.gerar_backup)

        self.btn_restaurar = QPushButton("Restaurar Backup")
        self.btn_restaurar.setObjectName("secondaryButton")
        self.btn_restaurar.clicked.connect(self.restaurar_backup)

        botoes.addWidget(self.btn_backup)
        botoes.addWidget(self.btn_restaurar)

        self.layout.addLayout(botoes)
        self.layout.addStretch()

    # -------------------------------------------------
    # UTIL
    # -------------------------------------------------
    def _bloquear_ui(self, estado=True):
        self.setEnabled(not estado)
        QApplication.setOverrideCursor(
            Qt.WaitCursor if estado else Qt.ArrowCursor
        )

    def _limpar_senha(self):
        self.senha_input.clear()

    # -------------------------------------------------
    # BACKUP
    # -------------------------------------------------
    def gerar_backup(self):

        senha = self.senha_input.text().strip()

        if not senha:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Informe uma senha para o backup."),
            )
            return

        destino = QFileDialog.getExistingDirectory(
            self,
            TranslatorApp.get("Selecionar pasta para salvar o backup"),
        )

        if not destino:
            return

        self._bloquear_ui(True)

        try:
            arquivo = self.controller.criar_backup(destino, senha)

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Backup gerado com sucesso") + f":\n{arquivo}",
            )

        except Exception as e:
            self.logger.exception("Erro ao gerar backup")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )

        finally:
            self._bloquear_ui(False)
            self._limpar_senha()

    # -------------------------------------------------
    # RESTAURAÇÃO
    # -------------------------------------------------
    def restaurar_backup(self):

        senha = self.senha_input.text().strip()

        if not senha:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Informe a senha do backup."),
            )
            return

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            TranslatorApp.get("Selecionar arquivo de backup"),
            "",
            f"{TranslatorApp.get('Backup')} (*.kp);;{TranslatorApp.get('Todos os arquivos')} (*)",
        )

        if not arquivo:
            return

        confirm = QMessageBox.question(
            self,
            TranslatorApp.get("Confirmação"),
            TranslatorApp.get(
                "Restaurar um backup irá substituir os dados atuais.\nDeseja continuar?"
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
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get(
                    "Backup restaurado com sucesso.\nReinicie o sistema."
                ),
            )

        except Exception as e:
            self.logger.exception("Erro ao restaurar backup")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )

        finally:
            self._bloquear_ui(False)
            self._limpar_senha()
