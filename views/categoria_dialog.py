from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)


class CategoriaDialog(QDialog):

    def __init__(self, parent=None, nome=None, tipo=None):
        super().__init__(parent)

        self.setWindowTitle("Categoria")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        # ---------------- FORM ----------------
        form_layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setText(nome if nome else "")
        form_layout.addRow("Nome:", self.nome_input)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Despesa", "Receita"])

        if tipo:
            self.tipo_combo.setCurrentText(tipo)

        form_layout.addRow("Tipo:", self.tipo_combo)

        layout.addLayout(form_layout)

        # ---------------- BOTÕES ----------------
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        button_box.accepted.connect(self._validar)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    # ==================================================
    # VALIDAÇÃO
    # ==================================================
    def _validar(self):

        if not self.nome_input.text().strip():
            QMessageBox.warning(
                self,
                "Atenção",
                "O nome da categoria não pode estar vazio."
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