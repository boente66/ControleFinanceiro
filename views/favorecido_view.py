import unicodedata

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QDialog,
    QAbstractItemView,
    QComboBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from views.FavorecidoDialog import FavorecidoDialog
from controllers.favorecido_controller import FavorecidoController
from utilitarios.ion_path import IonPath

from core.translator_app import TranslatorApp


class FavorecidoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = FavorecidoController()

        self.setMinimumSize(820, 600)
        self.setWindowTitle("Favorecidos")

        # 🔥 estado
        self.data_original = []
        self.data_filtrada = []
        self.state = {
            "busca": "",
            "tipo": "ALL",
            "ordem": "AZ",
        }

        # 🔥 debounce busca
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filter)

        self._init_ui()
        self.load_favorecidos()

        TranslatorApp.enable_auto_translation(self)

    # =====================================================
    # UI
    # =====================================================
    def _init_ui(self):

        main_layout = QVBoxLayout(self)

        # ---------- TÍTULO ----------
        self.title_label = QLabel("Favorecidos")
        self.title_label.setObjectName("pageTitle")
        main_layout.addWidget(self.title_label)

        # ---------- BOTÕES ----------
        button_layout = QHBoxLayout()

        def btn(texto, icon, fn, style):
            b = QPushButton(texto)
            b.setObjectName(style)
            b.setIcon(self._icon(icon))
            b.clicked.connect(fn)
            return b

        self.add_btn = btn(
            "Adicionar", "add", self.open_add_favorecido_dialog, "primaryButton"
        )
        self.edit_btn = btn("Editar", "edit", self.edit_favorecido, "primaryButton")
        self.delete_btn = btn(
            "Excluir", "delete", self.delete_favorecido, "deleteButton"
        )

        for b in (self.add_btn, self.edit_btn, self.delete_btn):
            button_layout.addWidget(b)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # ---------- BUSCA + FILTRO ----------
        filtro_layout = QHBoxLayout()

        self.search_label = QLabel("Buscar:")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nome, tipo, CPF/CNPJ, contato...")
        self.search_input.textChanged.connect(self._on_busca_change)

        self.tipo_filtro = QComboBox()
        self.tipo_filtro.addItem("Todos", "ALL")
        self.tipo_filtro.addItem("Pessoa Física", "PF")
        self.tipo_filtro.addItem("Pessoa Jurídica", "PJ")
        self.tipo_filtro.currentIndexChanged.connect(self._on_tipo_change)

        filtro_layout.addWidget(self.search_label)
        filtro_layout.addWidget(self.search_input)
        filtro_layout.addWidget(QLabel("Tipo:"))
        filtro_layout.addWidget(self.tipo_filtro)

        main_layout.addLayout(filtro_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nome", "Tipo", "CPF/CNPJ", "Contato"])

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.edit_favorecido)

        main_layout.addWidget(self.table)

    # =====================================================
    # ICON
    # =====================================================
    def _icon(self, nome: str):
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
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        return text.replace(" ", "")

    # =====================================================
    # LOAD
    # =====================================================
    def load_favorecidos(self):
        self.data_original = self.controller.listar_favorecidos()
        self.apply_filter()

    # =====================================================
    # FILTRO
    # =====================================================
    def apply_filter(self):

        termo = self.normalize(self.state["busca"])
        tipo_filtro = self.state["tipo"]
        ordem = self.state["ordem"]

        filtrados = []

        for fav in self.data_original:

            nome = fav.get("Nome", "")
            tipo = fav.get("Tipo", "")
            doc = fav.get("CPF") or fav.get("CNPJ") or ""
            tel = fav.get("Telefone_PF") or fav.get("Telefone_PJ") or ""

            texto = self.normalize(nome + tipo + doc + tel)

            if termo and termo not in texto:
                continue

            if tipo_filtro != "ALL":
                if tipo_filtro == "PF" and tipo != "Pessoa Física":
                    continue
                if tipo_filtro == "PJ" and tipo != "Pessoa Jurídica":
                    continue

            filtrados.append(fav)

        if ordem == "AZ":
            filtrados.sort(key=lambda x: self.normalize(x.get("Nome", "")))
        elif ordem == "ZA":
            filtrados.sort(key=lambda x: self.normalize(x.get("Nome", "")), reverse=True)

        self.data_filtrada = filtrados
        self._render_table()

    # =====================================================
    # RENDER
    # =====================================================
    def _render_table(self):

        self.table.setRowCount(0)

        if not self.data_filtrada:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Nenhum registro encontrado"))
            self.table.setSpan(0, 0, 1, 4)
            return

        for row, fav in enumerate(self.data_filtrada):

            self.table.insertRow(row)

            tipo = fav.get("Tipo", "")
            icone = "👤" if tipo == "Pessoa Física" else "🏢"

            nome_item = QTableWidgetItem(f"{icone} {fav.get('Nome', '')}")
            nome_item.setData(Qt.UserRole, fav.get("ID_Favorecido"))

            self.table.setItem(row, 0, nome_item)
            self.table.setItem(row, 1, QTableWidgetItem(tipo))
            self.table.setItem(row, 2, QTableWidgetItem(fav.get("CPF") or fav.get("CNPJ") or ""))
            self.table.setItem(row, 3, QTableWidgetItem(fav.get("Telefone_PF") or fav.get("Telefone_PJ") or ""))

    # =====================================================
    # SELEÇÃO
    # =====================================================
    def get_selected_favorecido(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Nenhum favorecido selecionado."),
            )
            return None

        item = self.table.item(row, 0)
        id_fav = item.data(Qt.UserRole) if item else None

        return {"ID_Favorecido": id_fav}

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

        dialog = FavorecidoDialog(parent=self, favorecido=selecionado)

        if dialog.exec_() == QDialog.Accepted:
            self.load_favorecidos()

    def delete_favorecido(self):

        selecionado = self.get_selected_favorecido()
        if not selecionado:
            return

        confirm = QMessageBox.question(
            self,
            TranslatorApp.get("Confirmar Exclusão"),
            TranslatorApp.get("Deseja realmente excluir este favorecido?"),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:

            sucesso = self.controller.remover_favorecido(selecionado["ID_Favorecido"])

            if sucesso:
                self.load_favorecidos()
            else:
                QMessageBox.warning(
                    self,
                    TranslatorApp.get("Erro"),
                    TranslatorApp.get("Não foi possível excluir o favorecido."),
                )

    # =====================================================
    # STATE
    # =====================================================
    def _on_busca_change(self):
        self.state["busca"] = self.search_input.text()
        self.search_timer.start()

    def _on_tipo_change(self):
        self.state["tipo"] = self.tipo_filtro.currentData()
        self.apply_filter()