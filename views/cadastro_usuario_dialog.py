from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QMessageBox, QGroupBox
)
from PyQt5.QtCore import QDate

from controllers.user_controller import UserController
from core.translator_app import TranslatorApp


class CadastroUsuarioDialog(QDialog):
    """
    Diálogo de cadastro de usuário.
    Responsável apenas por UI e validações básicas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # ✅ título reativo
        TranslatorApp.window_title(self, "Cadastro de Usuário")

        self.setMinimumSize(420, 420)

        self.controller = UserController()

        self._init_ui()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def _init_ui(self):

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Grupo
        # -------------------------------------------------
        self.group = QGroupBox()
        TranslatorApp.group(self.group, "Informações do Usuário")

        form = QFormLayout()

        self.nome_input = QLineEdit()
        TranslatorApp.form(form, "Nome:", self.nome_input)

        self.nascimento_input = QDateEdit(QDate.currentDate())
        self.nascimento_input.setCalendarPopup(True)
        TranslatorApp.form(form, "Data de Nascimento:", self.nascimento_input)

        self.sexo_input = QComboBox()
        TranslatorApp.combo(
            self.sexo_input,
            ["Masculino", "Feminino", "Outro"]
        )
        TranslatorApp.form(form, "Sexo:", self.sexo_input)

        self.cpf_input = QLineEdit()
        TranslatorApp.placeholder(self.cpf_input, "Somente números")
        TranslatorApp.form(form, "CPF:", self.cpf_input)

        self.telefone_input = QLineEdit()
        TranslatorApp.form(form, "Telefone:", self.telefone_input)

        self.celular_input = QLineEdit()
        TranslatorApp.form(form, "Celular:", self.celular_input)

        self.email_input = QLineEdit()
        TranslatorApp.form(form, "Email:", self.email_input)

        self.login_input = QLineEdit()
        TranslatorApp.form(form, "Login:", self.login_input)

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        TranslatorApp.form(form, "Senha:", self.senha_input)

        self.nivel_input = QComboBox()
        TranslatorApp.combo(self.nivel_input, ["usuario", "admin"])
        TranslatorApp.form(form, "Nível de Acesso:", self.nivel_input)

        self.group.setLayout(form)
        layout.addWidget(self.group)

        # -------------------------------------------------
        # Botão
        # -------------------------------------------------
        self.btn_salvar = QPushButton()
        self.btn_salvar.setObjectName("primaryButton")
        TranslatorApp.text(self.btn_salvar, "Salvar")
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

        # validações
        if not nome or not login or not senha or not email:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Preencha os campos obrigatórios")
            )
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("E-mail inválido")
            )
            return

        dados = {
            "Nome": nome,
            "DataNascimento": self.nascimento_input.date().toString("yyyy-MM-dd"),
            "Sexo": self.sexo_input.currentData(),
            "CPF": self.cpf_input.text().strip(),
            "Telefone": self.telefone_input.text().strip(),
            "Celular": self.celular_input.text().strip(),
            "Email": email,
            "Login": login,
            "Senha": senha,
            "Nivel_Acesso": self.nivel_input.currentData()
        }

        try:
            sucesso = self.controller.register_user(dados)

            if sucesso:
                QMessageBox.information(
                    self,
                    TranslatorApp.get("Sucesso"),
                    TranslatorApp.get("Usuário cadastrado com sucesso")
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Usuário Existente"),
                    TranslatorApp.get("Já existe um usuário com este login ou e-mail")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                f"{TranslatorApp.get('Erro ao cadastrar usuário')}:\n{e}"
            )