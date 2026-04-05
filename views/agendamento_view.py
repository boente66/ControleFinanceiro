import logging
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QLineEdit,
    QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from views.agendamento_dialog import AgendamentoDialog
from controllers.schedule_controller import ScheduleController
from controllers.account_controller import AccountController
from controllers.fatura_controller import FaturaController

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter
from utilitarios.ion_path import IonPath

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class AgendamentoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.schedule_controller = ScheduleController()
        self.account_controller = AccountController()
        self.fatura_controller = FaturaController()

        self._icon_cache = {}

        self.data = []

        self._init_ui()

        self.setWindowTitle("Agendamentos")
        TranslatorApp.enable_auto_translation(self)

        self.load_cartoes()
        self.load_data()

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

        main_layout.addWidget(self._create_sidebar(), 1)
        main_layout.addWidget(self._create_main_panel(), 4)

    # ==================================================
    # SIDEBAR
    # ==================================================
    def _create_sidebar(self):
        box = QGroupBox("Filtros rápidos")
        layout = QVBoxLayout(box)

        buttons = [
            ("Todos", None),
            ("Receber", "Contas a Receber"),
            ("Pagar", "Contas a Pagar"),
            ("Transferência", "Transferências"),
        ]

        for texto, tipo in buttons:
            btn = QPushButton(texto)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, t=tipo: self.apply_quick_filter(t))
            layout.addWidget(btn)

        layout.addStretch()
        return box

    # ==================================================
    # MAIN PANEL
    # ==================================================
    def _create_main_panel(self):
        container = QWidget()
        main_layout = QVBoxLayout(container)

        # ========================
        # FILTROS
        # ========================
        filtros = QHBoxLayout()

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Todos", "Contas a Receber", "Contas a Pagar", "Transferências"
        ])

        self.combo_status = QComboBox()
        self.combo_status.addItems([
            "Todos", "AGENDADO", "PAGO", "CANCELADO"
        ])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar...")

        self.combo_tipo.currentIndexChanged.connect(self.apply_filter)
        self.combo_status.currentIndexChanged.connect(self.apply_filter)
        self.search_input.textChanged.connect(self.apply_filter)

        filtros.addWidget(self.combo_tipo)
        filtros.addWidget(self.combo_status)
        filtros.addWidget(self.search_input)

        # BOTÕES
        self.add_btn = QPushButton("Adicionar")
        self.edit_btn = QPushButton("Editar")
        self.cancel_btn = QPushButton("Cancelar")
        self.execute_btn = QPushButton("Executar")

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        self.cancel_btn.clicked.connect(self.cancel_agendamento)
        self.execute_btn.clicked.connect(self.execute_agendamento)

        for btn in (self.add_btn, self.edit_btn, self.cancel_btn, self.execute_btn):
            filtros.addWidget(btn)

        main_layout.addLayout(filtros)

        # ========================
        # CORPO (DUAS COLUNAS)
        # ========================
        body = QHBoxLayout()

        # -------- AGENDAMENTOS --------
        ag_group = QGroupBox("Agendamentos")
        ag_layout = QVBoxLayout(ag_group)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Conta", "Favorecido", "Descrição", "Data", "Valor", "Status"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        ag_layout.addWidget(self.table)
        body.addWidget(ag_group, 3)

        # -------- CARTÕES --------
        card_group = QGroupBox("Cartões (Fatura Prevista)")
        card_layout = QVBoxLayout(card_group)

        self.cartao_filter = QComboBox()
        self.cartao_filter.currentIndexChanged.connect(self.load_data)

        card_layout.addWidget(self.cartao_filter)

        self.table_cartao = QTableWidget()
        self.table_cartao.setColumnCount(4)
        self.table_cartao.setHorizontalHeaderLabels([
            "Descrição", "Data", "Valor", "Tipo"
        ])
        self.table_cartao.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        card_layout.addWidget(self.table_cartao)
        body.addWidget(card_group, 2)

        main_layout.addLayout(body)

        # ========================
        # RESUMO
        # ========================
        self.lbl_total = QLabel()
        main_layout.addWidget(self.lbl_total)

        return container

    # ==================================================
    # LOAD
    # ==================================================
    def load_data(self):
        try:
            self.data = self.schedule_controller.get_all_schedules() or []
        except Exception:
            logger.exception("Erro ao carregar agendamentos")
            self.data = []

        self.apply_filter()
        self.load_cartao()
        self.calcular_resumo()

    def load_cartoes(self):
        try:
            cartoes = self.fatura_controller.listar_cartoes()
            self.cartao_filter.clear()

            for c in cartoes:
                self.cartao_filter.addItem(c["Nome"], c["ID_Cartao"])
        except Exception:
            logger.exception("Erro ao carregar cartões")

    # ==================================================
    # FILTROS
    # ==================================================
    def apply_filter(self):

        tipo = self.combo_tipo.currentText()
        status = self.combo_status.currentText()
        termo = self.search_input.text().lower()

        self.table.setRowCount(0)

        self.total_pagar = 0
        self.total_receber = 0

        for ag in self.data:

            if tipo != "Todos" and ag.get("Tipo") != tipo:
                continue

            if status != "Todos" and ag.get("Status") != status:
                continue

            if termo and termo not in (ag.get("Descricao") or "").lower():
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
                if ag.get("Tipo") == "Contas a Pagar":
                    self.total_pagar += valor
                elif ag.get("Tipo") == "Contas a Receber":
                    self.total_receber += valor

    def apply_quick_filter(self, tipo):
        self.combo_tipo.setCurrentText(tipo or "Todos")

    # ==================================================
    # CARTÃO
    # ==================================================
    def load_cartao(self):

        self.table_cartao.setRowCount(0)
        self.total_previsto = 0

        id_cartao = self.cartao_filter.currentData()
        if not id_cartao:
            return

        for ag in self.data:

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
            self.table_cartao.setItem(row, 3, QTableWidgetItem("Previsto"))

    # ==================================================
    # RESUMO
    # ==================================================
    def calcular_resumo(self):

        contas = self.account_controller.get_all_accounts()
        saldo_atual = sum(float(c.get("Saldo_Atual", 0)) for c in contas)

        saldo_previsto = saldo_atual - self.total_pagar + self.total_receber - self.total_previsto

        self.lbl_total.setText(
            f"Pagar: {CurrencyFormatter.format(self.total_pagar)} | "
            f"Receber: {CurrencyFormatter.format(self.total_receber)} | "
            f"Fatura: {CurrencyFormatter.format(self.total_previsto)} | "
            f"Saldo: {CurrencyFormatter.format(saldo_previsto)}"
        )

    # ==================================================
    # AÇÕES
    # ==================================================
    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    def open_add_dialog(self):
        dlg = AgendamentoDialog(self)
        if dlg.exec_():
            self.load_data()

    def open_edit_dialog(self):
        ag_id = self._get_selected_id()
        if not ag_id:
            return

        dlg = AgendamentoDialog(self, agendamento_id=ag_id)
        if dlg.exec_():
            self.load_data()

    def cancel_agendamento(self):
        ag_id = self._get_selected_id()
        if not ag_id:
            return

        if QMessageBox.question(self, "Confirmar", "Cancelar agendamento?") == QMessageBox.Yes:
            self.schedule_controller.cancelar_agendamento(ag_id)
            self.load_data()

    def execute_agendamento(self):
        ag_id = self._get_selected_id()
        if not ag_id:
            return

        if QMessageBox.question(self, "Confirmar", "Executar agora?") == QMessageBox.Yes:
            self.schedule_controller.executar_agendamento(ag_id)
            self.load_data()