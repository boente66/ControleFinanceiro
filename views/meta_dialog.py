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

        self._is_bound = False

        # título traduzível
        TranslatorApp.window_title(self, "Nova Meta")

        self.setMinimumWidth(400)

        self._init_ui()
        self._apply_translation()

        self._carregar_categorias()

        # 🔥 bind correto
        if not self._is_bound:
            TranslatorApp.bind(self._on_translate)
            self._is_bound = True

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        layout = QVBoxLayout(self)

        # Nome
        self.lbl_nome = QLabel()
        layout.addWidget(self.lbl_nome)

        self.input_nome = QLineEdit()
        layout.addWidget(self.input_nome)

        # Tipo
        self.lbl_tipo = QLabel()
        layout.addWidget(self.lbl_tipo)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Categoria",
            "Economia",
            "Objetivo"
        ])
        self.combo_tipo.currentTextChanged.connect(self._alterar_tipo)
        layout.addWidget(self.combo_tipo)

        # Categoria
        self.lbl_categoria = QLabel()
        layout.addWidget(self.lbl_categoria)

        self.combo_categoria = QComboBox()
        layout.addWidget(self.combo_categoria)

        # Valor alvo
        self.lbl_valor = QLabel()
        layout.addWidget(self.lbl_valor)

        self.input_valor = QLineEdit()
        layout.addWidget(self.input_valor)

        # Datas
        self.lbl_inicio = QLabel()
        layout.addWidget(self.lbl_inicio)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        layout.addWidget(self.data_inicio)

        self.lbl_fim = QLabel()
        layout.addWidget(self.lbl_fim)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate().addMonths(1))
        layout.addWidget(self.data_fim)

        # Botões
        botoes = QHBoxLayout()

        self.btn_salvar = QPushButton()
        self.btn_salvar.setObjectName("addButton")
        self.btn_salvar.clicked.connect(self._salvar)

        self.btn_cancelar = QPushButton()
        self.btn_cancelar.clicked.connect(self.reject)

        botoes.addWidget(self.btn_salvar)
        botoes.addWidget(self.btn_cancelar)

        layout.addLayout(botoes)

        self._alterar_tipo("Categoria")

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _on_translate(self, *_):
        self._apply_translation()

    def _apply_translation(self):

        TranslatorApp.text(self.lbl_nome, "Nome da Meta")
        TranslatorApp.text(self.lbl_tipo, "Tipo")
        TranslatorApp.text(self.lbl_categoria, "Categoria")
        TranslatorApp.text(self.lbl_valor, "Valor Alvo")
        TranslatorApp.text(self.lbl_inicio, "Data Início")
        TranslatorApp.text(self.lbl_fim, "Data Fim")

        TranslatorApp.text(self.btn_salvar, "Salvar")
        TranslatorApp.text(self.btn_cancelar, "Cancelar")

        TranslatorApp.placeholder(self.input_valor, "Ex: 1500,00")

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