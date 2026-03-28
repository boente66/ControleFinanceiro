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
from core.session import Session
from core.i18n import t

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter
from utilitarios.ion_path import IonPath

logger = logging.getLogger(__name__)


class AgendamentoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.schedule_controller = ScheduleController()
        self.main_controller = MainController()
        self.account_controller = AccountController()

        self._icon_cache = {}

        self._init_ui()
        self.load_agendamentos()

        Session.on_idioma_change(self._retranslate)

    # ==================================================
    # ICON UTIL
    # ==================================================
    def _icon(self, nome: str):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        try:
            caminho = IonPath.resource("assets", "icons", f"{nome}.svg")

            if not os.path.exists(caminho):
                logger.warning(f"[Ícone não encontrado] {caminho}")
                icon = QIcon()
            else:
                icon = QIcon(caminho)

            self._icon_cache[nome] = icon
            return icon

        except Exception:
            logger.exception(f"Erro ao carregar ícone: {nome}")
            return QIcon()

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar, 1)

        self.main_panel = self._create_main_panel()
        main_layout.addWidget(self.main_panel, 3)

        self._retranslate(Session.get_config("idioma", "Português"))

    # ==================================================
    # SIDEBAR
    # ==================================================
    def _create_sidebar(self):
        group = QGroupBox()
        group.setObjectName("sidebar")
        layout = QVBoxLayout(group)

        self.btn_receber = QPushButton()
        self.btn_pagar = QPushButton()
        self.btn_transfer = QPushButton()
        self.btn_todos = QPushButton()

        # Ícones
        self.btn_receber.setIcon(self._icon("receber"))
        self.btn_pagar.setIcon(self._icon("pagar"))
        self.btn_transfer.setIcon(self._icon("transfer"))
        self.btn_todos.setIcon(self._icon("list"))

        for btn in (
            self.btn_receber,
            self.btn_pagar,
            self.btn_transfer,
            self.btn_todos,
        ):
            btn.setIconSize(QSize(16, 16))
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        self.btn_receber.clicked.connect(lambda: self.apply_quick_filter("Contas a Receber"))
        self.btn_pagar.clicked.connect(lambda: self.apply_quick_filter("Contas a Pagar"))
        self.btn_transfer.clicked.connect(lambda: self.apply_quick_filter("Transferências"))
        self.btn_todos.clicked.connect(lambda: self.apply_quick_filter(None))

        layout.addStretch()
        return group

    # ==================================================
    # MAIN PANEL
    # ==================================================
    def _create_main_panel(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        filtros = QHBoxLayout()

        self.filter_label = QLabel()
        self.filter_combo = QComboBox()
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.apply_filter)

        filtros.addWidget(self.filter_label)
        filtros.addWidget(self.filter_combo)
        filtros.addWidget(self.search_input)

        # BOTÕES
        self.add_btn = QPushButton()
        self.add_btn.setIcon(self._icon("add"))

        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(self._icon("edit"))

        self.cancel_btn = QPushButton()
        self.cancel_btn.setIcon(self._icon("cancel"))

        self.execute_btn = QPushButton()
        self.execute_btn.setIcon(self._icon("check"))

        for btn in (self.add_btn, self.edit_btn, self.cancel_btn, self.execute_btn):
            btn.setIconSize(QSize(16, 16))
            btn.setCursor(Qt.PointingHandCursor)
            filtros.addWidget(btn)

        # Estado inicial
        self.edit_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.execute_btn.setEnabled(False)

        # Conexões
        self.add_btn.clicked.connect(self.open_add_dialog)
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        self.cancel_btn.clicked.connect(self.cancel_agendamento)
        self.execute_btn.clicked.connect(self.execute_agendamento)

        layout.addLayout(filtros)

        # -------- TABELA --------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setColumnHidden(0, True)
        self.table.setSortingEnabled(True)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.itemSelectionChanged.connect(self.update_buttons_state)

        layout.addWidget(self.table)

        # -------- RESUMO --------
        resumo = QVBoxLayout()

        self.lbl_total_pagar = QLabel()
        self.lbl_total_receber = QLabel()
        self.lbl_saldo_atual = QLabel()
        self.lbl_saldo_previsto = QLabel()

        resumo.addWidget(self.lbl_total_pagar)
        resumo.addWidget(self.lbl_total_receber)
        resumo.addWidget(self.lbl_saldo_atual)
        resumo.addWidget(self.lbl_saldo_previsto)

        layout.addLayout(resumo)

        return container

    # ==================================================
    # DADOS
    # ==================================================
    def load_agendamentos(self, tipo_filtro=None, termo_busca=None):

        idioma = Session.get_config("idioma", "Português")

        try:
            agendamentos = self.schedule_controller.get_all_schedules()
            self.table.setRowCount(0)

            total_pagar = 0.0
            total_receber = 0.0

            for ag in agendamentos:

                tipo_ag = ag.get("Tipo")

                if tipo_filtro and tipo_ag != tipo_filtro:
                    continue

                if termo_busca and termo_busca.lower() not in (ag.get("Descricao") or "").lower():
                    continue

                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(str(ag.get("ID_Agendamento"))))
                self.table.setItem(row, 1, QTableWidgetItem(ag.get("Conta", "")))
                self.table.setItem(row, 2, QTableWidgetItem(ag.get("Favorecido", "")))
                self.table.setItem(row, 3, QTableWidgetItem(ag.get("Descricao", "")))
                self.table.setItem(row, 4, QTableWidgetItem(DateFormatter.iso_to_br(ag.get("Data"))))

                valor = float(ag.get("Valor", 0))
                self.table.setItem(row, 5, QTableWidgetItem(CurrencyFormatter.format(valor)))

                status = ag.get("Status", "")
                self.table.setItem(row, 6, QTableWidgetItem(status))

                if status == "AGENDADO":
                    if tipo_ag == "Contas a Pagar":
                        total_pagar += valor
                    elif tipo_ag == "Contas a Receber":
                        total_receber += valor

            # Feedback vazio
            if self.table.rowCount() == 0:
                self.table.setRowCount(1)
                self.table.setItem(0, 1, QTableWidgetItem("Nenhum agendamento encontrado"))

            # Totais
            self.lbl_total_pagar.setText(f"{t('Total a pagar:', idioma)} {CurrencyFormatter.format(total_pagar)}")
            self.lbl_total_receber.setText(f"{t('Total a receber:', idioma)} {CurrencyFormatter.format(total_receber)}")

            contas = self.account_controller.get_all_accounts()

            saldo_atual_total = sum(float(c.get("Saldo_Atual", 0)) for c in contas)

            self.lbl_saldo_atual.setText(
                f"{t('Saldo atual total:', idioma)} {CurrencyFormatter.format(saldo_atual_total)}"
            )

            saldo_previsto_total = saldo_atual_total - total_pagar + total_receber

            self.lbl_saldo_previsto.setText(
                f"{t('Saldo previsto:', idioma)} {CurrencyFormatter.format(saldo_previsto_total)}"
            )

            self.update_buttons_state()

        except Exception:
            logger.exception("Erro ao carregar agendamentos")
            QMessageBox.critical(self, t("Erro", idioma), t("Erro ao carregar agendamentos.", idioma))

    # ==================================================
    # FILTROS
    # ==================================================
    def apply_filter(self):
        tipo = self.filter_combo.currentText()
        termo = self.search_input.text().strip()

        idioma = Session.get_config("idioma", "Português")

        if tipo == t("Todos", idioma):
            tipo = None

        self.load_agendamentos(tipo, termo)

    def apply_quick_filter(self, tipo):
        idioma = Session.get_config("idioma", "Português")

        self.filter_combo.setCurrentText(tipo if tipo else t("Todos", idioma))
        self.search_input.clear()
        self.load_agendamentos(tipo)

    # ==================================================
    # AÇÕES
    # ==================================================
    def open_add_dialog(self):
        dialog = AgendamentoDialog(self)
        if dialog.exec_():
            self.load_agendamentos()

    def open_edit_dialog(self):
        ag = self._get_selected()
        if not ag:
            return

        dialog = AgendamentoDialog(self, ag)
        if dialog.exec_():
            self.load_agendamentos()

    def cancel_agendamento(self):
        ag = self._get_selected()
        if not ag:
            return

        self.schedule_controller.cancel_schedule(ag)
        self.load_agendamentos()

    def execute_agendamento(self):
        ag = self._get_selected()
        if not ag:
            return

        self.main_controller.execute_schedule(ag)
        self.load_agendamentos()

    # ==================================================
    # AUX
    # ==================================================
    def _get_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return None

        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def update_buttons_state(self):
        enabled = self.table.currentRow() >= 0
        self.edit_btn.setEnabled(enabled)
        self.cancel_btn.setEnabled(enabled)
        self.execute_btn.setEnabled(enabled)

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _retranslate(self, idioma):
        self.sidebar.setTitle(t("Agendamentos", idioma))

        self.btn_receber.setText(t("Contas a Receber", idioma))
        self.btn_pagar.setText(t("Contas a Pagar", idioma))
        self.btn_transfer.setText(t("Transferências", idioma))
        self.btn_todos.setText(t("Todos", idioma))

        self.filter_label.setText(t("Filtrar por:", idioma))
        self.search_input.setPlaceholderText(t("Pesquisar...", idioma))

        self.filter_combo.clear()
        self.filter_combo.addItems([
            t("Todos", idioma),
            t("Contas a Receber", idioma),
            t("Contas a Pagar", idioma),
            t("Transferências", idioma),
        ])

        self.add_btn.setText(t("Adicionar", idioma))
        self.edit_btn.setText(t("Editar", idioma))
        self.cancel_btn.setText(t("Cancelar", idioma))
        self.execute_btn.setText(t("Executar", idioma))

        self.table.setHorizontalHeaderLabels([
            "ID",
            t("Conta", idioma),
            t("Favorecido", idioma),
            t("Descrição", idioma),
            t("Vencimento", idioma),
            t("Valor", idioma),
            t("Status", idioma),
        ])