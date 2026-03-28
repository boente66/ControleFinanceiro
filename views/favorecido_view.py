import unicodedata

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QDialog,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from views.FavorecidoDialog import FavorecidoDialog
from controllers.favorecido_controller import FavorecidoController
from utilitarios.ion_path import IonPath


class FavorecidoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = FavorecidoController()

        self.setWindowTitle("Favorecidos")
        self.setMinimumSize(820, 600)

        # ================= LAYOUT PRINCIPAL =================
        main_layout = QVBoxLayout(self)

        # ---------- TÍTULO ----------
        title_label = QLabel("Favorecidos")
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; margin-bottom: 8px;"
        )
        main_layout.addWidget(title_label)

        # ---------- BOTÕES ----------
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Adicionar")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.setIcon(self._icon("add"))
        self.add_btn.clicked.connect(self.open_add_favorecido_dialog)

        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setObjectName("primaryButton")
        self.edit_btn.setIcon(self._icon("edit"))
        self.edit_btn.clicked.connect(self.edit_favorecido)

        self.delete_btn = QPushButton("Excluir")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setIcon(self._icon("delete"))
        self.delete_btn.clicked.connect(self.delete_favorecido)

        for btn in (self.add_btn, self.edit_btn, self.delete_btn):
            button_layout.addWidget(btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # ---------- BUSCA ----------
        search_layout = QHBoxLayout()

        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Nome, tipo, CPF/CNPJ, contato..."
        )
        self.search_input.textChanged.connect(self.apply_filter)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)

        main_layout.addLayout(search_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Nome", "Tipo", "CPF/CNPJ", "Contato"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_favorecido)

        main_layout.addWidget(self.table)

        self.load_favorecidos()

    # =====================================================
    # ICON UTIL
    # =====================================================
    def _icon(self, nome: str):
        """
        Retorna um QIcon baseado no nome do ícone.
        Ex: self._icon("add") -> assets/icons/add.svg
        """
        caminho = IonPath.resource("assets", "icons", f"{nome}.svg")
        return QIcon(caminho)

    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================
    def normalize(self, text):
        if not text:
            return ""

        text = str(text).lower().strip()
        text = unicodedata.normalize("NFD", text)
        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn"
        )
        return text.replace(" ", "")

    # =====================================================
    # FILTRO
    # =====================================================
    def apply_filter(self):

        termo = self.normalize(self.search_input.text())

        for row in range(self.table.rowCount()):

            if not termo:
                self.table.setRowHidden(row, False)
                continue

            linha_texto = ""

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                texto = item.text() if item else ""
                linha_texto += self.normalize(texto)

            self.table.setRowHidden(row, termo not in linha_texto)

    # =====================================================
    # SELEÇÃO
    # =====================================================
    def get_selected_favorecido(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Nenhum favorecido selecionado."
            )
            return None

        id_item = self.table.item(row, 0)
        id_fav = id_item.data(Qt.UserRole) if id_item else None

        return {
            "Nome": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
            "Tipo": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "CPF/CNPJ": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
            "Contato": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
            "ID_Favorecido": id_fav,
        }

    # =====================================================
    # CARREGAR
    # =====================================================
    def load_favorecidos(self):

        self.table.setRowCount(0)

        favorecidos = self.controller.listar_favorecidos()

        if not favorecidos:
            return

        for row, fav in enumerate(favorecidos):

            self.table.insertRow(row)

            nome_item = QTableWidgetItem(fav.get("Nome", ""))
            nome_item.setData(Qt.UserRole, fav.get("ID_Favorecido"))
            self.table.setItem(row, 0, nome_item)

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(fav.get("Tipo", ""))
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    fav.get("CPF") or fav.get("CNPJ") or ""
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    fav.get("Telefone_PF") or fav.get("Telefone_PJ") or ""
                )
            )

    # =====================================================
    # AÇÕES
    # =====================================================
    def open_add_favorecido_dialog(self):

        dialog = FavorecidoDialog(parent=self)

        if dialog.exec_() == QDialog.Accepted:
            self.load_favorecidos()

    def edit_favorecido(self):

        selecionado = self.get_selected_favorecido()
        if not selecionado:
            return

        dialog = FavorecidoDialog(
            parent=self,
            favorecido=selecionado
        )

        if dialog.exec_() == QDialog.Accepted:
            self.load_favorecidos()

    def delete_favorecido(self):

        selecionado = self.get_selected_favorecido()
        if not selecionado:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir '{selecionado['Nome']}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:

            sucesso = self.controller.remover_favorecido(
                selecionado["ID_Favorecido"]
            )

            if sucesso:
                self.load_favorecidos()
            else:
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Não foi possível excluir o favorecido."
                )