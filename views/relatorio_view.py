import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget,
    QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QFrame, QTextEdit, QMessageBox,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from controllers.relatorio_controller import RelatorioController
from utilitarios.makepdf import MakePDF
from utilitarios.currency_formatter import CurrencyFormatter
from core.translator_app import TranslatorApp
from core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class RelatorioView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = RelatorioController()
        self.figure = None
        self.canvas = None

        self.setWindowTitle("Relatórios")

        self._init_ui()
        TranslatorApp.enable_auto_translation(self)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        main_layout = QHBoxLayout(self)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)

        self.titulo = QLabel("Relatórios")
        self.titulo.setObjectName("pageTitle")
        self.titulo.setAlignment(Qt.AlignCenter)

        self.sections = QListWidget()

        sidebar_layout.addWidget(self.titulo)
        sidebar_layout.addWidget(self.sections)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar, 1)

        self.stacked = QStackedWidget()

        self.w_diario = self._build_diario()
        self.w_anual = self._build_anual()
        self.w_informe = self._build_informe()

        self.stacked.addWidget(self.w_diario)
        self.stacked.addWidget(self.w_anual)
        self.stacked.addWidget(self.w_informe)

        main_layout.addWidget(self.stacked, 4)

        self.sections.addItems([
            "Relatório Diário",
            "Relatório Anual",
            "Informe de Rendimentos"
        ])

        self.sections.currentRowChanged.connect(self.stacked.setCurrentIndex)
        self.sections.setCurrentRow(0)

    # ==================================================
    # 💳 CARDS
    # ==================================================
    def _create_cards(self):

        layout = QHBoxLayout()

        def create_card(title):
            card = QFrame()
            card.setObjectName("card")

            v = QVBoxLayout(card)

            lbl_title = QLabel(title)
            lbl_value = QLabel("R$ 0,00")

            lbl_title.setObjectName("cardTitle")
            lbl_value.setObjectName("cardValue")

            v.addWidget(lbl_title)
            v.addWidget(lbl_value)

            return card, lbl_value

        self.card_receita, self.lbl_receita = create_card("Receitas")
        self.card_despesa, self.lbl_despesa = create_card("Despesas")
        self.card_saldo, self.lbl_saldo = create_card("Saldo")

        layout.addWidget(self.card_receita)
        layout.addWidget(self.card_despesa)
        layout.addWidget(self.card_saldo)

        return layout

    # ==================================================
    # 📊 GRÁFICOS COMPLETOS
    # ==================================================
    def _create_chart(self):
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure

            self.figure = Figure(figsize=(8, 4))
            self.canvas = FigureCanvas(self.figure)
            return self.canvas

        except Exception:
            self.figure = None
            self.canvas = QLabel(
                "Gráficos indisponíveis neste ambiente. "
                "Os relatórios continuam funcionando sem visualização gráfica."
            )
            self.canvas.setWordWrap(True)
            self.canvas.setObjectName("infoLabel")
            return self.canvas

    def _update_chart(self, dados):
        if not self.figure or not hasattr(self.canvas, "draw"):
            return

        self.figure.clear()

        receitas = [float(d.get("Receita", 0)) for d in dados]
        despesas = [float(d.get("Despesa", 0)) for d in dados]

        colors = ThemeManager.get_chart_colors()

        # 📊 RESUMO
        ax1 = self.figure.add_subplot(131)
        ax1.bar(
            ["Receitas", "Despesas"],
            [sum(receitas), sum(despesas)],
            color=[colors["receita"], colors["despesa"]]
        )
        ax1.set_title("Resumo", color=colors["text"])
        ax1.grid(color=colors["grid"], linestyle="--", alpha=0.3)

        # 📈 EVOLUÇÃO
        ax2 = self.figure.add_subplot(132)
        saldo = []
        total = 0
        for r, d in zip(receitas, despesas):
            total += r - d
            saldo.append(total)

        ax2.plot(saldo, color=colors["saldo"])
        ax2.set_title("Evolução", color=colors["text"])
        ax2.grid(color=colors["grid"], linestyle="--", alpha=0.3)

        # 🍩 PIZZA
        ax3 = self.figure.add_subplot(133)
        ax3.pie(
            [sum(receitas), sum(despesas)],
            labels=["Receitas", "Despesas"],
            autopct="%1.1f%%"
        )
        ax3.set_title("Distribuição")

        self.figure.tight_layout()
        self.canvas.draw()

    # ==================================================
    # 🧠 INSIGHTS
    # ==================================================
    def _create_insights(self):
        self.lbl_insights = QLabel()
        self.lbl_insights.setObjectName("infoLabel")
        return self.lbl_insights

    def _update_insights(self, receitas, despesas):

        if despesas > receitas:
            texto = "⚠️ Gastos maiores que receitas"
        elif receitas > despesas * 2:
            texto = "🔥 Excelente controle financeiro"
        else:
            texto = "✔️ Situação equilibrada"

        self.lbl_insights.setText(texto)

    # ==================================================
    # DIÁRIO
    # ==================================================
    def _build_diario(self):

        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addLayout(self._create_cards())
        layout.addWidget(self._create_chart())
        layout.addWidget(self._create_insights())

        ctrl = QHBoxLayout()

        self.input_days = QComboBox()
        self.input_days.addItems(["7", "15", "30", "90"])

        btn = QPushButton("Gerar")
        btn.clicked.connect(self.load_diario)

        ctrl.addWidget(QLabel("Dias:"))
        ctrl.addWidget(self.input_days)
        ctrl.addWidget(btn)
        ctrl.addStretch()

        layout.addLayout(ctrl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Data", "Categoria", "Receita", "Despesa", "Economia"
        ])

        layout.addWidget(self.table)

        self.load_diario()
        return w

    def load_diario(self):
        try:
            dias = int(self.input_days.currentText())
            data = self.controller.relatorio_diario(dias)

            if not data:
                self._empty(self.table)
                return

            receitas = sum(float(r.get("Receita", 0)) for r in data)
            despesas = sum(float(r.get("Despesa", 0)) for r in data)
            saldo = receitas - despesas

            self.lbl_receita.setText(CurrencyFormatter.format(receitas))
            self.lbl_despesa.setText(CurrencyFormatter.format(despesas))
            self.lbl_saldo.setText(CurrencyFormatter.format(saldo))

            self._update_chart(data)
            self._update_insights(receitas, despesas)

            self._fill_table(self.table, data)

        except Exception:
            logger.exception("Erro relatório diário")

    # ==================================================
    # ANUAL
    # ==================================================
    def _build_anual(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.table_anual = QTableWidget()
        layout.addWidget(self.table_anual)

        return w

    # ==================================================
    # INFORME
    # ==================================================
    def _build_informe(self):

        w = QWidget()
        layout = QVBoxLayout(w)

        ctrl = QHBoxLayout()

        self.combo_inf = QComboBox()
        ano = datetime.now().year
        self.combo_inf.addItems([str(a) for a in range(ano, ano - 6, -1)])

        btn_preview = QPushButton("Visualizar")
        btn_pdf = QPushButton("PDF")
        btn_print = QPushButton("Imprimir")

        btn_preview.clicked.connect(self.preview)
        btn_pdf.clicked.connect(self.export_pdf)
        btn_print.clicked.connect(self.print_pdf)

        ctrl.addWidget(QLabel("Ano Base:"))
        ctrl.addWidget(self.combo_inf)
        ctrl.addWidget(btn_preview)
        ctrl.addWidget(btn_pdf)
        ctrl.addWidget(btn_print)

        layout.addLayout(ctrl)

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(self.text)

        return w

    def preview(self):
        ano = int(self.combo_inf.currentText())
        txt = self.controller.gerar_texto_informe(ano)
        self.text.setPlainText(txt or "Sem dados")

    def export_pdf(self):
        txt = self.text.toPlainText()
        if not txt:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Salvar", "informe.pdf")

        if path:
            MakePDF.gerar_pdf(path, "Informe de Rendimentos", txt)

    def print_pdf(self):
        printer = QPrinter()
        dlg = QPrintDialog(printer, self)

        if dlg.exec_():
            self.text.print_(printer)

    # ==================================================
    # UTIL
    # ==================================================
    def _fill_table(self, table, data):

        table.setRowCount(0)

        for i, row in enumerate(data):
            table.insertRow(i)

            for j, val in enumerate(row.values()):
                if isinstance(val, (int, float)):
                    val = CurrencyFormatter.format(val)

                table.setItem(i, j, QTableWidgetItem(str(val)))

    def _empty(self, table):
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setItem(0, 0, QTableWidgetItem("📭 Nenhum dado"))
