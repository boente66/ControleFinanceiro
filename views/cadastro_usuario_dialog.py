from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QMessageBox, QGroupBox, QLabel
)
from PyQt5.QtCore import QDate

from controllers.user_controller import UserController
from core.translator_app import TranslatorApp


class CadastroUsuarioDialog(QDialog):
    """
    Diálogo de cadastro de usuário.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(420, 420)

        self.controller = UserController()
        self.usuario_edicao = None

        self._init_ui()

        # 🔥 título base
        self.setWindowTitle("Cadastro de Usuário")

        # 🔥 tradução automática global
        TranslatorApp.bind(self._atualizar_textos, self)
        self._atualizar_textos()
    
    #==================================================
    # REATIVIDADE
    #==================================================
    def _atualizar_textos(self, *_):
        self.setWindowTitle(TranslatorApp.get("Cadastro de Usuário"))
        self.lbl_nome.setText(TranslatorApp.get("Nome") + ":")
        self.lbl_nascimento.setText(TranslatorApp.get("Data de Nascimento") + ":")
        self.lbl_sexo.setText(TranslatorApp.get("Sexo") + ":")
        self.lbl_cpf.setText(TranslatorApp.get("CPF") + ":")
        self.lbl_tel.setText(TranslatorApp.get("Telefone") + ":")
        self.lbl_cel.setText(TranslatorApp.get("Celular") + ":")
        self.lbl_email.setText(TranslatorApp.get("Email") + ":")
        self.lbl_login.setText(TranslatorApp.get("Login") + ":")
        self.lbl_senha.setText(TranslatorApp.get("Senha") + ":")
        self.lbl_nivel.setText(TranslatorApp.get("Nível de Acesso") + ":")

        self.btn_salvar.setText(TranslatorApp.get("Salvar"))

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def _init_ui(self):

        layout = QVBoxLayout(self)

        # Grupo
        self.group = QGroupBox("Informações do Usuário")

        form = QFormLayout()

        # Nome
        self.lbl_nome = QLabel("Nome")
        self.nome_input = QLineEdit()
        form.addRow(self.lbl_nome, self.nome_input)

        # Nascimento
        self.lbl_nascimento = QLabel("Data de Nascimento")
        self.nascimento_input = QDateEdit(QDate.currentDate())
        self.nascimento_input.setCalendarPopup(True)
        form.addRow(self.lbl_nascimento, self.nascimento_input)

        # Sexo
        self.lbl_sexo = QLabel("Sexo")
        self.sexo_input = QComboBox()
        self.sexo_input.addItem("Masculino", "Masculino")
        self.sexo_input.addItem("Feminino", "Feminino")
        self.sexo_input.addItem("Outro", "Outro")
        form.addRow(self.lbl_sexo, self.sexo_input)

        # CPF
        self.lbl_cpf = QLabel("CPF")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Somente números")
        form.addRow(self.lbl_cpf, self.cpf_input)

        # Telefone
        self.lbl_tel = QLabel("Telefone")
        self.telefone_input = QLineEdit()
        form.addRow(self.lbl_tel, self.telefone_input)

        # Celular
        self.lbl_cel = QLabel("Celular")
        self.celular_input = QLineEdit()
        form.addRow(self.lbl_cel, self.celular_input)

        # Email
        self.lbl_email = QLabel("Email")
        self.email_input = QLineEdit()
        form.addRow(self.lbl_email, self.email_input)

        # Login
        self.lbl_login = QLabel("Login")
        self.login_input = QLineEdit()
        form.addRow(self.lbl_login, self.login_input)

        # Senha
        self.lbl_senha = QLabel("Senha")
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Obrigatória no cadastro")
        form.addRow(self.lbl_senha, self.senha_input)

        # Nível
        self.lbl_nivel = QLabel("Nível de Acesso")
        self.nivel_input = QComboBox()
        self.nivel_input.addItem("Usuário", "usuario")
        self.nivel_input.addItem("Admin", "admin")
        form.addRow(self.lbl_nivel, self.nivel_input)

        self.group.setLayout(form)
        layout.addWidget(self.group)

        # Botão salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.clicked.connect(self.salvar_usuario)

        layout.addWidget(self.btn_salvar)

    def preencher_dados(self, usuario):
        if not usuario:
            return

        self.usuario_edicao = usuario
        self.setWindowTitle("Editar Usuário")
        self.senha_input.setPlaceholderText("Deixe em branco para manter")

        self.nome_input.setText(usuario.get("Nome", ""))
        self.cpf_input.setText(usuario.get("CPF", "") or "")
        self.telefone_input.setText(usuario.get("Telefone", "") or "")
        self.celular_input.setText(usuario.get("Celular", "") or "")
        self.email_input.setText(usuario.get("Email", "") or "")
        self.login_input.setText(usuario.get("Login", "") or "")

        data = QDate.fromString(
            usuario.get("DataNascimento", "") or "",
            "yyyy-MM-dd"
        )
        if data.isValid():
            self.nascimento_input.setDate(data)

        self._selecionar_combo_por_data(
            self.sexo_input,
            usuario.get("Sexo")
        )
        self._selecionar_combo_por_data(
            self.nivel_input,
            usuario.get("Nivel_Acesso")
        )

    def _selecionar_combo_por_data(self, combo, valor):
        index = combo.findData(valor)
        if index >= 0:
            combo.setCurrentIndex(index)

    # -----------------------------------------------------------
    # SALVAR USUÁRIO
    # -----------------------------------------------------------
    def salvar_usuario(self):

        nome = self.nome_input.text().strip()
        login = self.login_input.text().strip()
        senha = self.senha_input.text().strip()
        email = self.email_input.text().strip()

        if not nome or not login or not email or (not self.usuario_edicao and not senha):
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
            if self.usuario_edicao:
                sucesso = self.controller.update_user(
                    self.usuario_edicao["ID_Usuario"],
                    dados
                )
                mensagem_sucesso = "Usuário atualizado com sucesso"
            else:
                sucesso = self.controller.register_user(dados)
                mensagem_sucesso = "Usuário cadastrado com sucesso"

            if sucesso:
                QMessageBox.information(
                    self,
                    TranslatorApp.get("Sucesso"),
                    TranslatorApp.get(mensagem_sucesso)
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
    #-----------------------------------------------------------
    # CICLO DE VIDA
    #-----------------------------------------------------------
    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)