import logging
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QLineEdit,
    QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from views.agendamento_dialog import AgendamentoDialog
from controllers.schedule_controller import ScheduleController
from controllers.main_controller import MainController
from controllers.account_controller import AccountController
from controllers.fatura_controller import FaturaController  # 🔥 NOVO

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter
from utilitarios.ion_path import IonPath

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class AgendamentoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.schedule_controller = ScheduleController()
        self.main_controller = MainController()
        self.account_controller = AccountController()
        self.fatura_controller = FaturaController()  # 🔥 NOVO

        self._icon_cache = {}

        TranslatorApp.window_title(self, "Agendamentos")

        self._init_ui()

        TranslatorApp.bind(self._on_translate)

        self.load_cartoes()
        self.load_data()

    # ==================================================
    # REATIVIDADE
    # ==================================================
    def _on_translate(self, *_):
        self._retranslate_static()
        self.load_data()

    def _retranslate_static(self):
        TranslatorApp.text(self.btn_receber, "Contas a Receber")
        TranslatorApp.text(self.btn_pagar, "Contas a Pagar")
        TranslatorApp.text(self.btn_transfer, "Transferências")
        TranslatorApp.text(self.btn_todos, "Todos")

        TranslatorApp.text(self.filter_label, "Filtrar por:")
        TranslatorApp.placeholder(self.search_input, "Pesquisar...")

        TranslatorApp.text(self.add_btn, "Adicionar")
        TranslatorApp.text(self.edit_btn, "Editar")
        TranslatorApp.text(self.cancel_btn, "Cancelar")
        TranslatorApp.text(self.execute_btn, "Executar")

        TranslatorApp.table_headers(
            self.table,
            ["ID", "Conta", "Favorecido", "Descrição", "Vencimento", "Valor", "Status"]
        )

    # ==================================================
    # ICON
    # ==================================================
    def _icon(self, nome: str):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        path = IonPath.resource("assets", "icons", f"{nome}.svg")
        icon = QIcon(path) if os.path.exists(path) else QIcon()

        self._icon_cache[nome] = icon
        return icon

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar, 1)

        self.main_panel = self._create_main_panel()
        main_layout.addWidget(self.main_panel, 3)

    def _create_sidebar(self):
        self.sidebar_group = QGroupBox()
        TranslatorApp.group(self.sidebar_group, "Agendamentos")

        layout = QVBoxLayout(self.sidebar_group)

        self.btn_receber = QPushButton()
        self.btn_pagar = QPushButton()
        self.btn_transfer = QPushButton()
        self.btn_todos = QPushButton()

        for btn in (self.btn_receber, self.btn_pagar, self.btn_transfer, self.btn_todos):
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        self.btn_receber.clicked.connect(lambda: self.apply_quick_filter("Contas a Receber"))
        self.btn_pagar.clicked.connect(lambda: self.apply_quick_filter("Contas a Pagar"))
        self.btn_transfer.clicked.connect(lambda: self.apply_quick_filter("Transferências"))
        self.btn_todos.clicked.connect(lambda: self.apply_quick_filter(None))

        layout.addStretch()
        return self.sidebar_group

    def _create_main_panel(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        # ========================
        # FILTROS
        # ========================
        filtros = QHBoxLayout()

        self.filter_label = QLabel()
        self.filter_combo = QComboBox()
        TranslatorApp.combo(self.filter_combo, ["Todos", "Contas a Receber", "Contas a Pagar", "Transferências"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.apply_filter)

        filtros.addWidget(self.filter_label)
        filtros.addWidget(self.filter_combo)
        filtros.addWidget(self.search_input)

        # ========================
        # BOTÕES
        # ========================
        self.add_btn = QPushButton()
        self.edit_btn = QPushButton()
        self.cancel_btn = QPushButton()
        self.execute_btn = QPushButton()

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        self.cancel_btn.clicked.connect(self.cancel_agendamento)
        self.execute_btn.clicked.connect(self.execute_agendamento)

        for btn in (self.add_btn, self.edit_btn, self.cancel_btn, self.execute_btn):
            filtros.addWidget(btn)

        layout.addLayout(filtros)

        # ========================
        # TABELA PRINCIPAL
        # ========================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # ========================
        # 🔥 CARTÃO
        # ========================
        filtro_cartao_layout = QHBoxLayout()

        self.lbl_cartao = QLabel("Cartão:")
        self.cartao_filter = QComboBox()
        self.cartao_filter.currentIndexChanged.connect(self.load_data)

        filtro_cartao_layout.addWidget(self.lbl_cartao)
        filtro_cartao_layout.addWidget(self.cartao_filter)

        layout.addLayout(filtro_cartao_layout)

        self.table_cartao = QTableWidget()
        self.table_cartao.setColumnCount(5)
        self.table_cartao.setHorizontalHeaderLabels(
            ["Descrição", "Data", "Valor", "Origem", "Tipo"]
        )
        self.table_cartao.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_cartao)

        # ========================
        # RESUMO
        # ========================
        self.lbl_total_pagar = QLabel()
        self.lbl_total_receber = QLabel()
        self.lbl_fatura_prevista = QLabel()
        self.lbl_saldo_atual = QLabel()
        self.lbl_saldo_previsto = QLabel()

        layout.addWidget(self.lbl_total_pagar)
        layout.addWidget(self.lbl_total_receber)
        layout.addWidget(self.lbl_fatura_prevista)
        layout.addWidget(self.lbl_saldo_atual)
        layout.addWidget(self.lbl_saldo_previsto)

        return container

    # ==================================================
    # CARTÕES
    # ==================================================
    def load_cartoes(self):
        try:
            cartoes = self.fatura_controller.listar_cartoes()
            self.cartao_filter.clear()

            for c in cartoes:
                self.cartao_filter.addItem(c["Nome"], c["ID_Cartao"])

        except Exception:
            logger.exception("Erro ao carregar cartões")

    # ==================================================
    # LOAD GERAL
    # ==================================================
    def load_data(self):
        self.load_agendamentos()
        self.load_cartao()
        self.calcular_resumo()

    # ==================================================
    # AGENDAMENTOS
    # ==================================================
    def load_agendamentos(self, tipo_filtro=None, termo_busca=None):

        self.table.setRowCount(0)

        self.total_pagar = 0
        self.total_receber = 0

        ags = self.schedule_controller.get_all_schedules()

        for ag in ags:

            tipo = ag.get("Tipo")

            if tipo_filtro and tipo != tipo_filtro:
                continue

            if termo_busca and termo_busca.lower() not in (ag.get("Descricao") or "").lower():
                continue

            valor = float(ag.get("Valor", 0))

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(ag.get("ID_Agendamento"))))
            self.table.setItem(row, 1, QTableWidgetItem(ag.get("Conta", "")))
            self.table.setItem(row, 2, QTableWidgetItem(ag.get("Favorecido", "")))
            self.table.setItem(row, 3, QTableWidgetItem(ag.get("Descricao", "")))
            self.table.setItem(row, 4, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))
            self.table.setItem(row, 5, QTableWidgetItem(CurrencyFormatter.format(valor)))
            self.table.setItem(row, 6, QTableWidgetItem(TranslatorApp.get(ag.get("Status", ""))))

            if ag.get("Status") == "AGENDADO":
                if tipo == "Contas a Pagar":
                    self.total_pagar += valor
                elif tipo == "Contas a Receber":
                    self.total_receber += valor

    # ==================================================
    # CARTÃO
    # ==================================================
    def load_cartao(self):

        self.table_cartao.setRowCount(0)
        self.total_previsto = 0

        id_cartao = self.cartao_filter.currentData()
        if not id_cartao:
            return

        ags = self.schedule_controller.get_all_schedules()

        for ag in ags:

            if ag.get("ID_Cartao") != id_cartao:
                continue

            if ag.get("Status") != "AGENDADO":
                continue

            valor = float(ag.get("Valor", 0))
            self.total_previsto += valor

            row = self.table_cartao.rowCount()
            self.table_cartao.insertRow(row)

            self.table_cartao.setItem(row, 0, QTableWidgetItem(ag.get("Descricao", "")))
            self.table_cartao.setItem(row, 1, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))
            self.table_cartao.setItem(row, 2, QTableWidgetItem(CurrencyFormatter.format(valor)))
            self.table_cartao.setItem(row, 3, QTableWidgetItem("Agendamento"))
            self.table_cartao.setItem(row, 4, QTableWidgetItem("Previsto"))

    # ==================================================
    # RESUMO
    # ==================================================
    def calcular_resumo(self):

        contas = self.account_controller.get_all_accounts()
        saldo_atual = sum(float(c.get("Saldo_Atual", 0)) for c in contas)

        saldo_previsto = (
            saldo_atual
            - self.total_pagar
            + self.total_receber
            - self.total_previsto
        )

        self.lbl_total_pagar.setText(f"Total a pagar: {CurrencyFormatter.format(self.total_pagar)}")
        self.lbl_total_receber.setText(f"Total a receber: {CurrencyFormatter.format(self.total_receber)}")
        self.lbl_fatura_prevista.setText(f"Fatura prevista: {CurrencyFormatter.format(self.total_previsto)}")
        self.lbl_saldo_atual.setText(f"Saldo atual: {CurrencyFormatter.format(saldo_atual)}")
        self.lbl_saldo_previsto.setText(f"Saldo projetado: {CurrencyFormatter.format(saldo_previsto)}")