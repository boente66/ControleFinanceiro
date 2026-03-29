import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class CategoriaDialog(QDialog):

    def __init__(self, parent=None, nome=None, tipo=None):
        super().__init__(parent)

        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        # ---------------- FORM ----------------
        form_layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setText(nome if nome else "")
        form_layout.addRow("", self.nome_input)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Despesa", "Receita"])

        if tipo:
            self.tipo_combo.setCurrentText(tipo)

        form_layout.addRow("", self.tipo_combo)

        layout.addLayout(form_layout)

        # ---------------- BOTÕES ----------------
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.button_box.accepted.connect(self._validar)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

        # 🔥 TRADUÇÃO INICIAL
        self._apply_translation()

        # 🔥 REATIVO (MUDA AO TROCAR IDIOMA)
        TranslatorApp.bind(lambda _: self._apply_translation())

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _apply_translation(self):

        self.setWindowTitle(TranslatorApp.get("Categoria"))

        # Labels do form
        layout = self.layout().itemAt(0).layout()

        layout.labelForField(self.nome_input).setText(
            TranslatorApp.get("Nome") + ":"
        )

        layout.labelForField(self.tipo_combo).setText(
            TranslatorApp.get("Tipo") + ":"
        )

        # Combo traduzido
        TranslatorApp.combo(
            self.tipo_combo,
            ["Despesa", "Receita"]
        )

        # Botões
        self.button_box.button(QDialogButtonBox.Ok).setText(
            TranslatorApp.get("OK")
        )
        self.button_box.button(QDialogButtonBox.Cancel).setText(
            TranslatorApp.get("Cancelar")
        )

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
            "Tipo": self.tipo_combo.currentText()
        }