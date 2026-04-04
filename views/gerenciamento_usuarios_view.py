from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from controllers.user_controller import UserController
from views.cadastro_usuario_dialog import CadastroUsuarioDialog

from core.translator_app import TranslatorApp


class GerenciamentoUsuariosView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.usuario_controller = UserController()

        # 🔥 título base
        self.setWindowTitle("Gerenciamento de Usuários")

        self._init_ui()

        self.lista_completa = []
        self.atualizar_tabela()

        # 🔥 tradução automática global
        TranslatorApp.enable_auto_translation(self)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        layout = QtWidgets.QVBoxLayout(self)

        # -------------------------------------------------
        # PESQUISA
        # -------------------------------------------------
        search_layout = QtWidgets.QHBoxLayout()

        self.lbl_search = QtWidgets.QLabel("Pesquisar:")

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Nome, e-mail ou nível")
        self.search_input.textChanged.connect(self.aplicar_filtro_pesquisa)

        search_layout.addWidget(self.lbl_search)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        # -------------------------------------------------
        # TABELA
        # -------------------------------------------------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome", "Email", "Administrador"]
        )

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table)

        # -------------------------------------------------
        # BOTÕES
        # -------------------------------------------------
        btn_layout = QtWidgets.QHBoxLayout()

        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.setObjectName("primaryButton")

        self.btn_edit = QtWidgets.QPushButton("Editar")
        self.btn_edit.setObjectName("menuButton")

        self.btn_delete = QtWidgets.QPushButton("Excluir")
        self.btn_delete.setObjectName("deleteButton")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

        # Conexões
        self.btn_add.clicked.connect(self.adicionar_usuario)
        self.btn_edit.clicked.connect(self.editar_usuario)
        self.btn_delete.clicked.connect(self.excluir_usuario)

    # ==================================================
    # CARREGAMENTO
    # ==================================================
    def atualizar_tabela(self):
        self.lista_completa = self.usuario_controller.get_all_users()
        self.preencher_tabela(self.lista_completa)

    def preencher_tabela(self, usuarios):
        self.table.setRowCount(len(usuarios))

        for row, user in enumerate(usuarios):

            self.table.setItem(
                row, 0,
                QtWidgets.QTableWidgetItem(str(user["ID_Usuario"]))
            )

            self.table.setItem(
                row, 1,
                QtWidgets.QTableWidgetItem(user["Nome"])
            )

            self.table.setItem(
                row, 2,
                QtWidgets.QTableWidgetItem(user["Email"])
            )

            admin = (
                TranslatorApp.get("Sim")
                if user["Nivel_Acesso"] == "admin"
                else TranslatorApp.get("Não")
            )

            self.table.setItem(
                row, 3,
                QtWidgets.QTableWidgetItem(admin)
            )

        self.table.resizeColumnsToContents()

    # ==================================================
    # FILTRO
    # ==================================================
    def aplicar_filtro_pesquisa(self):

        termo = self.search_input.text().lower().strip()

        if not termo:
            self.preencher_tabela(self.lista_completa)
            return

        filtrados = [
            u for u in self.lista_completa
            if termo in str(u["ID_Usuario"]).lower()
            or termo in u["Nome"].lower()
            or termo in u["Email"].lower()
            or termo in u["Nivel_Acesso"].lower()
        ]

        self.preencher_tabela(filtrados)

    # ==================================================
    # CRUD
    # ==================================================
    def adicionar_usuario(self):

        dialog = CadastroUsuarioDialog(self)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.atualizar_tabela()

    def editar_usuario(self):

        row = self.table.currentRow()

        if row < 0:
            QtWidgets.QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Selecione um usuário")
            )
            return

        user_id = int(self.table.item(row, 0).text())
        usuario = self.usuario_controller.get_user_by_id(user_id)

        dialog = CadastroUsuarioDialog(self)
        dialog.preencher_dados(usuario)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.atualizar_tabela()

    def excluir_usuario(self):

        row = self.table.currentRow()

        if row < 0:
            QtWidgets.QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Selecione um usuário")
            )
            return

        user_id = int(self.table.item(row, 0).text())

        confirm = QtWidgets.QMessageBox.question(
            self,
            TranslatorApp.get("Confirmar Exclusão"),
            TranslatorApp.get("Deseja realmente excluir este usuário"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm != QtWidgets.QMessageBox.Yes:
            return

        # 🔥 regra de negócio correta (executa após confirmação)
        if not self.usuario_controller.delete_user(user_id):
            QtWidgets.QMessageBox.critical(
                self,
                TranslatorApp.get("Restrição"),
                TranslatorApp.get("Não é possível excluir o único administrador restante")
            )
            return

        self.atualizar_tabela()