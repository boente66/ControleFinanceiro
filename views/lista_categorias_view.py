from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMenu, QAction, QDialog, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt

from controllers.category_controller import CategoryController
from views.categoria_dialog import CategoriaDialog
from views.subcategoria_dialog import SubcategoriaDialog

import logging

logging.basicConfig(level=logging.ERROR)


class ListaCategoriasView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = CategoryController()
        self.setWindowTitle("Gerenciar Categorias")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # ---------------- TÍTULO ----------------
        title = QLabel("Listas e Categorias")
        title.setObjectName("title")
        layout.addWidget(title)

        # ---------------- BOTÕES ----------------
        buttons = QHBoxLayout()

        btn_nova = QPushButton("Nova Categoria")
        btn_nova.clicked.connect(self.add_categoria_dialog)
        buttons.addWidget(btn_nova)

        btn_sub = QPushButton("Nova Subcategoria")
        btn_sub.clicked.connect(self.add_subcategoria_dialog)
        buttons.addWidget(btn_sub)

        btn_excluir = QPushButton("Excluir")
        btn_excluir.clicked.connect(self.excluir_categoria)
        buttons.addWidget(btn_excluir)

        buttons.addStretch()
        layout.addLayout(buttons)

        # ---------------- TABELA ----------------
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Categoria", "Tipo", "ID"]
        )
        self.table.setColumnHidden(2, True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(
            self.show_context_menu
        )

        layout.addWidget(self.table)

        self.load_categorias()

    # ==================================================
    # CARREGAR
    # ==================================================
    def load_categorias(self):
        try:
            self.table.setRowCount(0)
            categorias = self.controller.get_all_categories()
            self._popular_tabela(categorias)
        except Exception as e:
            logging.error(e)
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao carregar categorias:\n{e}"
            )

    # ==================================================
    # POPULAR TABELA (RECURSIVO)
    # ==================================================
    def _popular_tabela(self, categorias, pai_id=None, indent=""):

        for categoria in categorias:

            if categoria["ID_Categoria_Pai"] == pai_id:

                row = self.table.rowCount()
                self.table.insertRow(row)

                # Nome
                item_nome = QTableWidgetItem(
                    indent + categoria["Nome"]
                )
                self.table.setItem(row, 0, item_nome)

                # Tipo
                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(categoria["Tipo"])
                )

                # ID oculto
                id_item = QTableWidgetItem(
                    str(categoria["ID_Categoria"])
                )
                id_item.setData(
                    Qt.UserRole,
                    categoria["ID_Categoria"]
                )
                self.table.setItem(row, 2, id_item)

                # Subcategorias recursivas
                self._popular_tabela(
                    categorias,
                    categoria["ID_Categoria"],
                    indent + "    └ "
                )

    # ==================================================
    # NOVA CATEGORIA
    # ==================================================
    def add_categoria_dialog(self):

        dialog = CategoriaDialog(self)

        if dialog.exec_() == QDialog.Accepted:

            data = dialog.get_data()

            try:
                self.controller.add_category(
                    data["Nome"],
                    data["Tipo"]
                )
                self.load_categorias()

            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    # ==================================================
    # NOVA SUBCATEGORIA (CORRIGIDO)
    # ==================================================
    def add_subcategoria_dialog(self):

        dialog = SubcategoriaDialog(
            parent=self,
            controller=self.controller,
            categoria_pai_id=None
        )

        if dialog.exec_() == QDialog.Accepted:

            data = dialog.get_data()

            try:
                # 🔎 Buscar categoria pai para herdar o tipo
                categoria_pai = self.controller.get_category_by_id(
                    data["ID_Categoria_Pai"]
                )

                if not categoria_pai:
                    QMessageBox.warning(
                        self,
                        "Erro",
                        "Categoria pai não encontrada."
                    )
                    return

                tipo = categoria_pai["Tipo"]

                self.controller.add_subcategory(
                    data["Nome"],
                    tipo,
                    data["ID_Categoria_Pai"]
                )

                self.load_categorias()

            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    # ==================================================
    # EXCLUIR
    # ==================================================
    def excluir_categoria(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione uma categoria."
            )
            return

        item_id = self.table.item(row, 2)

        if not item_id:
            return

        categoria_id = item_id.data(Qt.UserRole)

        try:
            ok, msg = self.controller.delete_category(
                categoria_id
            )

            if not ok:
                QMessageBox.warning(self, "Aviso", msg)
            else:
                self.load_categorias()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    # ==================================================
    # MENU CONTEXTO
    # ==================================================
    def show_context_menu(self, position):

        if self.table.currentRow() < 0:
            return

        menu = QMenu(self)

        copiar = QAction("Copiar", self)
        editar = QAction("Editar", self)
        excluir = QAction("Excluir", self)

        copiar.triggered.connect(self.copiar_categoria)
        editar.triggered.connect(self.editar_categoria)
        excluir.triggered.connect(self.excluir_categoria)

        menu.addAction(copiar)
        menu.addAction(editar)
        menu.addAction(excluir)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    # ==================================================
    # COPIAR
    # ==================================================
    def copiar_categoria(self):

        item = self.table.currentItem()

        if item:
            QApplication.clipboard().setText(
                item.text().replace("└ ", "").strip()
            )

    # ==================================================
    # EDITAR
    # ==================================================
    def editar_categoria(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione uma categoria."
            )
            return

        item_id = self.table.item(row, 2)

        if not item_id:
            return

        categoria_id = item_id.data(Qt.UserRole)

        nome = self.table.item(row, 0).text().replace("└ ", "").strip()
        tipo = self.table.item(row, 1).text()

        dialog = CategoriaDialog(
            self,
            nome=nome,
            tipo=tipo
        )

        if dialog.exec_() == QDialog.Accepted:

            data = dialog.get_data()

            try:
                self.controller.update_category(
                    categoria_id,
                    data["Nome"],
                    data["Tipo"]
                )
                self.load_categorias()

            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
