# -*- coding: utf-8 -*-
import logging
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QLineEdit,
    QMessageBox, QAbstractItemView, QHeaderView, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor

from controllers.main_controller import MainController
from views.agendamento_dialog import AgendamentoDialog
from controllers.schedule_controller import ScheduleController
from controllers.account_controller import AccountController
from controllers.fatura_controller import FaturaController
from controllers.favorecido_controller import FavorecidoController

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter
from utilitarios.ion_path import IonPath

from core.translator_app import TranslatorApp
from core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class AgendamentoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.schedule_controller = ScheduleController()
        self.account_controller = AccountController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.main_controller = MainController()

        self._icon_cache = {}
        self.data = []
        self.filtered_data = []

        self.total_pagar = 0
        self.total_receber = 0
        self.total_previsto = 0

        self._init_ui()

        self.setWindowTitle("Agendamentos")
        TranslatorApp.enable_auto_translation(self)

        self.load_cartoes()
        self.load_favorecidos()
        self.load_data()

    # ==================================================
    # ICON
    # ==================================================
    def _icon(self, nome: str) -> QIcon:
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
        main_layout.setSpacing(10)

        # SIDEBAR
        sidebar = QFrame()
        sidebar_layout = QVBoxLayout(sidebar)

        self.btn_all = QPushButton("Todos")
        self.btn_all.setIcon(self._icon("list"))

        self.btn_receber = QPushButton("Receber")
        self.btn_receber.setIcon(self._icon("arrow-down"))

        self.btn_pagar = QPushButton("Pagar")
        self.btn_pagar.setIcon(self._icon("arrow-up"))

        self.btn_transfer = QPushButton("Transferência")
        self.btn_transfer.setIcon(self._icon("swap"))

        self.btn_all.clicked.connect(lambda: self.apply_quick_filter(None))
        self.btn_receber.clicked.connect(lambda: self.apply_quick_filter("Contas a Receber"))
        self.btn_pagar.clicked.connect(lambda: self.apply_quick_filter("Contas a Pagar"))
        self.btn_transfer.clicked.connect(lambda: self.apply_quick_filter("Transferências"))

        for b in [self.btn_all, self.btn_receber, self.btn_pagar, self.btn_transfer]:
            b.setCursor(Qt.PointingHandCursor)
            sidebar_layout.addWidget(b)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar, 1)

        # MAIN
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addLayout(self._create_toolbar())

        splitter = QSplitter(Qt.Vertical)

        # TOPO
        top = QWidget()
        top_layout = QVBoxLayout(top)

        self.table = self._create_table()
        self.table.setMinimumHeight(300)

        top_layout.addWidget(self.table)
        top_layout.addLayout(self._create_cards())

        splitter.addWidget(top)

        # BASE
        bottom = QSplitter(Qt.Vertical)
        bottom.addWidget(self._create_fatura())
        bottom.addWidget(self._create_historico())

        splitter.addWidget(bottom)

        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        main_layout.addWidget(container, 4)

    # ==================================================
    # TOOLBAR
    # ==================================================
    def _create_toolbar(self):

        layout = QHBoxLayout()

        self.btn_add = QPushButton("Novo")
        self.btn_edit = QPushButton("Editar")
        self.btn_exec = QPushButton("Executar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_add.setIcon(self._icon("add"))
        self.btn_edit.setIcon(self._icon("edit"))
        self.btn_exec.setIcon(self._icon("play"))
        self.btn_cancel.setIcon(self._icon("cancel"))

        for btn in [self.btn_add, self.btn_edit, self.btn_exec, self.btn_cancel]:
            btn.setIconSize(QSize(18, 18))

        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        self.btn_exec.clicked.connect(self.execute_agendamento)
        self.btn_cancel.clicked.connect(self.cancel_agendamento)

        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_exec)
        layout.addWidget(self.btn_cancel)

        layout.addStretch()

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Contas a Receber", "Contas a Pagar", "Transferências"])

        self.combo_status = QComboBox()
        self.combo_status.addItems(["Todos", "AGENDADO", "PAGO", "CANCELADO"])

        self.combo_favorecido = QComboBox()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar...")

        for w in [self.combo_tipo, self.combo_status, self.combo_favorecido]:
            w.currentIndexChanged.connect(self.apply_filter)

        self.search_input.textChanged.connect(self.apply_filter)

        layout.addWidget(self.combo_tipo)
        layout.addWidget(self.combo_status)
        layout.addWidget(self.combo_favorecido)
        layout.addWidget(self.search_input)

        return layout

    # ==================================================
    # TABLE
    # ==================================================
    def _create_table(self):
        table = QTableWidget(0, 8)
        table.setHorizontalHeaderLabels([
            "ID", "Data", "Descrição", "Categoria", "Favorecido", "Conta", "Valor", "Status"
        ])
        table.setColumnHidden(0, True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.itemSelectionChanged.connect(self._update_buttons)
        return table

    def _update_buttons(self):
        has = len(self._get_selected_ids()) > 0
        self.btn_edit.setEnabled(has)
        self.btn_cancel.setEnabled(has)
        self.btn_exec.setEnabled(True)

    def _get_selected_ids(self):
        rows = self.table.selectionModel().selectedRows()
        return [int(self.table.item(r.row(), 0).text()) for r in rows]

    def _create_cards(self):
        layout = QHBoxLayout()

        def card(titulo, valor):
            box = QVBoxLayout()
            box.addWidget(QLabel(titulo))
            box.addWidget(QLabel(CurrencyFormatter.format(valor)))

            w = QWidget()
            w.setLayout(box)
            return w

        layout.addWidget(card("Total a Pagar", self.total_pagar))
        layout.addWidget(card("Total a Receber", self.total_receber))
        layout.addWidget(card("Previsto", self.total_previsto))

        return layout

    # ==================================================
    # LOAD
    # ==================================================
    def load_data(self):
        self.data = self.schedule_controller.get_all_schedules() or []
        self.filtered_data = list(self.data)
        self.apply_filter()

    def load_cartoes(self):
        self.cartao_filter.clear()
        for c in self.fatura_controller.listar_cartoes():
            self.cartao_filter.addItem(c["Nome"], c["ID_Cartao"])

    def load_favorecidos(self):
        self.combo_favorecido.clear()
        self.combo_favorecido.addItem("Todos", None)
        for f in self.favorecido_controller.listar_favorecidos():
            self.combo_favorecido.addItem(f["Nome"], f["ID_Favorecido"])

    # ==================================================
    # FILTER
    # ==================================================
    def apply_filter(self):

        tipo = self.combo_tipo.currentText()
        status = self.combo_status.currentText()
        fav = self.combo_favorecido.currentData()
        termo = self.search_input.text().lower()

        self.table.setRowCount(0)
        self.filtered_data = []

        self.total_pagar = 0
        self.total_receber = 0

        for ag in self.data:

            if tipo != "Todos" and ag.get("Tipo") != tipo:
                continue

            if status != "Todos" and ag.get("Status") != status:
                continue

            if fav and ag.get("ID_Favorecido") != fav:
                continue

            if termo and termo not in (ag.get("Descricao") or "").lower():
                continue

            self.filtered_data.append(ag)

            valor = float(ag.get("Valor", 0))

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(ag.get("ID_Agendamento"))))
            self.table.setItem(row, 1, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))
            self.table.setItem(row, 2, QTableWidgetItem(ag.get("Descricao", "")))
            self.table.setItem(row, 3, QTableWidgetItem(ag.get("Categoria", "")))
            self.table.setItem(row, 4, QTableWidgetItem(ag.get("Favorecido", "")))
            self.table.setItem(row, 5, QTableWidgetItem(ag.get("Conta", "")))

            valor_item = QTableWidgetItem(CurrencyFormatter.format(valor))

            if ag.get("Tipo") == "Contas a Receber":
                valor_item.setForeground(QColor(ThemeManager.get_finance_color("receita")))
                self.total_receber += valor
            else:
                valor_item.setForeground(QColor(ThemeManager.get_finance_color("despesa")))
                self.total_pagar += valor

            self.table.setItem(row, 6, valor_item)
            self.table.setItem(row, 7, QTableWidgetItem(ag.get("Status", "")))

        self.load_cartao()
        self.calcular_resumo()
        self.load_historico()

    # ==================================================
    # FATURA
    # ==================================================
    def _create_fatura(self):

        group = QGroupBox("💳 Fatura Prevista")
        layout = QVBoxLayout(group)

        self.cartao_filter = QComboBox()
        self.cartao_filter.currentIndexChanged.connect(self.apply_filter)

        layout.addWidget(self.cartao_filter)

        self.table_cartao = QTableWidget(0, 7)
        self.table_cartao.setHorizontalHeaderLabels([
            "Data", "Descrição", "Categoria", "Favorecido",
            "Valor", "Parcelas", "Status"
        ])
        self.table_cartao.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_cartao)

        self.lbl_total_fatura = QLabel("TOTAL PREVISTO: R$ 0,00")
        layout.addWidget(self.lbl_total_fatura)

        return group

    def load_cartao(self):

        self.table_cartao.setRowCount(0)
        self.total_previsto = 0

        id_cartao = self.cartao_filter.currentData()
        if not id_cartao:
            return

        for ag in self.filtered_data:

            if ag.get("ID_Cartao") != id_cartao:
                continue

            if ag.get("Status") != "AGENDADO":
                continue

            valor = float(ag.get("Valor", 0))
            self.total_previsto += valor

            row = self.table_cartao.rowCount()
            self.table_cartao.insertRow(row)

            self.table_cartao.setItem(row, 0, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))
            self.table_cartao.setItem(row, 1, QTableWidgetItem(ag.get("Descricao", "")))
            self.table_cartao.setItem(row, 2, QTableWidgetItem(ag.get("Categoria", "")))
            self.table_cartao.setItem(row, 3, QTableWidgetItem(ag.get("Favorecido", "")))
            self.table_cartao.setItem(row, 4, QTableWidgetItem(CurrencyFormatter.format(valor)))
            self.table_cartao.setItem(row, 5, QTableWidgetItem(str(ag.get("Parcelas", "-"))))
            self.table_cartao.setItem(row, 6, QTableWidgetItem(ag.get("Status", "")))

        self.lbl_total_fatura.setText(f"TOTAL PREVISTO: {CurrencyFormatter.format(self.total_previsto)}")

    # ==================================================
    # HISTÓRICO
    # ==================================================
    def _create_historico(self):

        group = QGroupBox("📊 Histórico")
        layout = QVBoxLayout(group)

        self.table_hist = QTableWidget(0, 4)
        self.table_hist.setHorizontalHeaderLabels([
            "Data", "Descrição", "Valor", "Status"
        ])
        self.table_hist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_hist)
        return group

    def load_historico(self):

        self.table_hist.setRowCount(0)

        for ag in self.filtered_data:

            if ag.get("Status") != "PAGO":
                continue

            row = self.table_hist.rowCount()
            self.table_hist.insertRow(row)

            self.table_hist.setItem(row, 0, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))
            self.table_hist.setItem(row, 1, QTableWidgetItem(ag.get("Descricao", "")))
            self.table_hist.setItem(row, 2, QTableWidgetItem(CurrencyFormatter.format(float(ag.get("Valor", 0)))))
            self.table_hist.setItem(row, 3, QTableWidgetItem("Pago"))

    # ==================================================
    # RESUMO
    # ==================================================
    def calcular_resumo(self):

        contas = self.account_controller.get_all_accounts()
        saldo_atual = sum(float(c.get("Saldo_Atual", 0)) for c in contas)

        saldo_previsto = saldo_atual + self.total_receber - self.total_pagar - self.total_previsto

        self.lbl_total_fatura.setText(f"TOTAL PREVISTO: {CurrencyFormatter.format(self.total_previsto)}")

    # ==================================================
    # ACTIONS
    # ==================================================
    def open_add_dialog(self):
        dlg = AgendamentoDialog(self)
        if dlg.exec_():
            self.load_data()

    def open_edit_dialog(self):
        ids = self._get_selected_ids()
        if not ids:
            QMessageBox.warning(self, "Aviso", "Selecione um agendamento")
            return

        dlg = AgendamentoDialog(self, agendamento_id=ids[0])
        if dlg.exec_():
            self.load_data()

    def cancel_agendamento(self):
        ids = self._get_selected_ids()
        if not ids:
            return

        if QMessageBox.question(self, "Confirmar", f"Cancelar {len(ids)}?") != QMessageBox.Yes:
            return

        for ag_id in ids:
            self.schedule_controller.cancelar_agendamento(ag_id)

        self.load_data()

    def execute_agendamento(self):

        ids = self._get_selected_ids()

        if not ids:
            confirm = QMessageBox.question(
                self,
                "Executar todos",
                "Nenhum item selecionado.\nExecutar TODOS?"
            )
            if confirm != QMessageBox.Yes:
                return

            sucesso, falha = self.main_controller.execute_all_schedules()

        else:
            confirm = QMessageBox.question(
                self,
                "Executar",
                f"Executar {len(ids)}?"
            )
            if confirm != QMessageBox.Yes:
                return

            sucesso, falha = self.main_controller.execute_multiple_schedules(ids)

        QMessageBox.information(
            self,
            "Resultado",
            f"Sucesso: {len(sucesso)} | Falha: {len(falha)}"
        )

        self.load_data()

    def apply_quick_filter(self, tipo):
        self.combo_tipo.setCurrentText(tipo or "Todos")