from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QHBoxLayout
)

from controllers.account_controller import AccountController
from core.session import Session
from core.translator_app import TranslatorApp


class EditarContaDialog(QDialog):

    def __init__(self, parent=None, conta=None):
        super().__init__(parent)

        if not conta:
            raise ValueError("Conta é obrigatória")

        self.conta = conta
        self.usuario = Session.get_usuario()
        self.id_usuario = self.usuario["ID_Usuario"]

        self.controller = AccountController()

        # 🔥 título reativo
        TranslatorApp.window_title(self, "Editar Conta")

        self.setMinimumWidth(400)

        self._init_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Nome
        self.lbl_nome = QLabel()
        TranslatorApp.text(self.lbl_nome, "Nome da Conta")
        layout.addWidget(self.lbl_nome)

        self.nome_edit = QLineEdit(self.conta.get("Nome_Conta", ""))
        layout.addWidget(self.nome_edit)

        # Instituição
        self.lbl_inst = QLabel()
        TranslatorApp.text(self.lbl_inst, "Instituição")
        layout.addWidget(self.lbl_inst)

        self.inst_edit = QLineEdit(self.conta.get("Instituicao", ""))
        layout.addWidget(self.inst_edit)

        # Tipo
        self.lbl_tipo = QLabel()
        TranslatorApp.text(self.lbl_tipo, "Tipo da Conta")
        layout.addWidget(self.lbl_tipo)

        self.tipo_combo = QComboBox()
        TranslatorApp.combo(
            self.tipo_combo,
            ["Corrente", "Poupança", "Investimento"]
        )
        self.tipo_combo.setCurrentText(self.conta.get("Tipo", "Corrente"))
        layout.addWidget(self.tipo_combo)

        # Botões
        botoes = QHBoxLayout()

        self.salvar_btn = QPushButton()
        TranslatorApp.text(self.salvar_btn, "Salvar")

        self.cancelar_btn = QPushButton()
        TranslatorApp.text(self.cancelar_btn, "Cancelar")

        self.salvar_btn.clicked.connect(self.salvar)
        self.cancelar_btn.clicked.connect(self.reject)

        botoes.addWidget(self.salvar_btn)
        botoes.addWidget(self.cancelar_btn)

        layout.addLayout(botoes)

    # --------------------------------------------------
    # SALVAR
    # --------------------------------------------------
    def salvar(self):
        nome = self.nome_edit.text().strip()
        instituicao = self.inst_edit.text().strip()
        tipo = self.tipo_combo.currentText()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("O nome da conta é obrigatório.")
            )
            return

        try:
            self.controller.update_account(
                id_conta=self.conta["ID_Conta"],
                nome=nome,
                instituicao=instituicao,
                tipo=tipo,
                id_usuario=self.id_usuario
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Conta atualizada com sucesso.")
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )