# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QDialog,
    QToolButton, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon

from controllers.fatura_controller import FaturaController
from controllers.account_controller import AccountController

from core.theme_manager import ThemeManager
from core.translator_app import TranslatorApp

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter

from utilitarios.ion_path import IonPath
from views.TransactionDialog import TransactionDialog

logger = logging.getLogger(__name__)


class PainelFatura(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = FaturaController()
        self.account_controller = AccountController()

        self.cartao = None
        self.page = 0
        self.limit = 50
        self.filtro_status = "Todos"
        self._icon_cache = {}
        hoje = datetime.today()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year

        self.setWindowTitle("Fatura")

        self._init_ui()

        TranslatorApp.bind(self._on_translate, self)

    # ======================================================
    # REATIVIDADE
    # ======================================================
    def _on_translate(self, *_):
        self._carregar()

    # ======================================================
    #  ICONE
    # ======================================================
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
    # UI
    # ======================================================
    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.nome_cartao_label = QLabel("-")
        self.nome_cartao_label.setObjectName("pageTitle")

        self.info_label = QLabel("")
        self.info_label.setObjectName("muted")

        layout.addWidget(self.nome_cartao_label)
        layout.addWidget(self.info_label)

        # TOOLBAR
        toolbar = QHBoxLayout()

        def btn(texto, fn):
            b = QToolButton()
            b.setText(texto)
            b.clicked.connect(fn)
            return b

        self.btn_lancar = btn("+ Lançar", self.add_transaction)
        self.btn_lancar.setIcon(self._icon("add"))
        self.btn_pagar = btn("Pagar", self.pagar_fatura)
        self.btn_pagar.setIcon(self._icon("pay"))
        self.btn_exportar = btn("PDF", self.exportar_pdf)
        self.btn_exportar.setIcon(self._icon("pdf"))

        toolbar.addWidget(self.btn_lancar)
        toolbar.addWidget(self.btn_pagar)
        toolbar.addWidget(self.btn_exportar)

        toolbar.addStretch()

        self.filtro_combo = QComboBox()
        self.filtro_combo.addItem("Todos", "Todos")
        self.filtro_combo.addItem("Abertos", "Abertos")
        self.filtro_combo.addItem("Pagos", "Pagos")
        self.filtro_combo.currentIndexChanged.connect(self._on_filtro_changed)

        toolbar.addWidget(QLabel("Status:"))
        toolbar.addWidget(self.filtro_combo)

        layout.addLayout(toolbar)

        # FILTROS
        filtros = QHBoxLayout()

        self.mes_combo = QComboBox()
        self.mes_combo.addItems([str(i) for i in range(1, 13)])
        self.mes_combo.setCurrentIndex(self.mes_atual - 1)
        self.mes_combo.currentIndexChanged.connect(self._reset_paginacao)

        self.ano_combo = QComboBox()
        self.ano_combo.addItems(
            [str(self.ano_atual - 1), str(self.ano_atual), str(self.ano_atual + 1)]
        )
        self.ano_combo.setCurrentText(str(self.ano_atual))
        self.ano_combo.currentIndexChanged.connect(self._reset_paginacao)

        filtros.addWidget(QLabel("Mês:"))
        filtros.addWidget(self.mes_combo)
        filtros.addWidget(QLabel("Ano:"))
        filtros.addWidget(self.ano_combo)

        layout.addLayout(filtros)

        # TABELA
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Data", "Descrição", "Categoria", "Valor", "Status"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.table)

        # PAGINAÇÃO
        paginacao = QHBoxLayout()

        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.label_page = QLabel()

        self.btn_prev.clicked.connect(self._prev_page)
        self.btn_next.clicked.connect(self._next_page)

        paginacao.addWidget(self.btn_prev)
        paginacao.addWidget(self.label_page)
        paginacao.addWidget(self.btn_next)

        layout.addLayout(paginacao)

        # RESUMO
        self.resumo_label = QLabel()
        layout.addWidget(self.resumo_label)

        # FUTURAS
        self.futuras_label = QLabel()
        self.futuras_label.setObjectName("muted")
        layout.addWidget(self.futuras_label)

    # ======================================================
    # CONTROLE
    # ======================================================
    def set_cartao(self, cartao):
        self.cartao = cartao
        self.page = 0
        self._carregar()

    def _reset_paginacao(self):
        self.page = 0
        self._carregar()

    def _on_filtro_changed(self):
        self.filtro_status = self.filtro_combo.currentData()
        self._reset_paginacao()

    def _next_page(self):
        self.page += 1
        self._carregar()

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._carregar()

    # ======================================================
    # DADOS (100% CONTROLADOS)
    # ======================================================
    def _carregar(self):

        if not self.cartao:
            return

        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())

        painel = self.controller.get_painel_cartao(
            id_cartao=self.cartao["ID_Cartao"],
            mes=mes,
            ano=ano,
            page=self.page,
            limit=self.limit,
            status=self.filtro_status
        ) or {}

        self._render_header(painel.get("resumo", {}))
        self._render_tabela(painel.get("lancamentos", []))
        self._render_resumo(painel.get("fatura", {}))
        self._render_futuras(painel.get("futuras", {}))

        total = painel.get("total_registros", 0)
        total_paginas = max(1, (total // self.limit) + 1)

        self.label_page.setText(f"{self.page + 1} / {total_paginas}")
        self.nome_cartao_label.setText(self.cartao.get("Nome", ""))

    # ======================================================
    # RENDER
    # ======================================================
    def _render_header(self, resumo):

        self.info_label.setText(
            f"Limite: {CurrencyFormatter.format(resumo.get('limite', 0))} | "
            f"Devedor: {CurrencyFormatter.format(resumo.get('saldo_devedor', 0))} | "
            f"Disponível: {CurrencyFormatter.format(resumo.get('disponivel', 0))}"
        )

    def _render_resumo(self, fatura):

        self.resumo_label.setText(
            f"Fatura: {CurrencyFormatter.format(fatura.get('total', 0))} | "
            f"Abertos: {CurrencyFormatter.format(fatura.get('abertos', 0))} | "
            f"Pagos: {CurrencyFormatter.format(fatura.get('pagos', 0))}"
        )

    def _render_futuras(self, futuras):

        texto = "Próximas faturas:\n"

        if not futuras:
            texto += "Nenhuma"
        else:
            for mes, valor in futuras.items():
                texto += f"{mes} → {CurrencyFormatter.format(valor)}\n"

        self.futuras_label.setText(texto)

    def _render_tabela(self, dados):

        self.table.setRowCount(0)
        for item in dados:
            row = self.table.rowCount()
            self.table.insertRow(row)

            valor = float(item.get("Valor", 0))
            pago = item.get("Paga")

            cor = (
                ThemeManager.get_color("success")
                if pago
                else ThemeManager.get_color("danger")
            )

            status = "Pago" if pago else "Aberto"

            descricao = item.get("Descricao", "")

            if item.get("Parcela_Atual") and item.get("Num_Parcelas"):
                descricao += f" ({item['Parcela_Atual']}/{item['Num_Parcelas']})"

            self.table.setItem(row, 0, QTableWidgetItem(
                DateFormatter.iso_to_br(item.get("Data", ""))
            ))

            
            self.table.setItem(row, 1, QTableWidgetItem(descricao))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("Categoria", ""))))

            valor_item = QTableWidgetItem(CurrencyFormatter.format(valor))
            valor_item.setForeground(QColor(cor))

            self.table.setItem(row, 3, valor_item)

            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(cor))
            self.table.setItem(row, 4, status_item)

    # ======================================================
    # AÇÕES
    # ======================================================
    def add_transaction(self):
        dialog = TransactionDialog(
            parent=self,
            contexto="cartao",
            id_contexto=self.cartao["ID_Cartao"]
        )
        if dialog.exec_() == QDialog.Accepted:
            self._carregar()

    def pagar_fatura(self):

        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())

        contas = self.account_controller.get_all_accounts()

        if not contas:
            QMessageBox.warning(self, "Erro", "Nenhuma conta disponível")
            return

        conta_id = contas[0]["ID_Conta"]

        try:
            self.controller.pagar_fatura(
                id_cartao=self.cartao["ID_Cartao"],
                id_conta=conta_id,
                mes=mes,
                ano=ano
            )

            QMessageBox.information(self, "Sucesso", "Fatura paga com sucesso")
            self._carregar()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def exportar_pdf(self):

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", "", "PDF Files (*.pdf)"
        )

        if not caminho:
            return

        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())

        dados = self.controller.listar_lancamentos_fatura(
            self.cartao["ID_Cartao"], mes, ano
        )

        try:
            self.controller.exportar_fatura_pdf(self.cartao, dados, caminho)
            QMessageBox.information(self, "Sucesso", "PDF exportado")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
