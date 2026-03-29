from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from controllers.account_controller import AccountController
from core.translator_app import TranslatorApp

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
        self.controller = AccountController()

        self.setMinimumWidth(300)

        # 🔥 título traduzível
        TranslatorApp.window_title(self, "Ajustar Saldo da Conta")

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Conta
        self.lbl_conta = QLabel()
        layout.addWidget(self.lbl_conta)

        TranslatorApp._bind(self._update_conta_label)

        # Label saldo
        self.lbl_saldo = QLabel()
        layout.addWidget(self.lbl_saldo)
        TranslatorApp.text(self.lbl_saldo, "Novo saldo:")

        # Input
        self.saldo_edit = QLineEdit()
        TranslatorApp.placeholder(self.saldo_edit, "Ex: 1500,00")
        layout.addWidget(self.saldo_edit)

        # Botão salvar
        self.btn_salvar = QPushButton()
        self.btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(self.btn_salvar)
        TranslatorApp.text(self.btn_salvar, "Salvar Ajuste")

        # Botão cancelar
        self.btn_cancelar = QPushButton()
        self.btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(self.btn_cancelar)
        TranslatorApp.text(self.btn_cancelar, "Cancelar")

    # --------------------------------------------------
    # TEXTO DINÂMICO
    # --------------------------------------------------
    def _update_conta_label(self, idioma):
        self.lbl_conta.setText(
            f"{TranslatorApp.get('Conta')}: {self.conta.get('Nome_Conta', '')}"
        )

    # --------------------------------------------------
    # AÇÃO
    # --------------------------------------------------
    def salvar(self):
        texto = self.saldo_edit.text().strip().replace(".", "").replace(",", ".")

        try:
            novo_saldo = float(texto)
        except ValueError:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Saldo inválido.")
            )
            return

        try:
            # 🔥 SEM ID_USUARIO → controller resolve
            self.controller.ajustar_saldo(
                id_conta=self.conta["ID_Conta"],
                novo_saldo=novo_saldo
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Saldo ajustado com sucesso.")
            )
            self.accept()

        except Exception as e:
            logger.exception("Erro ao ajustar saldo")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )