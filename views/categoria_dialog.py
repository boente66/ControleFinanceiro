import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox, QLabel
)

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class CategoriaDialog(QDialog):

    def __init__(self, parent=None, nome=None, tipo=None):
        super().__init__(parent)

        self.setMinimumWidth(300)

        # 🔥 título reativo
        TranslatorApp.window_title(self, "Categoria")

        layout = QVBoxLayout(self)

        # ---------------- FORM ----------------
        form_layout = QFormLayout()

        # Nome
        self.lbl_nome = QLabel()
        TranslatorApp.text(self.lbl_nome, "Nome")

        self.nome_input = QLineEdit()
        if nome:
            self.nome_input.setText(nome)

        form_layout.addRow(self.lbl_nome, self.nome_input)

        # Tipo
        self.lbl_tipo = QLabel()
        TranslatorApp.text(self.lbl_tipo, "Tipo")

        self.tipo_combo = QComboBox()
        TranslatorApp.combo(self.tipo_combo, ["Despesa", "Receita"])

        if tipo:
            self.tipo_combo.setCurrentText(tipo)

        form_layout.addRow(self.lbl_tipo, self.tipo_combo)

        layout.addLayout(form_layout)

        # ---------------- BOTÕES ----------------
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        layout.addWidget(self.button_box)

        # 🔥 BOTÕES REATIVOS
        TranslatorApp.text(
            self.button_box.button(QDialogButtonBox.Ok),
            "OK"
        )
        TranslatorApp.text(
            self.button_box.button(QDialogButtonBox.Cancel),
            "Cancelar"
        )

        self.button_box.accepted.connect(self._validar)
        self.button_box.rejected.connect(self.reject)

    # ==================================================
    # VALIDAÇÃO
    # ==================================================
    def _validar(self):

        if not self.nome_input.text().strip():
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("O nome da categoria não pode estar vazio.")
            )
            return

        self.accept()

    # ==================================================
    # RETORNO DOS DADOS
    # ==================================================
    def get_data(self):

        return {
            "Nome": self.nome_input.text().strip(),
            "Tipo": self.tipo_combo.currentData()
        }