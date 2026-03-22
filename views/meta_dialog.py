import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDateEdit,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate
from controllers.meta_controller import MetaController
from controllers.category_controller import CategoryController
from utilitarios.currency_formatter import CurrencyFormatter

logger = logging.getLogger(__name__)


class MetaDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = MetaController()
        self.category_controller = CategoryController()

        self.setWindowTitle("Nova Meta")
        self.setMinimumWidth(400)

        self._init_ui()
        self._carregar_categorias()

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        layout = QVBoxLayout(self)

        # Nome
        layout.addWidget(QLabel("Nome da Meta"))
        self.input_nome = QLineEdit()
        layout.addWidget(self.input_nome)

        # Tipo
        layout.addWidget(QLabel("Tipo"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Categoria",
            "Economia",
            "Objetivo"
        ])
        self.combo_tipo.currentTextChanged.connect(self._alterar_tipo)
        layout.addWidget(self.combo_tipo)

        # Categoria
        layout.addWidget(QLabel("Categoria"))
        self.combo_categoria = QComboBox()
        layout.addWidget(self.combo_categoria)

        # Valor alvo
        layout.addWidget(QLabel("Valor Alvo"))
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Ex: 1500.00")
        layout.addWidget(self.input_valor)

        # Datas
        layout.addWidget(QLabel("Data Início"))
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        layout.addWidget(self.data_inicio)

        layout.addWidget(QLabel("Data Fim"))
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate().addMonths(1))
        layout.addWidget(self.data_fim)

        # Botões
        botoes = QHBoxLayout()

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("addButton")
        btn_salvar.clicked.connect(self._salvar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_cancelar)

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
            QMessageBox.warning(self, "Erro", "Informe o nome da meta.")
            return

        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        if data_inicio > data_fim:
            QMessageBox.warning(self, "Erro", "Data final inválida.")
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
            QMessageBox.critical(self, "Erro", str(e))