# -*- coding: utf-8 -*-
import logging
import os
import re

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from PyQt5 import uic

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

        if contexto is None or id_contexto is None:
            raise ValueError("Contexto inválido")

        self.contexto = contexto
        self.id_contexto = id_contexto

        # controllers
        self.main_controller = MainController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self.import_controller = IAImportController()

        self._icon_cache = {}

        # ======================================================
        # 🔥 LOAD UI SEGURO
        # ======================================================
        try:
            if self.contexto == "cartao":
                path = IonPath.load_ui("views", "ui", "fatura_dialog.ui")
            elif self.contexto == "conta":
                path = IonPath.load_ui("views", "ui", "TransactionDialog.ui")

            if not os.path.exists(path):
                raise FileNotFoundError(f"UI não encontrado: {path}")

            uic.loadUi(path, self)

        except Exception as e:
            logger.exception("Erro ao carregar UI")
            QMessageBox.critical(self, "Erro", f"Falha ao carregar interface:\n{e}")
            raise

        # ======================================================
        # 🔥 VALIDAÇÃO CRÍTICA
        # ======================================================
        if not hasattr(self, "descricao_edit"):
            raise RuntimeError("UI carregou mas widgets não foram encontrados")

        self.setMinimumWidth(820)

        # setup
        self._configurar_ui()
        self._carregar_favorecidos()
        self._carregar_categorias()

        TranslatorApp.enable_auto_translation(self)

        self._conectar_eventos()

        self.descricao_edit.setFocus()

    # ======================================================
    # CONFIG UI
    # ======================================================
    def _configurar_ui(self):

        if hasattr(self, "tipo_combo"):
            self.tipo_combo.clear()
            self.tipo_combo.addItem("Despesa", "Despesa")
            self.tipo_combo.addItem("Receita", "Receita")

        if hasattr(self, "data_edit"):
            self.data_edit.setDate(QDate.currentDate())

        if self.contexto == "cartao" and hasattr(self, "parcelas_spin"):
            self.parcelas_spin.setRange(1, 36)

    # ======================================================
    # EVENTOS
    # ======================================================
    def _conectar_eventos(self):

        if hasattr(self, "btn_salvar"):
            self.btn_salvar.clicked.connect(self.salvar)

        if hasattr(self, "btn_cancelar"):
            self.btn_cancelar.clicked.connect(self.reject)

        if hasattr(self, "valor_edit"):
            self.valor_edit.textChanged.connect(self._formatar_moeda)

        if hasattr(self, "tipo_combo"):
            self.tipo_combo.currentIndexChanged.connect(self._update_label)

        if hasattr(self, "btn_add_fav"):
            self.btn_add_fav.setIcon(self._icon("add"))
            self.btn_add_fav.clicked.connect(self._novo_favorecido)

        if hasattr(self, "btn_add_cat"):
            self.btn_add_cat.setIcon(self._icon("add"))
            self.btn_add_cat.clicked.connect(self._nova_categoria)

    # ======================================================
    # LABEL DINÂMICO
    # ======================================================
    def _update_label(self):

        if not hasattr(self, "lbl_favorecido"):
            return

        if self.contexto == "cartao":
            self.lbl_favorecido.setText("Estabelecimento")
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

        if not hasattr(self, "categoria_combo"):
            return

        self.categoria_combo.clear()
        self.categoria_combo.addItem("Nenhum", None)

        dados = self.category_controller.get_all_categories() or []

        for c in dados:
            nome = c.get("Nome") or c.get("nome")
            cid = c.get("ID_Categoria") or c.get("id_categoria")

            if nome:
                self.categoria_combo.addItem(nome, cid)

    def _carregar_favorecidos(self):

        if not hasattr(self, "favorecido_combo"):
            return

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
            tipo = self.tipo_combo.currentData() if hasattr(self, "tipo_combo") else "Despesa"

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