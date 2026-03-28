import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QDialog,
    QDialogButtonBox, QLineEdit, QDateEdit, QToolButton,
    QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from controllers.fatura_controller import FaturaController
from controllers.account_controller import AccountController

from core.theme_manager import ThemeManager
from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter

from views.TransactionDialog import TransactionDialog

logger = logging.getLogger(__name__)


class PainelFatura(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = FaturaController()
        self.account_controller = AccountController()

        self.cartao = None
        self.resumo = {}

        # paginação
        self.page = 0
        self.limit = 50

        # filtro
        self.filtro_status = "Todos"

        hoje = datetime.today()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year

        self._init_ui()

    # ======================================================
    # UI
    # ======================================================
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # HEADER
        self.nome_cartao_label = QLabel("-")
        self.nome_cartao_label.setObjectName("pageTitle")

        self.info_label = QLabel("")
        self.info_label.setObjectName("muted")

        layout.addWidget(self.nome_cartao_label)
        layout.addWidget(self.info_label)

        # TOOLBAR
        toolbar = QHBoxLayout()

        btn_lancar = QToolButton(text="Lançar")
        btn_lancar.clicked.connect(self.add_transaction)

        btn_pagar = QToolButton(text="Pagar")
        btn_pagar.clicked.connect(self.pagar_fatura)

        btn_exportar = QToolButton(text="PDF")
        btn_exportar.clicked.connect(self.exportar_pdf)

        toolbar.addWidget(btn_lancar)
        toolbar.addWidget(btn_pagar)
        toolbar.addWidget(btn_exportar)

        toolbar.addStretch()

        self.filtro_combo = QComboBox()
        self.filtro_combo.addItems(["Todos", "Abertos", "Pagos"])
        self.filtro_combo.currentTextChanged.connect(self._on_filtro_changed)

        toolbar.addWidget(QLabel("Status:"))
        toolbar.addWidget(self.filtro_combo)

        layout.addLayout(toolbar)

        # FILTRO DATA
        filtros = QHBoxLayout()

        self.mes_combo = QComboBox()
        self.mes_combo.addItems([str(i) for i in range(1, 13)])
        self.mes_combo.setCurrentIndex(self.mes_atual - 1)
        self.mes_combo.currentIndexChanged.connect(self._reset_paginacao)

        self.ano_combo = QComboBox()
        self.ano_combo.addItems([
            str(self.ano_atual - 1),
            str(self.ano_atual),
            str(self.ano_atual + 1),
        ])
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
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        # PAGINAÇÃO
        paginacao = QHBoxLayout()

        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.label_page = QLabel("Página 1")

        self.btn_prev.clicked.connect(self._prev_page)
        self.btn_next.clicked.connect(self._next_page)

        paginacao.addWidget(self.btn_prev)
        paginacao.addWidget(self.label_page)
        paginacao.addWidget(self.btn_next)

        layout.addLayout(paginacao)

        # RESUMO
        self.resumo_label = QLabel("")
        layout.addWidget(self.resumo_label)

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

    def _on_filtro_changed(self, texto):
        self.filtro_status = texto
        self._reset_paginacao()

    def _next_page(self):
        self.page += 1
        self._carregar()

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._carregar()

    # ======================================================
    # DADOS
    # ======================================================
    def _carregar(self):

        if not self.cartao:
            return

        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())

        result = self.controller.obter_fatura_paginada(
            self.cartao["ID_Cartao"],
            mes,
            ano,
            limit=self.limit,
            offset=self.page * self.limit
        )

        dados = result["dados"]
        total = result["total"]

        # filtro leve
        if self.filtro_status == "Abertos":
            dados = [d for d in dados if not d.get("Paga")]
        elif self.filtro_status == "Pagos":
            dados = [d for d in dados if d.get("Paga")]

        self._preencher_tabela(dados)
        self._atualizar_resumo(total)

        self.label_page.setText(f"Página {self.page + 1}")

        self.nome_cartao_label.setText(self.cartao.get("Nome", ""))

    # ======================================================
    # TABELA
    # ======================================================
    def _preencher_tabela(self, dados):

        self.table.setRowCount(0)

        for item in dados:
            row = self.table.rowCount()
            self.table.insertRow(row)

            valor = float(item["Valor"])
            status = "Pago" if item.get("Paga") else "Aberto"

            cor = ThemeManager.get_color("success") if item.get("Paga") \
                else ThemeManager.get_color("danger")

            self.table.setItem(row, 0, QTableWidgetItem(
                DateFormatter.iso_to_br(item["Data"])
            ))
            self.table.setItem(row, 1, QTableWidgetItem(item["Descricao"]))
            self.table.setItem(row, 2, QTableWidgetItem(
                str(item.get("Categoria", ""))
            ))

            valor_item = QTableWidgetItem(
                CurrencyFormatter.format(valor)
            )
            valor_item.setForeground(QColor(cor))

            self.table.setItem(row, 3, valor_item)
            self.table.setItem(row, 4, QTableWidgetItem(status))

    # ======================================================
    # RESUMO
    # ======================================================
    def _atualizar_resumo(self, total_registros):
        self.resumo_label.setText(
            f"Lançamentos: {total_registros} | Página: {self.page + 1}"
        )

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
            QMessageBox.warning(self, "Erro", "Nenhuma conta disponível.")
            return

        conta_id = contas[0]["ID_Conta"]  # simples (pode evoluir depois)

        try:
            self.controller.pagar_fatura(
                id_cartao=self.cartao["ID_Cartao"],
                id_conta=conta_id,
                mes=mes,
                ano=ano
            )

            QMessageBox.information(self, "Sucesso", "Fatura paga com sucesso.")
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
            self.cartao["ID_Cartao"],
            mes,
            ano
        )

        try:
            self.controller.exportar_fatura_pdf(
                self.cartao,
                dados,
                caminho
            )

            QMessageBox.information(self, "Sucesso", "PDF exportado.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
