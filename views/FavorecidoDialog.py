# -*- coding: utf-8 -*-
import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox
)

from core.translator_app import TranslatorApp
from utilitarios.name_format import NameFormat
from form.favorecido_form import FavorecidoForm

logger = logging.getLogger(__name__)


class FavorecidoDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Novo Favorecido")
        self.setMinimumWidth(400)

        self._build_ui()
        self._trocar_tipo()

        TranslatorApp.enable_auto_translation(self)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Pessoa Física", "PF")
        self.tipo_combo.addItem("Pessoa Jurídica", "PJ")
        self.tipo_combo.currentIndexChanged.connect(self._trocar_tipo)

        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.tipo_combo)

        self.nome_label = QLabel("Nome")
        self.nome_edit = QLineEdit()

        layout.addWidget(self.nome_label)
        layout.addWidget(self.nome_edit)

        self.doc_label = QLabel("CPF")
        self.doc_edit = QLineEdit()

        layout.addWidget(self.doc_label)
        layout.addWidget(self.doc_edit)

        self.tel_label = QLabel("Telefone")
        self.tel_edit = QLineEdit()

        layout.addWidget(self.tel_label)
        layout.addWidget(self.tel_edit)

        btns = QHBoxLayout()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self.salvar)

        btns.addStretch()
        btns.addWidget(cancelar)
        btns.addWidget(salvar)

        layout.addLayout(btns)

        self.doc_edit.editingFinished.connect(self._formatar_documento)
        self.tel_edit.editingFinished.connect(self._formatar_telefone)

    def _trocar_tipo(self):
        tipo = self.tipo_combo.currentData()
        self.doc_edit.clear()

        if tipo == "PF":
            self.nome_label.setText("Nome")
            self.doc_label.setText("CPF")
        else:
            self.nome_label.setText("Razão Social")
            self.doc_label.setText("CNPJ")

    def _formatar_documento(self):
        texto = self.doc_edit.text()
        tipo = self.tipo_combo.currentData()

        if tipo == "PF":
            self.doc_edit.setText(NameFormat.formatCPF(texto))
        else:
            self.doc_edit.setText(NameFormat.formatCNPJ(texto))

    def _formatar_telefone(self):
        texto = self.tel_edit.text()
        self.tel_edit.setText(NameFormat.formatTelefone(texto))

    def get_dados(self):
        form = FavorecidoForm(
            tipo=self.tipo_combo.currentData(),
            nome=self.nome_edit.text(),
            documento=self.doc_edit.text(),
            telefone=self.tel_edit.text()
        )

        form.validar()
        return form.to_dict()

    def salvar(self):
        try:
            self.dados = self.get_dados()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))