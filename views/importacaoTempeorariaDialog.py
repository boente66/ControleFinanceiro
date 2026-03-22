from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout,
    QAbstractItemView, QCheckBox, QHeaderView
)
from PyQt5.QtCore import Qt

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter
from views.editar_transacao_dialog import EditTransactionDialog
from controllers.category_controller import CategoryController


class ImportacaoTemporariaDialog(QDialog):
    """
    Tela de revisão dos lançamentos reconhecidos.
    NÃO grava no banco.
    Apenas retorna os selecionados.
    """

    def __init__(self, lancamentos, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Revisar Lançamentos Importados")
        self.resize(1000, 500)

        self.lancamentos = lancamentos or []
        self.category_controller = CategoryController()

        # 🔥 Cache simples para evitar várias consultas repetidas
        self._categoria_cache = {}

        layout = QVBoxLayout(self)

        # ======================================================
        # TABELA
        # ======================================================
        self.table = QTableWidget(len(self.lancamentos), 7)
        self.table.setHorizontalHeaderLabels([
            "Importar",
            "Data",
            "Descrição",
            "Categoria",
            "Confiança",
            "Valor",
            "Tipo"
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._popular_tabela()

        layout.addWidget(self.table)

        # ======================================================
        # BOTÕES
        # ======================================================
        btns = QHBoxLayout()

        btn_editar = QPushButton("Editar selecionado")
        btn_editar.clicked.connect(self.editar_selecionado)

        btn_confirmar = QPushButton("Confirmar importação")
        btn_confirmar.clicked.connect(self.confirmar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btns.addWidget(btn_editar)
        btns.addStretch()
        btns.addWidget(btn_confirmar)
        btns.addWidget(btn_cancelar)

        layout.addLayout(btns)

    # ======================================================
    # POPULAR TABELA
    # ======================================================
    def _popular_tabela(self):

        for row, lanc in enumerate(self.lancamentos):

            # Checkbox
            chk = QCheckBox()
            chk.setChecked(True)
            self.table.setCellWidget(row, 0, chk)

            # Data
            data_iso = lanc.get("Data", "")
            data_formatada = DateFormatter.iso_to_br(data_iso) if data_iso else ""
            self.table.setItem(row, 1, QTableWidgetItem(data_formatada))

            # Descrição
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(str(lanc.get("Descricao", "")))
            )

            # Categoria
            id_categoria = lanc.get("ID_Categoria")
            nome_categoria = self._get_nome_categoria(id_categoria)
            self.table.setItem(row, 3, QTableWidgetItem(nome_categoria))

            # Confiança
            confianca = float(lanc.get("ConfiancaIA", 0))
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(f"{confianca * 100:.0f}%")
            )

            # Valor
            valor = float(lanc.get("Valor", 0))
            self.table.setItem(
                row,
                5,
                QTableWidgetItem(CurrencyFormatter.format(valor))
            )

            # Tipo
            self.table.setItem(
                row,
                6,
                QTableWidgetItem(str(lanc.get("Tipo", "")))
            )

    # ======================================================
    # CACHE DE CATEGORIA
    # ======================================================
    def _get_nome_categoria(self, id_categoria):

        if not id_categoria:
            return ""

        if id_categoria in self._categoria_cache:
            return self._categoria_cache[id_categoria]

        nome = self.category_controller.get_nome_categoria_by_id(id_categoria)
        self._categoria_cache[id_categoria] = nome

        return nome

    # ======================================================
    # EDITAR
    # ======================================================
    def editar_selecionado(self):

        row = self.table.currentRow()
        if row < 0:
            return

        lanc = self.lancamentos[row]

        dialog = EditTransactionDialog(
            transacao=lanc,
            parent=self,
            modo_temporario=True
        )

        if dialog.exec_() == QDialog.Accepted:

            dados = getattr(dialog, "dados_editados", None)
            if not dados:
                return

            self.lancamentos[row].update(dados)

            # Atualiza visual

            # Data
            data_iso = dados.get("Data", "")
            data_formatada = DateFormatter.iso_to_br(data_iso) if data_iso else ""
            self.table.item(row, 1).setText(data_formatada)

            # Descrição
            self.table.item(row, 2).setText(
                dados.get("Descricao", "")
            )

            # Categoria
            id_categoria = dados.get("ID_Categoria")
            nome_categoria = self._get_nome_categoria(id_categoria)
            self.table.item(row, 3).setText(nome_categoria)

            # Valor
            self.table.item(row, 5).setText(
                CurrencyFormatter.format(dados.get("Valor", 0))
            )

            # Tipo
            self.table.item(row, 6).setText(
                dados.get("Tipo", "")
            )

    # ======================================================
    # CONFIRMAR
    # ======================================================
    def confirmar(self):

        selecionados = []

        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                selecionados.append(self.lancamentos[row])

        if not selecionados:
            QMessageBox.warning(
                self,
                "Aviso",
                "Nenhum lançamento selecionado."
            )
            return

        self.lancamentos = selecionados
        self.accept()

    # ======================================================
    # GET
    # ======================================================
    def get_lancamentos_confirmados(self):
        return self.lancamentos