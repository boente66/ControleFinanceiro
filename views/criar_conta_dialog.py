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
from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class CriarContaDialog(QDialog):
    """
    Dialog responsável APENAS por coletar dados da UI
    e chamar o Controller.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = AccountController()

        # 🔥 título reativo
        TranslatorApp.window_title(self, "Criar Conta")

        self.setFixedSize(360, 260)

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Nome
        self.nome_input = QLineEdit()
        TranslatorApp.form(form, "Nome da Conta:", self.nome_input)

        # Instituição
        self.instituicao_input = QLineEdit()
        TranslatorApp.form(form, "Instituição:", self.instituicao_input)

        # Tipo
        self.tipo_combo = QComboBox()
        TranslatorApp.combo(
            self.tipo_combo,
            ["Corrente", "Poupança", "Investimento"]
        )
        TranslatorApp.form(form, "Tipo:", self.tipo_combo)

        # Saldo
        self.saldo_input = QLineEdit()
        TranslatorApp.placeholder(self.saldo_input, "0,00")
        TranslatorApp.form(form, "Saldo Inicial:", self.saldo_input)

        layout.addLayout(form)

        # Botões
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.buttons.accepted.connect(self._salvar)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

        # 🔥 tradução dos botões
        self.buttons.button(QDialogButtonBox.Ok).setText(
            TranslatorApp.get("Salvar")
        )
        self.buttons.button(QDialogButtonBox.Cancel).setText(
            TranslatorApp.get("Cancelar")
        )

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
            "ID_Usuario": usuario["ID_Usuario"],
        }

        try:
            self.controller.create_account(dados)

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Conta criada com sucesso."),
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                str(e)
            )

        except Exception:
            logger.exception("Erro ao criar conta")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Não foi possível criar a conta."),
            )
