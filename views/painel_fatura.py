import logging
from datetime import datetime, date

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QDialog,
    QDialogButtonBox, QLineEdit, QDateEdit, QToolButton,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from controllers.fatura_controller import FaturaController
from controllers.account_controller import AccountController


from core.i18n import t

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

        hoje = datetime.today()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year

        self._init_ui()

    # ======================================================
    # API PÚBLICA
    # ======================================================
    def set_cartao(self, cartao: dict):
        if not cartao:
            return

        self.cartao = cartao
        self.mes_combo.setCurrentIndex(self.mes_atual - 1)
        self.ano_combo.setCurrentText(str(self.ano_atual))
        self.atualizar_painel()

    # ======================================================
    # UI
    # ======================================================
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # CABEÇALHO
        self.nome_cartao_label = QLabel("-")
        self.nome_cartao_label.setObjectName("title")

        self.final_cartao_label = QLabel("")
        self.final_cartao_label.setObjectName("muted")

        self.datas_fatura_label = QLabel("")
        self.datas_fatura_label.setObjectName("muted")

        layout.addWidget(self.nome_cartao_label)
        layout.addWidget(self.final_cartao_label)
        layout.addWidget(self.datas_fatura_label)

        # TOOLBAR
        acoes = QHBoxLayout()

        btn_lancar = QToolButton(text="Lançamento")
        btn_lancar.clicked.connect(self.add_transaction)

        btn_pagar = QToolButton(text="Pagar Fatura")
        btn_pagar.clicked.connect(self.pagar_fatura)

        btn_exportar = QToolButton(text="Exportar PDF")
        btn_exportar.clicked.connect(self.exportar_pdf)

        acoes.addWidget(btn_lancar)
        acoes.addWidget(btn_pagar)
        acoes.addWidget(btn_exportar)
        acoes.addStretch()
        layout.addLayout(acoes)

        # LIMITE
        info = QHBoxLayout()

        self.limite_label = QLabel("R$ 0,00")
        self.disponivel_label = QLabel("R$ 0,00")

        info.addWidget(QLabel("Limite:"))
        info.addWidget(self.limite_label)
        info.addSpacing(30)
        info.addWidget(QLabel("Disponível:"))
        info.addWidget(self.disponivel_label)
        info.addStretch()

        layout.addLayout(info)

        # FILTROS
        filtros = QHBoxLayout()

        self.mes_combo = QComboBox()
        self.mes_combo.addItems([str(i) for i in range(1, 13)])
        self.mes_combo.currentIndexChanged.connect(self.atualizar_painel)

        self.ano_combo = QComboBox()
        self.ano_combo.addItems([
            str(self.ano_atual - 1),
            str(self.ano_atual),
            str(self.ano_atual + 1),
        ])
        self.ano_combo.currentIndexChanged.connect(self.atualizar_painel)

        filtros.addWidget(QLabel("Mês:"))
        filtros.addWidget(self.mes_combo)
        filtros.addWidget(QLabel("Ano:"))
        filtros.addWidget(self.ano_combo)
        filtros.addStretch()

        layout.addLayout(filtros)

        # TABELA
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Data", "Descrição", "Valor", "Categoria"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        # RESUMO
        self.resumo_label = QLabel("Total: R$ 0,00 | Lançamentos: 0")
        layout.addWidget(self.resumo_label)

    # ======================================================
    # DADOS
    # ======================================================
    def atualizar_painel(self):
        if not self.cartao:
            return

        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())

        self.nome_cartao_label.setText(self.cartao.get("nome", ""))
        final = self.cartao.get("final")
        self.final_cartao_label.setText(f"**** {final}" if final else "")

        fechamento, vencimento = self._calcular_datas_fatura(mes, ano)

        self.datas_fatura_label.setText(
            f"Fechamento: {DateFormatter.us_to_br(fechamento)} | "
            f"Vencimento: {DateFormatter.us_to_br(vencimento)}"
        )

        extrato = self.controller.listar_lancamentos_fatura(
            self.cartao["ID_Cartao"],
            mes,
            ano
        ) or []

        self.table.setRowCount(0)
        total = 0.0

        for item in extrato:
            valor = float(item.get("Valor", 0))
            total += valor

            self._add_row(
                item.get("Data"),
                item.get("Descricao"),
                valor,
                item.get("Categoria")
            )

        self.resumo = {
            "total_fatura": total,
            "quantidade_lancamentos": len(extrato),
        }

        self._atualizar_limites()
        self._atualizar_resumo()

    # ======================================================
    # HELPERS
    # ======================================================
    def _calcular_datas_fatura(self, mes, ano):
        dia_fech = self.cartao["dia_fechamento"]
        dia_venc = self.cartao["dia_vencimento"]

        fechamento = date(ano, mes, dia_fech)

        if dia_venc <= dia_fech:
            vencimento = date(
                ano + (1 if mes == 12 else 0),
                1 if mes == 12 else mes + 1,
                dia_venc
            )
        else:
            vencimento = date(ano, mes, dia_venc)

        return fechamento, vencimento

    def _add_row(self, data, descricao, valor, categoria):
        row = self.table.rowCount()
        self.table.insertRow(row)

        data_formatada = DateFormatter.iso_to_br(data)

        self.table.setItem(row, 0, QTableWidgetItem(data_formatada))
        self.table.setItem(row, 1, QTableWidgetItem(descricao or ""))

        valor_item = QTableWidgetItem(
            CurrencyFormatter.format(valor)
        )

        # Despesa do cartão é valor POSITIVO → vermelho
        valor_item.setForeground(
            QColor("#c62828")
        )

        self.table.setItem(row, 2, valor_item)
        self.table.setItem(row, 3, QTableWidgetItem(categoria or ""))

    def _atualizar_limites(self):
        limite = float(self.cartao.get("limite", 0))
        disponivel = self.controller.obter_limite_disponivel(
            self.cartao["ID_Cartao"]
        )

        self.limite_label.setText(CurrencyFormatter.format(limite))
        self.disponivel_label.setText(CurrencyFormatter.format(disponivel))

    def _atualizar_resumo(self):
        self.resumo_label.setText(
            f"Total: {CurrencyFormatter.format(self.resumo.get('total_fatura', 0))} | "
            f"Lançamentos: {self.resumo.get('quantidade_lancamentos', 0)}"
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
            self.atualizar_painel()

    def pagar_fatura(self):
        total = self.resumo.get("total_fatura", 0.0)

        if total <= 0:
            QMessageBox.information(self, "Aviso", "Não há valor pendente.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Pagar Fatura")
        layout = QVBoxLayout(dialog)

        valor_input = QLineEdit(str(total))
        layout.addWidget(QLabel("Valor a pagar:"))
        layout.addWidget(valor_input)

        conta_combo = QComboBox()
        contas = self.account_controller.get_all_accounts() 

        for conta in contas:
            conta_combo.addItem(
                f"{conta['Nome_Conta']} "
                f"({CurrencyFormatter.format(conta['Saldo_Atual'])})",
                conta["ID_Conta"]
            )

        layout.addWidget(QLabel("Conta:"))
        layout.addWidget(conta_combo)

        data_input = QDateEdit(QDate.currentDate())
        data_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data:"))
        layout.addWidget(data_input)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(botoes)

        def confirmar():
            try:
                valor_pago = float(valor_input.text().replace(",", "."))
            except ValueError:
                QMessageBox.warning(self, "Erro", "Valor inválido.")
                return

            self.controller.pagar_fatura(
                id_cartao=self.cartao["ID_Cartao"],
                id_conta=conta_combo.currentData(),
                mes=int(self.mes_combo.currentText()),
                ano=int(self.ano_combo.currentText()),
                data_pagamento=data_input.date().toString("yyyy-MM-dd"),
                valor_pago=valor_pago
            )

            dialog.accept()
            self.atualizar_painel()

        botoes.accepted.connect(confirmar)
        botoes.rejected.connect(dialog.reject)

        dialog.exec_()

    def exportar_pdf(self):
        # ask user where to save the PDF
        mes = int(self.mes_combo.currentText())
        ano = int(self.ano_combo.currentText())
        default_name = f"fatura_{self.cartao.get('ID_Cartao', 'cartao')}_{mes}_{ano}.pdf"
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", default_name, "PDF Files (*.pdf)")
        if not caminho:
            return

        # use the existing controller instance
        self.controller.exportar_fatura_pdf(
            id_cartao=self.cartao["ID_Cartao"],
            mes=mes,
            ano=ano,
            caminho=caminho
        )
