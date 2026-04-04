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

        if not self.usuario:
            raise ValueError("Usuário não autenticado")

        self.id_usuario = self.usuario["ID_Usuario"]

        self.controller = AccountController()

        # 🔥 título base (auto traduzido)
        self.setWindowTitle("Editar Conta")

        self.setMinimumWidth(400)

        self._init_ui()

        # 🔥 tradução automática global
        TranslatorApp.enable_auto_translation(self)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Nome
        self.lbl_nome = QLabel("Nome da Conta")
        layout.addWidget(self.lbl_nome)

        self.nome_edit = QLineEdit(self.conta.get("Nome_Conta", ""))
        self.nome_edit.setPlaceholderText("Ex: Conta Principal")
        layout.addWidget(self.nome_edit)

        # Instituição
        self.lbl_inst = QLabel("Instituição")
        layout.addWidget(self.lbl_inst)

        self.inst_edit = QLineEdit(self.conta.get("Instituicao", ""))
        self.inst_edit.setPlaceholderText("Ex: Nubank, Itaú")
        layout.addWidget(self.inst_edit)

        # Tipo
        self.lbl_tipo = QLabel("Tipo da Conta")
        layout.addWidget(self.lbl_tipo)

        self.tipo_combo = QComboBox()

        tipos = [
            ("Corrente", "Corrente"),
            ("Poupança", "Poupança"),
            ("Investimento", "Investimento"),
        ]

        for texto, valor in tipos:
            self.tipo_combo.addItem(texto, valor)

        # 🔥 usa DATA (correto)
        index = self.tipo_combo.findData(self.conta.get("Tipo", "Corrente"))
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)

        layout.addWidget(self.tipo_combo)

        # Botões
        botoes = QHBoxLayout()

        self.salvar_btn = QPushButton("Salvar")
        self.cancelar_btn = QPushButton("Cancelar")

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
        tipo = self.tipo_combo.currentData()

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