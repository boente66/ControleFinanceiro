import os
from venv import logger
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate
import re
from PyQt5.QtCore import Qt, QSize
from controllers.main_controller import MainController
from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController
from core.translator_app import TranslatorApp
from utilitarios.ion_path import IonPath
from views.agendamento_view import QIcon


class TransactionDialogConta(QDialog):

    def __init__(self, parent=None, id_conta=None):
        super().__init__(parent)

        if id_conta is None:
            raise ValueError("Conta inválida")

        self.id_conta = id_conta

        self.main_controller = MainController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self._icon_cache = {}
        self._init_ui()
        self._configurar_ui()
        self._carregar_dados()
        self._conectar_eventos()

    # ======================================================
    # UI (CONSTRUÇÃO)
    # ======================================================
    def _init_ui(self):
        self.setWindowTitle("Novo Lançamento")
        self.resize(616, 404)
        self.setMinimumSize(616, 404)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ======================
        # TIPO
        # ======================
        tipo_layout = QHBoxLayout()

        self.tipo_label = QLabel("Tipo:")
        self.tipo_combo = QComboBox()

        tipo_layout.addWidget(self.tipo_label)
        tipo_layout.addWidget(self.tipo_combo)

        layout.addLayout(tipo_layout)

        # ======================
        # DESCRIÇÃO + DATA
        # ======================
        top_layout = QHBoxLayout()

        desc_layout = QVBoxLayout()
        self.descricao_label = QLabel("Descrição:")
        self.descricao_edit = QLineEdit()
        self.descricao_edit.setMinimumHeight(28)

        desc_layout.addWidget(self.descricao_label)
        desc_layout.addWidget(self.descricao_edit)

        data_layout = QVBoxLayout()
        self.data_label = QLabel("Data:")
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setMinimumHeight(28)

        data_layout.addWidget(self.data_label)
        data_layout.addWidget(self.data_edit)

        top_layout.addLayout(desc_layout)
        top_layout.addLayout(data_layout)
        top_layout.setStretch(0, 2)
        top_layout.setStretch(1, 1)

        layout.addLayout(top_layout)

        # ======================
        # FAVORECIDO + CATEGORIA
        # ======================
        mid_layout = QHBoxLayout()

        # favorecido
        fav_layout = QVBoxLayout()
        self.lbl_favorecido = QLabel("Pagar para:")

        fav_row = QHBoxLayout()
        self.favorecido_combo = QComboBox()
        self.favorecido_combo.setMinimumHeight(28)

        self.btn_add_fav = QPushButton("+")
        self.btn_add_fav.setIcon(self._icon("add"))
        self.btn_add_fav.setFixedSize(28, 28)

        fav_row.addWidget(self.favorecido_combo)
        fav_row.addWidget(self.btn_add_fav)

        fav_layout.addWidget(self.lbl_favorecido)
        fav_layout.addLayout(fav_row)

        # categoria
        cat_layout = QVBoxLayout()
        self.lbl_categoria = QLabel("Categoria:")

        cat_row = QHBoxLayout()
        self.categoria_combo = QComboBox()
        self.categoria_combo.setMinimumHeight(28)

        self.btn_add_cat = QPushButton("+")
        self.btn_add_cat.setIcon(self._icon("add"))
        self.btn_add_cat.setFixedSize(28, 28)

        cat_row.addWidget(self.categoria_combo)
        cat_row.addWidget(self.btn_add_cat)

        cat_layout.addWidget(self.lbl_categoria)
        cat_layout.addLayout(cat_row)

        mid_layout.addLayout(fav_layout)
        mid_layout.addLayout(cat_layout)

        layout.addLayout(mid_layout)

        # ======================
        # VALOR
        # ======================
        valor_layout = QVBoxLayout()
        self.valor_label = QLabel("Valor:")
        self.valor_edit = QLineEdit()
        self.valor_edit.setMinimumHeight(28)

        valor_layout.addWidget(self.valor_label)
        valor_layout.addWidget(self.valor_edit)

        layout.addLayout(valor_layout)

        # ======================
        # NOTAS
        # ======================
        notas_layout = QVBoxLayout()
        self.notas_label = QLabel("Notas:")
        self.notas_edit = QTextEdit()

        notas_layout.addWidget(self.notas_label)
        notas_layout.addWidget(self.notas_edit)

        layout.addLayout(notas_layout)

        # ======================
        # BOTÕES
        # ======================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_salvar = QPushButton("Salvar")

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_salvar)

        layout.addLayout(btn_layout)

    def _icon(self, nome):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        try:
            path = IonPath.resource("assets", "icons", f"{nome}.svg")
            icon = QIcon(path) if os.path.exists(path) else QIcon()
            self._icon_cache[nome] = icon
            return icon

        except Exception:
            logger.exception(f"Erro ao carregar ícone: {nome}")
            return QIcon()

    # ======================================================
    # CONFIG
    # ======================================================
    def _configurar_ui(self):
        self.tipo_combo.addItem("Despesa", "Despesa")
        self.tipo_combo.addItem("Receita", "Receita")
        self.tipo_combo.setCurrentIndex(0)

        self.data_edit.setDate(QDate.currentDate())

        self.btn_salvar.setDefault(True)

        self.descricao_edit.setFocus()

        self._update_label()

    # ======================================================
    # DADOS
    # ======================================================
    def _carregar_categorias(self, selecionar_id=None):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Nenhum", None)

        categorias = self.category_controller.get_all_categories() or []

        for categoria in categorias:
            self.categoria_combo.addItem(
                categoria["Nome"],
                categoria["ID_Categoria"]
            )

        if selecionar_id:
            index = self.categoria_combo.findData(selecionar_id)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)

    def _carregar_favorecidos(self, selecionar_id=None):
        self.favorecido_combo.clear()
        self.favorecido_combo.addItem("Nenhum", None)

        favorecidos = self.favorecido_controller.listar_favorecidos()

        for favorecido in favorecidos:
            self.favorecido_combo.addItem(
                favorecido["Nome"],
                favorecido["ID_Favorecido"]
            )

        if selecionar_id:
            index = self.favorecido_combo.findData(selecionar_id)
            if index >= 0:
                self.favorecido_combo.setCurrentIndex(index)

    # ======================================================
    # EVENTOS
    # ======================================================
    def _conectar_eventos(self):
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.reject)
        self.valor_edit.textChanged.connect(self._formatar_moeda)
        self.tipo_combo.currentIndexChanged.connect(self._update_label)
        self.btn_add_cat.clicked.connect(self._adicionar_categoria)
        self.btn_add_fav.clicked.connect(self._adicionar_favorecido)

    def _adicionar_categoria(self):
        try:
            from views.categoria_dialog import CategoriaDialog

            dialog = CategoriaDialog(parent=self)

            if dialog.exec_() == QDialog.Accepted:
                dados = dialog.get_data()
                nova_id = self.category_controller.add_category(
                    dados["Nome"],
                    dados["Tipo"]
                )
                self._carregar_categorias(nova_id)

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def _adicionar_favorecido(self):
        try:
            from views.FavorecidoDialog import FavorecidoDialog

            dialog = FavorecidoDialog(parent=self)

            if dialog.exec_() == QDialog.Accepted:
                id_favorecido = dialog.get_id()
                self._carregar_favorecidos(id_favorecido)

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    # ======================================================
    def _update_label(self):
        tipo = self.tipo_combo.currentData()
        self.lbl_favorecido.setText("Receber de" if tipo == "Receita" else "Pagar para")

    # ======================================================
    def _formatar_moeda(self):
        texto = re.sub(r"[^\d]", "", self.valor_edit.text())

        if not texto:
            return

        valor = int(texto) / 100

        self.valor_edit.blockSignals(True)
        self.valor_edit.setText(
            f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        self.valor_edit.blockSignals(False)

    # ======================================================
    def salvar(self):
        try:
            descricao = self.descricao_edit.text().strip()
            if not descricao:
                raise ValueError("Descrição obrigatória")

            valor = float(self.valor_edit.text().replace(".", "").replace(",", "."))

            tipo = self.tipo_combo.currentData()
            valor = -abs(valor) if tipo == "Despesa" else abs(valor)

            dados = {
                "Descricao": descricao,
                "Valor": valor,
                "Data": self.data_edit.date().toString("yyyy-MM-dd"),
                "ID_Conta": self.id_conta,
                "Tipo": tipo,
                "ID_Categoria": self.categoria_combo.currentData(),
                "ID_Favorecido": self.favorecido_combo.currentData(),
                "Notas": self.notas_edit.toPlainText()
            }

            self.main_controller.inserir_lancamento(dados)
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))