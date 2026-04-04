import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDateEdit,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate

from controllers.meta_controller import MetaController
from controllers.category_controller import CategoryController

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class MetaDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = MetaController()
        self.category_controller = CategoryController()

        # 🔥 título base
        self.setWindowTitle("Nova Meta")

        self.setMinimumWidth(400)

        self._init_ui()
        self._carregar_categorias()

        # 🔥 tradução automática global
        TranslatorApp.enable_auto_translation(self)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        layout = QVBoxLayout(self)

        # Nome
        self.lbl_nome = QLabel("Nome da Meta")
        layout.addWidget(self.lbl_nome)

        self.input_nome = QLineEdit()
        layout.addWidget(self.input_nome)

        # Tipo
        self.lbl_tipo = QLabel("Tipo")
        layout.addWidget(self.lbl_tipo)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Categoria", "Categoria")
        self.combo_tipo.addItem("Economia", "Economia")
        self.combo_tipo.addItem("Objetivo", "Objetivo")
        self.combo_tipo.currentTextChanged.connect(self._alterar_tipo)
        layout.addWidget(self.combo_tipo)

        # Categoria
        self.lbl_categoria = QLabel("Categoria")
        layout.addWidget(self.lbl_categoria)

        self.combo_categoria = QComboBox()
        layout.addWidget(self.combo_categoria)

        # Valor alvo
        self.lbl_valor = QLabel("Valor Alvo")
        layout.addWidget(self.lbl_valor)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Ex: 1500,00")
        layout.addWidget(self.input_valor)

        # Datas
        self.lbl_inicio = QLabel("Data Início")
        layout.addWidget(self.lbl_inicio)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        layout.addWidget(self.data_inicio)

        self.lbl_fim = QLabel("Data Fim")
        layout.addWidget(self.lbl_fim)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate().addMonths(1))
        layout.addWidget(self.data_fim)

        # Botões
        botoes = QHBoxLayout()

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setObjectName("addButton")
        self.btn_salvar.clicked.connect(self._salvar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        botoes.addWidget(self.btn_salvar)
        botoes.addWidget(self.btn_cancelar)

        layout.addLayout(botoes)

        self._alterar_tipo("Categoria")

    # ==================================================
    # CARREGAR CATEGORIAS
    # ==================================================
    def _carregar_categorias(self):

        self.combo_categoria.clear()
        categorias = self.category_controller.get_all_categories()

        for cat in categorias:
            self.combo_categoria.addItem(
                cat["Nome"],
                cat["ID_Categoria"]
            )

    # ==================================================
    # ALTERAR TIPO
    # ==================================================
    def _alterar_tipo(self, tipo):

        if tipo == "Categoria":
            self.combo_categoria.setEnabled(True)
        else:
            self.combo_categoria.setEnabled(False)

    # ==================================================
    # VALIDAR E SALVAR
    # ==================================================
    def _salvar(self):

        nome = self.input_nome.text().strip()
        tipo = self.combo_tipo.currentText()
        valor = self.input_valor.text().replace(",", ".").strip()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Informe o nome da meta.")
            )
            return

        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Valor inválido.")
            )
            return

        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        if data_inicio > data_fim:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Data final inválida.")
            )
            return

        dados = {
            "Nome": nome,
            "Tipo": tipo,
            "Valor_Alvo": valor,
            "Data_Inicio": data_inicio,
            "Data_Fim": data_fim
        }

        if tipo == "Categoria":
            dados["ID_Categoria"] = self.combo_categoria.currentData()

        try:
            self.controller.criar_meta(dados)
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )