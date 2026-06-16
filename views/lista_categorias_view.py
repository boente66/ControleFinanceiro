import logging

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMenu,
    QAction,
    QDialog,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt

from controllers.category_controller import CategoryController
from views.categoria_dialog import CategoriaDialog
from views.subcategoria_dialog import SubcategoriaDialog

from core.translator_app import TranslatorApp

logging.basicConfig(level=logging.ERROR)


class ListaCategoriasView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = CategoryController()

        # 🔥 título base
        self.setWindowTitle("Listas e Categorias")

        self.resize(600, 400)

        self._init_ui()
        
        self.load_categorias()
       
        # 🔥 tradução automática global
        TranslatorApp.bind(self._atualizar_textos, self)
        self._atualizar_textos()

    def _atualizar_textos(self, *_):
        self.setWindowTitle(
            TranslatorApp.get("Listas e Categorias")
        )

        self.title.setText(
            TranslatorApp.get("Listas e Categorias")
        )

        self.btn_nova.setText(
            TranslatorApp.get("Nova Categoria")
        )

        self.btn_sub.setText(
            TranslatorApp.get("Nova Subcategoria")
        )

        self.btn_excluir.setText(
            TranslatorApp.get("Excluir")
        )

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # ---------------- TÍTULO ----------------
        self.title = QLabel("Listas e Categorias")
        self.title.setObjectName("title")
        layout.addWidget(self.title)

        # ---------------- BOTÕES ----------------
        buttons = QHBoxLayout()

        self.btn_nova = QPushButton("Nova Categoria")
        self.btn_sub = QPushButton("Nova Subcategoria")
        self.btn_excluir = QPushButton("Excluir")

        self.btn_nova.clicked.connect(self.add_categoria_dialog)
        self.btn_sub.clicked.connect(self.add_subcategoria_dialog)
        self.btn_excluir.clicked.connect(self.excluir_categoria)

        buttons.addWidget(self.btn_nova)
        buttons.addWidget(self.btn_sub)
        buttons.addWidget(self.btn_excluir)

        buttons.addStretch()
        layout.addLayout(buttons)

        # ---------------- TABELA ----------------
        self.table = QTableWidget()
        self.table.setColumnCount(3)

        self.table.setHorizontalHeaderLabels([
            "Categoria",
            "Tipo",
            "ID"
        ])

        self.table.setColumnHidden(2, True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

    # ==================================================
    # CARREGAR
    # ==================================================
    def load_categorias(self):
        try:
            self.table.setRowCount(0)

            categorias = self.controller.get_all_categories()

            if not categorias:
                self.table.setRowCount(1)
                self.table.setItem(
                    0, 0,
                    QTableWidgetItem(
                        TranslatorApp.get("Nenhum registro encontrado")
                    )
                )
                self.table.setSpan(0, 0, 1, 3)
                return

            self._popular_tabela(categorias)

        except Exception as e:
            logging.error(e)
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                f"{TranslatorApp.get('Erro ao carregar categorias')}:\n{e}",
            )

    # ==================================================
    # POPULAR TABELA
    # ==================================================
    def _popular_tabela(self, categorias, pai_id=None, indent=""):

        for categoria in categorias:

            if categoria["ID_Categoria_Pai"] == pai_id:

                row = self.table.rowCount()
                self.table.insertRow(row)

                item_nome = QTableWidgetItem(indent + categoria["Nome"])
                self.table.setItem(row, 0, item_nome)

                self.table.setItem(
                    row, 1,
                    QTableWidgetItem(categoria["Tipo"])
                )

                id_item = QTableWidgetItem(str(categoria["ID_Categoria"]))
                id_item.setData(Qt.UserRole, categoria["ID_Categoria"])
                self.table.setItem(row, 2, id_item)

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
                QMessageBox.critical(
                    self,
                    TranslatorApp.get("Erro"),
                    str(e)
                )

    # ==================================================
    # NOVA SUBCATEGORIA
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
                categoria_pai = self.controller.get_category_by_id(
                    data["ID_Categoria_Pai"]
                )

                if not categoria_pai:
                    QMessageBox.warning(
                        self,
                        TranslatorApp.get("Erro"),
                        TranslatorApp.get("Categoria pai não encontrada"),
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
                QMessageBox.critical(
                    self,
                    TranslatorApp.get("Erro"),
                    str(e)
                )

    # ==================================================
    # EXCLUIR
    # ==================================================
    def excluir_categoria(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Selecione uma categoria"),
            )
            return

        item_id = self.table.item(row, 2)

        if not item_id:
            return

        categoria_id = item_id.data(Qt.UserRole)

        try:
            ok, msg = self.controller.delete_category(categoria_id)

            if not ok:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Aviso"),
                    msg
                )
            else:
                self.load_categorias()

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )

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
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Selecione uma categoria"),
            )
            return

        item_id = self.table.item(row, 2)

        if not item_id:
            return

        categoria_id = item_id.data(Qt.UserRole)

        nome = self.table.item(row, 0).text().replace("└ ", "").strip()
        tipo = self.table.item(row, 1).text()

        dialog = CategoriaDialog(self, nome=nome, tipo=tipo)

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
                QMessageBox.critical(
                    self,
                    TranslatorApp.get("Erro"),
                    str(e)
                )
    

    # ======================================================
    # CICLO DE VIDA
    # ======================================================
    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)