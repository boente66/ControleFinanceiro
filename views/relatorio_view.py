# relatorio_view.py
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QStackedWidget, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QFrame, QTextEdit, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from controllers.relatorio_controller import RelatorioController
from utilitarios.makepdf import MakePDF
from utilitarios.currency_formatter import CurrencyFormatter


logger = logging.getLogger(__name__)


class RelatorioView(QWidget):
    """
    Visualização de relatórios financeiros.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        
        

        self.controller = RelatorioController()

        self.setWindowTitle("Relatórios")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)

        titulo = QLabel("RELATÓRIOS")
        titulo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(titulo)

        self.sections = QListWidget()
        self.sections.addItems([
            "Relatório Diário",
            "Relatório Anual",
            "Informe de Rendimentos"
        ])
        sidebar_layout.addWidget(self.sections)

        sidebar_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        main_layout.addWidget(sidebar, 0)

        # Área principal
        self.stacked = QStackedWidget()
        self.stacked.addWidget(self._relatorio_diario_widget())
        self.stacked.addWidget(self._relatorio_anual_widget())
        self.stacked.addWidget(self._informe_relatorio_widget())
        main_layout.addWidget(self.stacked, 1)

        self.sections.currentRowChanged.connect(self.stacked.setCurrentIndex)
        self.sections.setCurrentRow(0)

    # ==================================================
    # FORMATAÇÃO SEGURA
    # ==================================================
    def _format_currency(self, value):
        try:
            return CurrencyFormatter.format(float(value))
        except Exception:
            return str(value)

    # ==================================================
    # RELATÓRIO DIÁRIO
    # ==================================================
    def _relatorio_diario_widget(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Relatório Diário"))

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Últimos (dias):"))

        self.input_days = QComboBox()
        self.input_days.addItems(["7", "15", "30", "90"])
        ctrl.addWidget(self.input_days)

        btn = QPushButton("Atualizar")
        btn.clicked.connect(self.load_relatorio_diario)
        ctrl.addWidget(btn)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_diario = QTableWidget()
        self.table_diario.setColumnCount(5)
        self.table_diario.setHorizontalHeaderLabels(
            ["Data", "Categoria", "Receita", "Despesa", "Economia"]
        )
        layout.addWidget(self.table_diario, 1)

        export_btn = QPushButton("Exportar CSV")
        export_btn.clicked.connect(
            lambda: self.export_table_csv(self.table_diario, "relatorio_diario")
        )
        layout.addWidget(export_btn)

        self.load_relatorio_diario()
        return w

    def load_relatorio_diario(self):
        dias = int(self.input_days.currentText())
        resp = self.controller.relatorio_diario(dias)
        self._preencher_tabela(self.table_diario, resp)

    # ==================================================
    # RELATÓRIO ANUAL
    # ==================================================
    def _relatorio_anual_widget(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Relatório Anual"))

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Ano:"))

        self.combo_ano_anual = QComboBox()
        ano_atual = datetime.now().year
        self.combo_ano_anual.addItems(
            [str(y) for y in range(ano_atual, ano_atual - 6, -1)]
        )
        ctrl.addWidget(self.combo_ano_anual)

        btn = QPushButton("Atualizar")
        btn.clicked.connect(self.load_relatorio_anual)
        ctrl.addWidget(btn)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_anual = QTableWidget()
        self.table_anual.setColumnCount(5)
        self.table_anual.setHorizontalHeaderLabels(
            ["Mês", "Categoria", "Receita", "Despesa", "Economia"]
        )
        layout.addWidget(self.table_anual, 1)

        export_btn = QPushButton("Exportar CSV")
        export_btn.clicked.connect(
            lambda: self.export_table_csv(self.table_anual, "relatorio_anual")
        )
        layout.addWidget(export_btn)

        self.load_relatorio_anual()
        return w

    def load_relatorio_anual(self):
        ano = int(self.combo_ano_anual.currentText())
        resp = self.controller.relatorio_anual(ano)
        self._preencher_tabela(self.table_anual, resp)

    # ==================================================
    # INFORME
    # ==================================================
    def _informe_relatorio_widget(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Informe de Rendimentos (IRPF)"))

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Ano base:"))

        self.year_combo = QComboBox()
        ano_atual = datetime.now().year
        self.year_combo.addItems(
            [str(y) for y in range(ano_atual, ano_atual - 6, -1)]
        )
        ctrl.addWidget(self.year_combo)

        btn_preview = QPushButton("Visualizar")
        btn_preview.clicked.connect(self.preview_informe)
        ctrl.addWidget(btn_preview)

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.clicked.connect(self.gerar_e_exportar_pdf)
        ctrl.addWidget(btn_pdf)

        btn_print = QPushButton("Imprimir")
        btn_print.clicked.connect(self.imprimir_informe)
        ctrl.addWidget(btn_print)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.pdf_view = QTextEdit()
        self.pdf_view.setReadOnly(True)
        layout.addWidget(self.pdf_view, 1)

        return w

    def preview_informe(self):
        ano = int(self.year_combo.currentText())
        texto = self.controller.gerar_texto_informe( ano)
        self.pdf_view.setPlainText(texto)

    # ==================================================
    # UTIL
    # ==================================================
    def _preencher_tabela(self, tabela, dados):
        tabela.setRowCount(0)
        if not dados:
            return

        for i, row in enumerate(dados):
            tabela.insertRow(i)
            for j, val in enumerate(row.values()):
                if isinstance(val, (int, float)):
                    val = self._format_currency(val)
                tabela.setItem(i, j, QTableWidgetItem(str(val)))

        tabela.resizeColumnsToContents()

    def gerar_e_exportar_pdf(self):
        texto = self.pdf_view.toPlainText()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Gere o informe antes.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", "informe.pdf", "PDF Files (*.pdf)"
        )
        if caminho:
            MakePDF.gerar_pdf(caminho, "Informe de Rendimentos", texto)

    def imprimir_informe(self):
        printer = QPrinter()
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            self.pdf_view.print_(printer)

    def export_table_csv(self, tabela, prefix):
        if tabela.rowCount() == 0:
            QMessageBox.information(self, "Exportar CSV", "Tabela vazia.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar CSV", f"{prefix}.csv", "CSV Files (*.csv)"
        )

        if not caminho:
            return

        with open(caminho, "w", encoding="utf-8") as f:
            headers = [
                tabela.horizontalHeaderItem(c).text()
                for c in range(tabela.columnCount())
            ]
            f.write(",".join(headers) + "\n")

            for r in range(tabela.rowCount()):
                row = [
                    tabela.item(r, c).text() if tabela.item(r, c) else ""
                    for c in range(tabela.columnCount())
                ]
                f.write(",".join(f'"{v}"' for v in row) + "\n")
