from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QPushButton, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate
import logging

from controllers.transaction_controller import TransactionController
from controllers.account_controller import AccountController
from core.session import Session

logger = logging.getLogger(__name__)


class TransferDialog(QDialog):
    """
    Diálogo responsável APENAS por coletar dados da UI
    e delegar a transferência ao controller.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Transferir Saldo")
        self.setMinimumWidth(320)

        self.usuario = Session.get_usuario()
        self.id_usuario = self.usuario["ID_Usuario"]
        self.transaction_controller = TransactionController()
        self.account_controller = AccountController()

        self._init_ui()
        self._carregar_contas()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Conta de origem:"))
        self.origem_combo = QComboBox()
        layout.addWidget(self.origem_combo)

        layout.addWidget(QLabel("Conta de destino:"))
        self.destino_combo = QComboBox()
        layout.addWidget(self.destino_combo)

        layout.addWidget(QLabel("Valor:"))
        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0.01, 1_000_000.00)
        self.valor_input.setDecimals(2)
        layout.addWidget(self.valor_input)

        layout.addWidget(QLabel("Data:"))
        self.data_input = QDateEdit(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        layout.addWidget(self.data_input)

        btn_transferir = QPushButton("Transferir")
        btn_transferir.clicked.connect(self._transferir)
        layout.addWidget(btn_transferir)

    # --------------------------------------------------
    # DADOS
    # --------------------------------------------------
    def _carregar_contas(self):
        self.origem_combo.clear()
        self.destino_combo.clear()

        contas = self.account_controller.get_all_accounts()

        for conta in contas:
            texto = f"{conta['Nome_Conta']} (Saldo: R$ {conta['Saldo_Atual']:,.2f})"
            texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")

            self.origem_combo.addItem(texto, conta["ID_Conta"])
            self.destino_combo.addItem(texto, conta["ID_Conta"])

    # --------------------------------------------------
    # AÇÃO
    # --------------------------------------------------
    def _transferir(self):
        id_origem = self.origem_combo.currentData()
        id_destino = self.destino_combo.currentData()
        valor = self.valor_input.value()
        data = self.data_input.date().toString("yyyy-MM-dd")

        if id_origem == id_destino:
            QMessageBox.warning(self, "Erro", "Selecione contas diferentes.")
            return

        try:
            self.transaction_controller.transferir_saldo(
                id_origem=id_origem,
                id_destino=id_destino,
                valor=valor,
                data=data,
                id_usuario=self.id_usuario
            )

            QMessageBox.information(
                self, "Sucesso", "Transferência realizada com sucesso."
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Atenção", str(e))

        except Exception:
            logger.exception("Erro ao transferir saldo")
            QMessageBox.critical(
                self, "Erro", "Erro inesperado ao realizar transferência."
            )