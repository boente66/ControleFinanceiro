import logging
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QComboBox,
)

from controllers.account_controller import AccountController
from core.session import Session


logger = logging.getLogger(__name__)


class CriarContaDialog(QDialog):
    """
    Dialog responsável APENAS por coletar dados da UI
    e chamar o Controller.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = AccountController()
       

        self.setWindowTitle("Criar Conta")
        self.setFixedSize(360, 260)

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.nome_input = QLineEdit()
        form.addRow("Nome da Conta:", self.nome_input)

        self.instituicao_input = QLineEdit()
        form.addRow("Instituição:", self.instituicao_input)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "Corrente",
            "Poupança",
            "Investimento"
        ])
        form.addRow("Tipo:", self.tipo_combo)

        self.saldo_input = QLineEdit()
        self.saldo_input.setPlaceholderText("0,00")
        form.addRow("Saldo Inicial:", self.saldo_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._salvar)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    # --------------------------------------------------
    # SALVAR
    # --------------------------------------------------
    def _salvar(self):
        usuario = Session.get_usuario()
        dados = {
            "Nome_Conta": self.nome_input.text().strip(),
            "Instituicao": self.instituicao_input.text().strip(),
            "Tipo": self.tipo_combo.currentText(),
            "Saldo_Atual": self.saldo_input.text().strip() or "0",
            "ID_Usuario": usuario["ID_Usuario"]
        }

        try:
            self.controller.create_account(dados)
            QMessageBox.information(
                self,
                "Sucesso",
                "Conta criada com sucesso."
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Atenção", str(e))

        except Exception as e:
            logger.exception("Erro ao criar conta")
            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível criar a conta."
            )
