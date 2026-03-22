from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QMessageBox, QGroupBox
)
from PyQt5.QtCore import QDate
from controllers.user_controller import UserController


class CadastroUsuarioDialog(QDialog):
    """
    Diálogo de cadastro de usuário.
    Responsável apenas por UI e validações básicas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Usuário")
        self.setMinimumSize(420, 420)

        self.controller = UserController()

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Grupo de informações
        # -------------------------------------------------
        group = QGroupBox("Informações do Usuário")
        form = QFormLayout()

        self.nome_input = QLineEdit()
        form.addRow("Nome:", self.nome_input)

        self.nascimento_input = QDateEdit(QDate.currentDate())
        self.nascimento_input.setCalendarPopup(True)
        form.addRow("Data de Nascimento:", self.nascimento_input)

        self.sexo_input = QComboBox()
        self.sexo_input.addItems(["Masculino", "Feminino", "Outro"])
        form.addRow("Sexo:", self.sexo_input)

        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Somente números")
        form.addRow("CPF:", self.cpf_input)

        self.telefone_input = QLineEdit()
        form.addRow("Telefone:", self.telefone_input)

        self.celular_input = QLineEdit()
        form.addRow("Celular:", self.celular_input)

        self.email_input = QLineEdit()
        form.addRow("Email:", self.email_input)

        self.login_input = QLineEdit()
        form.addRow("Login:", self.login_input)

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        form.addRow("Senha:", self.senha_input)

        self.nivel_input = QComboBox()
        self.nivel_input.addItems(["usuario", "admin"])
        form.addRow("Nível de Acesso:", self.nivel_input)

        group.setLayout(form)
        layout.addWidget(group)

        # -------------------------------------------------
        # Botão Salvar
        # -------------------------------------------------
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.clicked.connect(self.salvar_usuario)
        layout.addWidget(self.btn_salvar)

    # -----------------------------------------------------------
    # SALVAR USUÁRIO
    # -----------------------------------------------------------
    def salvar_usuario(self):
        nome = self.nome_input.text().strip()
        login = self.login_input.text().strip()
        senha = self.senha_input.text().strip()
        email = self.email_input.text().strip()

        # validações básicas
        if not nome or not login or not senha or not email:
            QMessageBox.warning(self, "Erro", "Preencha os campos obrigatórios.")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Erro", "E-mail inválido.")
            return

        dados = {
            "Nome": nome,
            "DataNascimento": self.nascimento_input.date().toString("yyyy-MM-dd"),
            "Sexo": self.sexo_input.currentText(),
            "CPF": self.cpf_input.text().strip(),
            "Telefone": self.telefone_input.text().strip(),
            "Celular": self.celular_input.text().strip(),
            "Email": email,
            "Login": login,
            "Senha": senha,
            "Nivel_Acesso": self.nivel_input.currentText()
        }

        try:
            sucesso = self.controller.register_user(dados)

            if sucesso:
                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Usuário cadastrado com sucesso!"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Usuário Existente",
                    "Já existe um usuário com este login ou e-mail."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao cadastrar usuário:\n{e}"
            )