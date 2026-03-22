import logging
import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QToolButton, QLabel, QMessageBox,
    QFileDialog, QAbstractItemView,
    QInputDialog, QProgressDialog, QDialog,
    QComboBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QIcon

from controllers.transaction_controller import TransactionController
from controllers.category_controller import CategoryController
from controllers.favorecido_controller import FavorecidoController
from controllers.ia_import_controller import IAImportController
from controllers.ia_export_controller import IAExportController

from views.TransactionDialog import TransactionDialog
from views.TransferDialog import TransferDialog
from views.editar_transacao_dialog import EditTransactionDialog
from views.importacaoTempeorariaDialog import ImportacaoTemporariaDialog

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter

from workers.import_worker import ImportWorker
from core.theme_manager import ThemeManager
from core.session import Session

logger = logging.getLogger(__name__)


class PainelAccount(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.conta = None
        usuario = Session.get_usuario() or {}
        self.usuario_id = usuario.get("ID_Usuario")

        self.filtro_periodo = "Mês Atual"

        self.transaction_controller = TransactionController()
        self.category_controller = CategoryController()
        self.favorecido_controller = FavorecidoController()
        self.ia_import_controller = IAImportController()
        self.ia_export_controller = IAExportController()
        self.progress_bar = QProgressDialog("Importando extrato...", "Cancelar", 0, 100, self)
        self.import_worker = None

        self._montar_ui()

    # ==================================================
    # UTIL
    # ==================================================

    def _icon(self, nome):
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_path, ".."))
        icon_path = os.path.join(project_root, "assets", "icons", f"{nome}.svg")
        return QIcon(icon_path)

    # ==================================================
    # UI
    # ==================================================

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()

        def criar_botao(texto, icon_name, callback):
            btn = QToolButton()
            btn.setText(texto)
            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(texto)
            btn.clicked.connect(callback)
            return btn

        btn_add = criar_botao("Lançamento", "add", self.add_transaction)
        btn_transfer = criar_botao("Transferência", "transfer", self.transfer_transaction)
        btn_edit = criar_botao("Editar", "edit", self.edit_transaction)
        btn_delete = criar_botao("Excluir", "delete", self.delete_transaction)
        btn_import = criar_botao("Importar", "import", self.importar_extrato)
        btn_export = criar_botao("Exportar", "export", self.exportar_extrato)

        for b in (btn_add, btn_transfer, btn_edit, btn_delete, btn_import, btn_export):
            toolbar.addWidget(b)

        toolbar.addStretch()

        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems([
            "Mês Atual",
            "Últimos 3 Meses",
            "Ano Atual",
            "Todos"
        ])
        self.combo_filtro.currentTextChanged.connect(self._alterar_filtro)

        toolbar.addWidget(QLabel("Período:"))
        toolbar.addWidget(self.combo_filtro)

        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Data", "Número", "Descrição", "Favorecido",
            "Categoria", "Receita", "Despesa", "Saldo"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.resumo = QLabel()
        layout.addWidget(self.resumo)

    # ==================================================
    # CONTA
    # ==================================================

    def set_conta(self, conta: dict):
        self.conta = conta
        self.carregar_historico()

    # ==================================================
    # FILTRO
    # ==================================================

    def _alterar_filtro(self, texto):
        self.filtro_periodo = texto
        self.carregar_historico()

    def _obter_periodo(self):
        hoje = datetime.today()

        if self.filtro_periodo == "Mês Atual":
            inicio = datetime(hoje.year, hoje.month, 1)
        elif self.filtro_periodo == "Últimos 3 Meses":
            mes = hoje.month - 2
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1
            inicio = datetime(ano, mes, 1)
        elif self.filtro_periodo == "Ano Atual":
            inicio = datetime(hoje.year, 1, 1)
        else:
            inicio = datetime(2000, 1, 1)

        fim = hoje
        return inicio.strftime("%Y-%m-%d"), fim.strftime("%Y-%m-%d")

    # ==================================================
    # HISTÓRICO
    # ==================================================

    def carregar_historico(self):
        if not self.conta:
            return

        inicio, fim = self._obter_periodo()

        transacoes = self.transaction_controller.get_transactions_by_account_periodo(
            self.conta["ID_Conta"],
            (inicio, fim)
        )

        self._preencher_tabela(transacoes or [])

    def _aplicar_estilo_valor(self, item, tipo):
        cor = ThemeManager.get_finance_color(tipo)
        if cor:
            item.setForeground(QColor(cor))
        fonte = QFont()
        fonte.setBold(True)
        item.setFont(fonte)

    def _preencher_tabela(self, transacoes):

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        saldo = 0.0
        receitas = 0.0
        despesas = 0.0

        for t in transacoes:
            r = self.table.rowCount()
            self.table.insertRow(r)

            self.table.setItem(r, 0, QTableWidgetItem(
                DateFormatter.iso_to_br(t["Data"])
            ))

            self.table.setItem(r, 1, QTableWidgetItem(
                str(t["ID_Transacao"])
            ))

            self.table.setItem(r, 2, QTableWidgetItem(
                t.get("Descricao", "")
            ))

            valor = float(t["Valor"])

            if valor > 0:
                receitas += valor
                item = QTableWidgetItem(CurrencyFormatter.format(valor))
                self._aplicar_estilo_valor(item, "receita")
                self.table.setItem(r, 5, item)
                self.table.setItem(r, 6, QTableWidgetItem(""))
            else:
                despesas += abs(valor)
                self.table.setItem(r, 5, QTableWidgetItem(""))
                item = QTableWidgetItem(
                    CurrencyFormatter.format(abs(valor))
                )
                self._aplicar_estilo_valor(item, "despesa")
                self.table.setItem(r, 6, item)

            saldo += valor

            item_saldo = QTableWidgetItem(
                CurrencyFormatter.format(saldo)
            )

            if saldo >= 0:
                self._aplicar_estilo_valor(item_saldo, "receita")
            else:
                self._aplicar_estilo_valor(item_saldo, "despesa")

            self.table.setItem(r, 7, item_saldo)

        self.table.setSortingEnabled(True)

        self.resumo.setText(
            f"Créditos: {CurrencyFormatter.format(receitas)} | "
            f"Débitos: {CurrencyFormatter.format(despesas)} | "
            f"Saldo: {CurrencyFormatter.format(saldo)}"
        )

    # ==================================================
    # AÇÕES
    # ==================================================

    def add_transaction(self):
        if not self.conta:
            QMessageBox.warning(self, "Lançamento", "Nenhuma conta selecionada.")
            return

        dlg = TransactionDialog(
            self,
            contexto="conta",
            id_contexto=self.conta["ID_Conta"]
        )

        if dlg.exec_() == QDialog.Accepted:
            self.carregar_historico()

    def transfer_transaction(self):
        dlg = TransferDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.carregar_historico()

    def edit_transaction(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Editar", "Selecione uma transação.")
            return

        id_transacao = int(self.table.item(row, 1).text())
        transacao = self.transaction_controller.get_transaction_by_id(id_transacao)

        dlg = EditTransactionDialog(transacao, self)
        if dlg.exec_() == QDialog.Accepted:
            self.carregar_historico()

    def delete_transaction(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Excluir", "Selecione uma transação.")
            return

        id_transacao = int(self.table.item(row, 1).text())

        confirm = QMessageBox.question(
            self,
            "Excluir",
            "Deseja realmente excluir esta transação?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.transaction_controller.delete_transaction(id_transacao)
            self.carregar_historico()

   # ===================================================
   # IMPORTAÇÃO
   # ===================================================
    def importar_extrato(self):

        if not self.conta:
            QMessageBox.warning(self, "Importar", "Nenhuma conta selecionada.")
            return

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir arquivo",
            "",
            "CSV Files (*.csv);;XLSX Files (*.xlsx);;PDF Files (*.pdf)"
        )

        if not arquivo:
            return

        try:
            self.ia_import_controller.importar_arquivo(
                conta=self.conta,
                caminho=arquivo,
                progress_callback=self._mostrar_progresso_importacao
            )

            QMessageBox.information(
                self,
                "Importação concluída",
                f"Extrato importado com sucesso de:\n{arquivo}"
            )

        except Exception as e:
            logger.exception("Erro ao importar extrato")
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao importar extrato:\n{str(e)}"
            )

    # ==================================================
    # EXPORTAÇÃO
    # ==================================================

    def exportar_extrato(self):

        if not self.conta:
            QMessageBox.warning(self, "Exportar", "Nenhuma conta selecionada.")
            return

        formato, ok = QInputDialog.getItem(
            self,
            "Exportar Extrato",
            "Escolha o formato:",
            ["CSV", "XLSX", "PDF"],
            0,
            False
        )

        if not ok or not formato:
            return

        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar arquivo",
            "",
            f"{formato} (*.{formato.lower()})"
        )

        if not arquivo:
            return

        try:
            inicio, fim = self._obter_periodo()

            transacoes = self.transaction_controller.get_transactions_by_account_periodo(
                self.conta["ID_Conta"],
                (inicio, fim)
            )

            if not transacoes:
                QMessageBox.information(
                    self,
                    "Exportar",
                    "Nenhuma transação encontrada para o período selecionado."
                )
                return

            self.ia_export_controller.exportar_extrato_conta(
                transacoes=transacoes,
                conta=self.conta,
                data_inicio=inicio,
                data_fim=fim,
                formato=formato,
                caminho=arquivo
            )

            QMessageBox.information(
                self,
                "Exportação concluída",
                f"Extrato exportado com sucesso em:\n{arquivo}"
            )

        except Exception as e:
            logger.exception("Erro ao exportar extrato")
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao exportar extrato:\n{str(e)}"
            )

    # ==================================================
    # FECHAR
    # ==================================================

    def closeEvent(self, event):
        try:
            if self.import_worker and self.import_worker.isRunning():
                self.import_worker.quit()
                self.import_worker.wait()
        except Exception:
            pass

        super().closeEvent(event)


    # ==================================================
    # EXPORTAÇÃO
    # ==================================================

    
    def _mostrar_progresso_importacao(self, progresso):
        self.progress_bar.setValue(progresso)
        self.progress_bar.setVisible(progresso < 100)
