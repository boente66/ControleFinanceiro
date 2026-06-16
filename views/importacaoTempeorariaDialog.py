# -*- coding: utf-8 -*-
import logging

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
    QCheckBox,
    QHeaderView,
)
from PyQt5.QtCore import Qt

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter

from views.editar_transacao_dialog import EditTransactionDialog
from controllers.category_controller import CategoryController

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class ImportacaoTemporariaDialog(QDialog):
    """
    Tela de revisão dos lançamentos reconhecidos.

    Responsabilidade:
    - Exibir lançamentos temporários reconhecidos pela importação.
    - Permitir revisar/editar antes de salvar.
    - Retornar apenas os lançamentos selecionados.
    - NÃO grava diretamente no banco.
    """

    COL_IMPORTAR = 0
    COL_DATA = 1
    COL_DESCRICAO = 2
    COL_CATEGORIA = 3
    COL_CONFIANCA = 4
    COL_VALOR = 5
    COL_TIPO = 6

    def __init__(self, lancamentos, parent=None):
        super().__init__(parent)

        self.lancamentos = lancamentos or []
        self.category_controller = CategoryController()
        self._categoria_cache = {}

        self.setWindowTitle("Revisar Lançamentos Importados")
        self.resize(1000, 500)

        self._init_ui()
        self._connect_events()

        TranslatorApp.bind(self._atualizar_textos, self)
        self._atualizar_textos()

        self._popular_tabela()

    # ======================================================
    # UI
    # ======================================================
    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 7)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        btns = QHBoxLayout()

        self.btn_editar = QPushButton()
        self.btn_confirmar = QPushButton()
        self.btn_cancelar = QPushButton()

        self.btn_confirmar.setObjectName("addButton")

        btns.addWidget(self.btn_editar)
        btns.addStretch()
        btns.addWidget(self.btn_confirmar)
        btns.addWidget(self.btn_cancelar)

        layout.addLayout(btns)

    # ======================================================
    # EVENTOS
    # ======================================================
    def _connect_events(self):
        self.btn_editar.clicked.connect(self.editar_selecionado)
        self.btn_confirmar.clicked.connect(self.confirmar)
        self.btn_cancelar.clicked.connect(self.reject)

    # ======================================================
    # TRADUÇÃO
    # ======================================================
    def _atualizar_textos(self, *_):
        self.setWindowTitle(
            TranslatorApp.get("Revisar Lançamentos Importados")
        )

        self.btn_editar.setText(
            TranslatorApp.get("Editar selecionado")
        )

        self.btn_confirmar.setText(
            TranslatorApp.get("Confirmar importação")
        )

        self.btn_cancelar.setText(
            TranslatorApp.get("Cancelar")
        )

        self.table.setHorizontalHeaderLabels([
            TranslatorApp.get("Importar"),
            TranslatorApp.get("Data"),
            TranslatorApp.get("Descrição"),
            TranslatorApp.get("Categoria"),
            TranslatorApp.get("Confiança"),
            TranslatorApp.get("Valor"),
            TranslatorApp.get("Tipo"),
        ])

    # ======================================================
    # POPULAR TABELA
    # ======================================================
    def _popular_tabela(self):
        self.table.setRowCount(0)

        for row, lanc in enumerate(self.lancamentos):
            self.table.insertRow(row)

            chk = QCheckBox()
            chk.setChecked(True)
            chk.setStyleSheet("margin-left: 20px;")

            self.table.setCellWidget(
                row,
                self.COL_IMPORTAR,
                chk
            )

            self._set_item(
                row,
                self.COL_DATA,
                self._formatar_data(lanc.get("Data", ""))
            )

            self._set_item(
                row,
                self.COL_DESCRICAO,
                str(lanc.get("Descricao", ""))
            )

            self._set_item(
                row,
                self.COL_CATEGORIA,
                self._get_nome_categoria(
                    lanc.get("ID_Categoria")
                )
            )

            confianca = float(
                lanc.get("ConfiancaIA", 0) or 0
            )

            self._set_item(
                row,
                self.COL_CONFIANCA,
                f"{confianca * 100:.0f}%"
            )

            valor = float(
                lanc.get("Valor", 0) or 0
            )

            self._set_item(
                row,
                self.COL_VALOR,
                CurrencyFormatter.format(valor)
            )

            self._set_item(
                row,
                self.COL_TIPO,
                str(lanc.get("Tipo", ""))
            )

    def _set_item(self, row, column, value):
        item = QTableWidgetItem(str(value))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(row, column, item)

    # ======================================================
    # FORMATADORES
    # ======================================================
    def _formatar_data(self, data_iso):
        if not data_iso:
            return ""

        try:
            return DateFormatter.iso_to_br(data_iso)
        except Exception:
            return str(data_iso)

    # ======================================================
    # CACHE DE CATEGORIA
    # ======================================================
    def _get_nome_categoria(self, id_categoria):
        if not id_categoria:
            return ""

        if id_categoria in self._categoria_cache:
            return self._categoria_cache[id_categoria]

        try:
            nome = self.category_controller.get_nome_categoria_by_id(
                id_categoria
            ) or ""

        except Exception:
            logger.exception("Erro ao buscar nome da categoria")
            nome = ""

        self._categoria_cache[id_categoria] = nome
        return nome

    # ======================================================
    # EDITAR
    # ======================================================
    def editar_selecionado(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Selecione um lançamento.")
            )
            return

        if row >= len(self.lancamentos):
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
            self._atualizar_linha(row)

    def _atualizar_linha(self, row):
        if row < 0 or row >= len(self.lancamentos):
            return

        lanc = self.lancamentos[row]

        self._set_item(
            row,
            self.COL_DATA,
            self._formatar_data(lanc.get("Data", ""))
        )

        self._set_item(
            row,
            self.COL_DESCRICAO,
            lanc.get("Descricao", "")
        )

        self._set_item(
            row,
            self.COL_CATEGORIA,
            self._get_nome_categoria(
                lanc.get("ID_Categoria")
            )
        )

        self._set_item(
            row,
            self.COL_VALOR,
            CurrencyFormatter.format(
                float(lanc.get("Valor", 0) or 0)
            )
        )

        self._set_item(
            row,
            self.COL_TIPO,
            lanc.get("Tipo", "")
        )

    # ======================================================
    # CONFIRMAR
    # ======================================================
    def confirmar(self):
        selecionados = []

        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(
                row,
                self.COL_IMPORTAR
            )

            if chk and chk.isChecked():
                selecionados.append(
                    self.lancamentos[row]
                )

        if not selecionados:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Nenhum lançamento selecionado.")
            )
            return

        self.lancamentos = selecionados
        self.accept()

    # ======================================================
    # GET
    # ======================================================
    def get_lancamentos_confirmados(self):
        return self.lancamentos

    # ======================================================
    # CICLO DE VIDA
    # ======================================================
    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)