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

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class RelatorioView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = RelatorioController()
        self._is_bound = False

        self._init_ui()
        self._apply_translation()

        if not self._is_bound:
            TranslatorApp.bind(self._on_translate)
            self._is_bound = True

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ================= SIDEBAR =================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)

        self.titulo = QLabel()
        self.titulo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.titulo)

        self.sections = QListWidget()
        sidebar_layout.addWidget(self.sections)

        sidebar_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        main_layout.addWidget(sidebar, 0)

        # ================= STACK =================
        self.stacked = QStackedWidget()

        self.w_diario = self._relatorio_diario_widget()
        self.w_anual = self._relatorio_anual_widget()
        self.w_informe = self._informe_relatorio_widget()

        self.stacked.addWidget(self.w_diario)
        self.stacked.addWidget(self.w_anual)
        self.stacked.addWidget(self.w_informe)

        main_layout.addWidget(self.stacked, 1)

        self.sections.currentRowChanged.connect(self.stacked.setCurrentIndex)
        self.sections.setCurrentRow(0)

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _on_translate(self, *_):
        self._apply_translation()

    def _apply_translation(self):

        TranslatorApp.text(self.titulo, "Relatórios")

        TranslatorApp.list_widget(
            self.sections,
            [
                "Relatório Diário",
                "Relatório Anual",
                "Informe de Rendimentos"
            ]
        )

        # tabelas
        TranslatorApp.table_headers(
            self.table_diario,
            ["Data", "Categoria", "Receita", "Despesa", "Economia"]
        )

        TranslatorApp.table_headers(
            self.table_anual,
            ["Mês", "Categoria", "Receita", "Despesa", "Economia"]
        )

    # ==================================================
    # UTIL
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

        self.lbl_diario = QLabel()
        layout.addWidget(self.lbl_diario)

        ctrl = QHBoxLayout()

        self.lbl_dias = QLabel()
        ctrl.addWidget(self.lbl_dias)

        self.input_days = QComboBox()
        self.input_days.addItems(["7", "15", "30", "90"])
        ctrl.addWidget(self.input_days)

        self.btn_diario = QPushButton()
        self.btn_diario.clicked.connect(self.load_relatorio_diario)
        ctrl.addWidget(self.btn_diario)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_diario = QTableWidget()
        self.table_diario.setColumnCount(5)
        layout.addWidget(self.table_diario, 1)

        self.btn_export_diario = QPushButton()
        self.btn_export_diario.clicked.connect(
            lambda: self.export_table_csv(self.table_diario, "relatorio_diario")
        )
        layout.addWidget(self.btn_export_diario)

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

        self.lbl_anual = QLabel()
        layout.addWidget(self.lbl_anual)

        ctrl = QHBoxLayout()

        self.lbl_ano = QLabel()
        ctrl.addWidget(self.lbl_ano)

        self.combo_ano_anual = QComboBox()
        ano_atual = datetime.now().year
        self.combo_ano_anual.addItems(
            [str(y) for y in range(ano_atual, ano_atual - 6, -1)]
        )
        ctrl.addWidget(self.combo_ano_anual)

        self.btn_anual = QPushButton()
        self.btn_anual.clicked.connect(self.load_relatorio_anual)
        ctrl.addWidget(self.btn_anual)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_anual = QTableWidget()
        self.table_anual.setColumnCount(5)
        layout.addWidget(self.table_anual, 1)

        self.btn_export_anual = QPushButton()
        self.btn_export_anual.clicked.connect(
            lambda: self.export_table_csv(self.table_anual, "relatorio_anual")
        )
        layout.addWidget(self.btn_export_anual)

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

        self.lbl_informe = QLabel()
        layout.addWidget(self.lbl_informe)

        ctrl = QHBoxLayout()

        self.lbl_base = QLabel()
        ctrl.addWidget(self.lbl_base)

        self.year_combo = QComboBox()
        ano_atual = datetime.now().year
        self.year_combo.addItems(
            [str(y) for y in range(ano_atual, ano_atual - 6, -1)]
        )
        ctrl.addWidget(self.year_combo)

        self.btn_preview = QPushButton()
        self.btn_preview.clicked.connect(self.preview_informe)
        ctrl.addWidget(self.btn_preview)

        self.btn_pdf = QPushButton()
        self.btn_pdf.clicked.connect(self.gerar_e_exportar_pdf)
        ctrl.addWidget(self.btn_pdf)

        self.btn_print = QPushButton()
        self.btn_print.clicked.connect(self.imprimir_informe)
        ctrl.addWidget(self.btn_print)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.pdf_view = QTextEdit()
        self.pdf_view.setReadOnly(True)
        layout.addWidget(self.pdf_view, 1)

        return w

    def preview_informe(self):
        ano = int(self.year_combo.currentText())
        texto = self.controller.gerar_texto_informe(ano)
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
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Gere o informe antes")
            )
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            TranslatorApp.get("Salvar PDF"),
            "informe.pdf",
            "PDF Files (*.pdf)"
        )

        if caminho:
            MakePDF.gerar_pdf(
                caminho,
                TranslatorApp.get("Informe de Rendimentos"),
                texto
            )

    def imprimir_informe(self):
        printer = QPrinter()
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            self.pdf_view.print_(printer)

    def export_table_csv(self, tabela, prefix):
        if tabela.rowCount() == 0:
            QMessageBox.information(
                self,
                TranslatorApp.get("Exportar CSV"),
                TranslatorApp.get("Tabela vazia")
            )
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            TranslatorApp.get("Salvar CSV"),
            f"{prefix}.csv",
            "CSV Files (*.csv)"
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
