# -*- coding: utf-8 -*-
import logging
import os
import re

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QDateEdit, QSpinBox
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon

from core.translator_app import TranslatorApp

from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController
from controllers.main_controller import MainController
from controllers.fatura_controller import FaturaController
from controllers.ia_import_controller import IAImportController

from utilitarios.ion_path import IonPath

from views.FavorecidoDialog import FavorecidoDialog
from views.categoria_dialog import CategoriaDialog

logger = logging.getLogger(__name__)


class TransactionDialog(QDialog):

    def __init__(self, parent=None, contexto=None, id_contexto=None):
        super().__init__(parent)

        if not contexto or not id_contexto:
            raise ValueError("Contexto inválido")

        self.contexto = contexto
        self.id_contexto = id_contexto

        self.main_controller = MainController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self.import_controller = IAImportController()

        self._icon_cache = {}

        self.setWindowTitle("Adicionar nova Transação")
        self.setMinimumWidth(820)

        self._build_ui()
        self._carregar_favorecidos()
        self._carregar_categorias()

        TranslatorApp.enable_auto_translation(self)

        self.valor_edit.textChanged.connect(self._formatar_moeda)
        self.tipo_combo.currentIndexChanged.connect(self._update_label)

        self._update_label()
        self.descricao_edit.setFocus()

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # TIPO
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Despesa", "Despesa")
        self.tipo_combo.addItem("Receita", "Receita")
        layout.addWidget(self.tipo_combo)

        # DESCRIÇÃO + DATA
        l1 = QHBoxLayout()

        self.descricao_edit = QLineEdit()
        self.descricao_edit.setPlaceholderText("Descrição")

        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)

        l1.addWidget(self.descricao_edit, 3)
        l1.addWidget(self.data_edit, 1)
        layout.addLayout(l1)

        # FAVORECIDO + CATEGORIA
        l2 = QHBoxLayout()

        self.lbl_favorecido = QLabel("Pagar para")
        self.favorecido_combo = QComboBox()

        btn_fav = QPushButton("")
        btn_fav.setIcon(self._icon("add"))
        btn_fav.setFixedSize(28, 28)
        btn_fav.clicked.connect(self._novo_favorecido)

        fav_layout = QHBoxLayout()
        fav_layout.addWidget(self.favorecido_combo)
        fav_layout.addWidget(btn_fav)

        bloco1 = QVBoxLayout()
        bloco1.addWidget(self.lbl_favorecido)
        bloco1.addLayout(fav_layout)

        self.lbl_categoria = QLabel("Categoria")
        self.categoria_combo = QComboBox()

        btn_cat = QPushButton("")
        btn_cat.setIcon(self._icon("add"))
        btn_cat.setFixedSize(28, 28)
        btn_cat.clicked.connect(self._nova_categoria)

        cat_layout = QHBoxLayout()
        cat_layout.addWidget(self.categoria_combo)
        cat_layout.addWidget(btn_cat)

        bloco2 = QVBoxLayout()
        bloco2.addWidget(self.lbl_categoria)
        bloco2.addLayout(cat_layout)

        l2.addLayout(bloco1)
        l2.addLayout(bloco2)

        layout.addLayout(l2)

        # VALOR
        self.valor_edit = QLineEdit()
        self.valor_edit.setPlaceholderText("0,00")
        layout.addWidget(self.valor_edit)

        # CARTÃO
        if self.contexto == "cartao":
            self.tipo_combo.setCurrentIndex(0)
            self.tipo_combo.setEnabled(False)

            self.parcelas_spin = QSpinBox()
            self.parcelas_spin.setRange(1, 36)
            layout.addWidget(self.parcelas_spin)

        # BOTÕES
        btns = QHBoxLayout()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self.salvar)

        btns.addStretch()
        btns.addWidget(cancelar)
        btns.addWidget(salvar)

        layout.addLayout(btns)

    # ======================================================
    # LABEL DINÂMICO
    # ======================================================
    def _update_label(self):
        if self.contexto == "cartao":
            self.lbl_favorecido.setText("Favorecido")
            return

        tipo = self.tipo_combo.currentData()

        if tipo == "Receita":
            self.lbl_favorecido.setText("Receber de")
        else:
            self.lbl_favorecido.setText("Pagar para")

    # ======================================================
    # FORMATAÇÃO
    # ======================================================
    def _formatar_moeda(self):
        texto = re.sub(r"[^\d]", "", self.valor_edit.text())

        if not texto:
            return

        valor = int(texto) / 100

        self.valor_edit.blockSignals(True)
        self.valor_edit.setText(
            f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        self.valor_edit.blockSignals(False)

    # ======================================================
    # ICON
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
            logger.exception("Erro ao carregar ícone")
            return QIcon()

    # ======================================================
    # LOAD
    # ======================================================
    def _carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Nenhum", None)

        dados = self.category_controller.get_all_categories() or []

        for c in dados:
            nome = c.get("Nome") or c.get("nome")
            cid = c.get("ID_Categoria") or c.get("id_categoria")

            if nome:
                self.categoria_combo.addItem(nome, cid)

    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        self.favorecido_combo.addItem("Nenhum", None)

        dados = self.favorecido_controller.listar_favorecidos() or []

        for f in dados:
            nome = f.get("Nome") or f.get("nome")
            fid = f.get("ID_Favorecido") or f.get("id_favorecido")

            if nome:
                self.favorecido_combo.addItem(nome, fid)

    # ======================================================
    # AÇÕES
    # ======================================================
    def _novo_favorecido(self):
        dialog = FavorecidoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._carregar_favorecidos()

    def _nova_categoria(self):
        dialog = CategoriaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._carregar_categorias()

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):
        try:
            descricao = self.descricao_edit.text().strip()
            if not descricao:
                raise ValueError("Descrição obrigatória")

            texto_valor = self.valor_edit.text().strip()
            if not texto_valor:
                raise ValueError("Valor inválido")

            valor = float(texto_valor.replace(".", "").replace(",", "."))
            tipo = self.tipo_combo.currentData()

            # REGRA DE SINAL
            if self.contexto == "conta":
                valor = abs(valor) if tipo == "Receita" else -abs(valor)
            else:
                valor = abs(valor)

            dados = {
                "Descricao": descricao,
                "Valor": valor,
                "Data": self.data_edit.date().toString("yyyy-MM-dd"),
                "ID_Categoria": self.categoria_combo.currentData(),
                "ID_Favorecido": self.favorecido_combo.currentData(),
            }

            if self.contexto == "conta":
                dados["ID_Conta"] = self.id_contexto
                dados["Tipo"] = tipo
                self.main_controller.inserir_lancamento(dados)

            else:
                dados["ID_Cartao"] = self.id_contexto
                dados["Parcelas"] = int(self.parcelas_spin.value())
                self.fatura_controller.registrar_despesa_cartao(dados)

            self.accept()

        except Exception as e:
            logger.exception("Erro ao salvar transação")
            QMessageBox.warning(self, "Erro", str(e))
