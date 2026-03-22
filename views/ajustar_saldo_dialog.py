from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from controllers.account_controller import AccountController
from core.session import Session
import logging

logger = logging.getLogger(__name__)


class AjustarSaldoDialog(QDialog):
    """
    Diálogo para ajuste manual de saldo da conta.
    Responsável APENAS pela UI.
    """

    def __init__(self, parent=None, conta=None):
        super().__init__(parent)

        if not conta:
            raise ValueError("Conta não informada para ajuste de saldo.")

        self.conta = conta
        self.usuario = Session.get_usuario()
        self.controller = AccountController()

        self.setWindowTitle("Ajustar Saldo da Conta")
        self.setMinimumWidth(300)

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Conta: {self.conta.get('Nome_Conta', '')}"))

        layout.addWidget(QLabel("Novo saldo:"))
        self.saldo_edit = QLineEdit()
        self.saldo_edit.setPlaceholderText("Ex: 1500,00")
        layout.addWidget(self.saldo_edit)

        salvar_btn = QPushButton("Salvar Ajuste")
        salvar_btn.clicked.connect(self.salvar)
        layout.addWidget(salvar_btn)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        layout.addWidget(cancelar_btn)

    # --------------------------------------------------
    # AÇÃO
    # --------------------------------------------------
    def salvar(self):
        texto = self.saldo_edit.text().strip().replace(".", "").replace(",", ".")

        try:
            novo_saldo = float(texto)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Saldo inválido.")
            return

        try:
            self.controller.ajustar_saldo(
                id_conta=self.conta["ID_Conta"],
                novo_saldo=novo_saldo,
                id_usuario=self.usuario["ID_Usuario"]
            )

            QMessageBox.information(
                self, "Sucesso", "Saldo ajustado com sucesso."
            )
            self.accept()

        except Exception as e:
            logger.exception("Erro ao ajustar saldo")
            QMessageBox.critical(self, "Erro", str(e))