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

        # 🔥 título base (auto traduzido)
        self.setWindowTitle("Categoria")

        layout = QVBoxLayout(self)

        # ---------------- FORM ----------------
        form_layout = QFormLayout()

        # Nome
        self.lbl_nome = QLabel("Nome")

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite o nome da categoria")

        if nome:
            self.nome_input.setText(nome)

        form_layout.addRow(self.lbl_nome, self.nome_input)

        # Tipo
        self.lbl_tipo = QLabel("Tipo")

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Despesa", "Despesa")
        self.tipo_combo.addItem("Receita", "Receita")

        if tipo:
            index = self.tipo_combo.findData(tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)

        form_layout.addRow(self.lbl_tipo, self.tipo_combo)

        layout.addLayout(form_layout)

        # ---------------- BOTÕES ----------------
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        # texto base (auto traduzido depois)
        self.button_box.button(QDialogButtonBox.Ok).setText("OK")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")

        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self._validar)
        self.button_box.rejected.connect(self.reject)

        # 🔥 TRADUÇÃO GLOBAL AUTOMÁTICA
        TranslatorApp.bind(self._atualizar_textos, self)
        self._atualizar_textos()
    
    def _atualizar_textos(self):
        self.setWindowTitle(TranslatorApp.get("Categoria"))
        self.lbl_nome.setText(TranslatorApp.get("Nome"))
        self.lbl_tipo.setText(TranslatorApp.get("Tipo"))
        self.nome_input.setPlaceholderText(
            TranslatorApp.get("Digite o nome da categoria")
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(
            TranslatorApp.get("OK")
        )
        self.button_box.button(QDialogButtonBox.Cancel).setText(
            TranslatorApp.get("Cancelar")
        )

    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)

    # ==================================================
    # VALIDAÇÃO
    # ==================================================
    def _validar(self):

        nome = self.nome_input.text().strip()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("O nome da categoria não pode estar vazio.")
            )
            return

        # 🔥 normalização (evita lixo no banco)
        self.nome_input.setText(nome)

        self.accept()

    # ==================================================
    # RETORNO DOS DADOS
    # ==================================================
    def get_data(self):

        return {
            "Nome": self.nome_input.text().strip(),
            "Tipo": self.tipo_combo.currentData()
        }