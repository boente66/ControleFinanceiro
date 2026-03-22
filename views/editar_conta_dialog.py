from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QHBoxLayout
)
from controllers.account_controller import AccountController
from core.session import Session


class EditarContaDialog(QDialog):
    def __init__(self, parent=None, conta=None):
        super().__init__(parent)

        if not conta:
            raise ValueError("Conta é obrigatória")

        self.conta = conta
        self.usuario = Session.get_usuario()
        self.id_usuario = self.usuario["ID_Usuario"]

        self.controller = AccountController()

        self.setWindowTitle("Editar Conta")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Nome
        layout.addWidget(QLabel("Nome da Conta:"))
        self.nome_edit = QLineEdit(conta.get("Nome_Conta", ""))
        layout.addWidget(self.nome_edit)

        # Instituição
        layout.addWidget(QLabel("Instituição:"))
        self.inst_edit = QLineEdit(conta.get("Instituicao", ""))
        layout.addWidget(self.inst_edit)

        # Tipo
        layout.addWidget(QLabel("Tipo da Conta:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Corrente", "Poupança", "Investimento"])
        self.tipo_combo.setCurrentText(conta.get("Tipo", "Corrente"))
        layout.addWidget(self.tipo_combo)

        # Botões
        botoes = QHBoxLayout()
        salvar_btn = QPushButton("Salvar")
        cancelar_btn = QPushButton("Cancelar")

        salvar_btn.clicked.connect(self.salvar)
        cancelar_btn.clicked.connect(self.reject)

        botoes.addWidget(salvar_btn)
        botoes.addWidget(cancelar_btn)

        layout.addLayout(botoes)

    def salvar(self):
        nome = self.nome_edit.text().strip()
        instituicao = self.inst_edit.text().strip()
        tipo = self.tipo_combo.currentText()

        if not nome:
            QMessageBox.warning(self, "Erro", "O nome da conta é obrigatório.")
            return

        try:
            self.controller.update_account(
                id_conta=self.conta["ID_Conta"],
                nome=nome,
                instituicao=instituicao,
                tipo=tipo,
                id_usuario=self.id_usuario
            )
            QMessageBox.information(self, "Sucesso", "Conta atualizada com sucesso.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))