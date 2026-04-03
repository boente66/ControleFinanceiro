from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QPushButton, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate
import logging

from controllers.transaction_controller import TransactionController
from controllers.account_controller import AccountController

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class TransferDialog(QDialog):
    """
    Diálogo responsável APENAS por coletar dados da UI
    e delegar a transferência ao controller.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        

        

        self.transaction_controller = TransactionController()
        self.account_controller = AccountController()

        self._is_bound = False

        # título traduzível
        TranslatorApp.window_title(self, "Transferir Saldo")

        self.setMinimumWidth(320)

        self._init_ui()
        self._apply_translation()

        self._carregar_contas()

        # 🔥 bind correto
        if not self._is_bound:
            TranslatorApp.bind(self._on_translate)
            self._is_bound = True

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # ORIGEM
        self.lbl_origem = QLabel()
        layout.addWidget(self.lbl_origem)

        self.origem_combo = QComboBox()
        layout.addWidget(self.origem_combo)

        # DESTINO
        self.lbl_destino = QLabel()
        layout.addWidget(self.lbl_destino)

        self.destino_combo = QComboBox()
        layout.addWidget(self.destino_combo)

        # VALOR
        self.lbl_valor = QLabel()
        layout.addWidget(self.lbl_valor)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0.01, 1_000_000.00)
        self.valor_input.setDecimals(2)
        layout.addWidget(self.valor_input)

        # DATA
        self.lbl_data = QLabel()
        layout.addWidget(self.lbl_data)

        self.data_input = QDateEdit(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        layout.addWidget(self.data_input)

        # BOTÃO
        self.btn_transferir = QPushButton()
        self.btn_transferir.clicked.connect(self._transferir)
        layout.addWidget(self.btn_transferir)

    # --------------------------------------------------
    # TRADUÇÃO
    # --------------------------------------------------
    def _on_translate(self, *_):
        self._apply_translation()
        self._carregar_contas()

    def _apply_translation(self):
        TranslatorApp.text(self.lbl_origem, "Conta de origem")
        TranslatorApp.text(self.lbl_destino, "Conta de destino")
        TranslatorApp.text(self.lbl_valor, "Valor")
        TranslatorApp.text(self.lbl_data, "Data")
        TranslatorApp.text(self.btn_transferir, "Transferir")

    # --------------------------------------------------
    # DADOS
    # --------------------------------------------------
    def _carregar_contas(self):
        self.origem_combo.clear()
        self.destino_combo.clear()

        contas = self.account_controller.get_all_accounts()

        for conta in contas:
            saldo = float(conta.get("Saldo_Atual", 0))

            texto = (
                f"{conta.get('Nome_Conta')} "
                f"({TranslatorApp.get('Saldo')}: {saldo:,.2f})"
            )

            # formato BR
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
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Selecione contas diferentes.")
            )
            return

        try:
            self.transaction_controller.transferir_saldo(
                id_origem=id_origem,
                id_destino=id_destino,
                valor=valor,
                data=data
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Transferência realizada com sucesso.")
            )

            self.accept()

        except ValueError as e:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                str(e)
            )

        except Exception:
            logger.exception("Erro ao transferir saldo")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro inesperado ao realizar transferência.")
            )