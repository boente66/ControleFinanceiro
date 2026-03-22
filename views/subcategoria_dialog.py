from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)


class SubcategoriaDialog(QDialog):

    def __init__(self, parent=None, controller=None, categoria_pai_id=None):
        super().__init__(parent)

        self.setWindowTitle("Nova Subcategoria")
        self.setMinimumWidth(300)

        if controller is None:
            raise RuntimeError("Controller não informado.")

        self.controller = controller
        self.categoria_pai_id = categoria_pai_id

        self._montar_ui()
        self._carregar_categorias_pai()
        self._selecionar_categoria_pai()

    # ==================================================
    # UI
    # ==================================================
    def _montar_ui(self):

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Nome
        self.nome_input = QLineEdit()
        form.addRow("Nome:", self.nome_input)

        # Categoria Pai
        self.categoria_pai_combo = QComboBox()
        form.addRow("Categoria Pai:", self.categoria_pai_combo)

        layout.addLayout(form)

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    # ==================================================
    # CARREGAR CATEGORIAS PAI
    # ==================================================
    def _carregar_categorias_pai(self):
        """
        Carrega apenas categorias principais
        (ID_Categoria_Pai IS NULL)
        """

        try:
            categorias = self.controller.get_all_categories()

            self.categoria_pai_combo.clear()

            for cat in categorias:
                if cat["ID_Categoria_Pai"] is None:
                    # Guarda ID no userData (forma correta)
                    self.categoria_pai_combo.addItem(
                        cat["Nome"],
                        cat["ID_Categoria"]
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao carregar categorias: {e}"
            )

    # ==================================================
    # SELECIONAR CATEGORIA PAI
    # ==================================================
    def _selecionar_categoria_pai(self):

        if not self.categoria_pai_id:
            return

        for i in range(self.categoria_pai_combo.count()):
            if self.categoria_pai_combo.itemData(i) == self.categoria_pai_id:
                self.categoria_pai_combo.setCurrentIndex(i)
                break

    # ==================================================
    # RETORNO
    # ==================================================
    def get_data(self):

        nome = self.nome_input.text().strip()

        if not nome:
            QMessageBox.warning(
                self,
                "Atenção",
                "O nome da subcategoria não pode estar vazio."
            )
            return None

        id_categoria_pai = self.categoria_pai_combo.currentData()

        if not id_categoria_pai:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione uma categoria pai."
            )
            return None

        return {
            "Nome": nome,
            "ID_Categoria_Pai": id_categoria_pai
        }