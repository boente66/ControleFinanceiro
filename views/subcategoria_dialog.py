from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
)

from core.translator_app import TranslatorApp


class SubcategoriaDialog(QDialog):

    def __init__(self, parent=None, controller=None, categoria_pai_id=None):
        super().__init__(parent)

        if controller is None:
            raise RuntimeError("Controller não informado.")

        self.controller = controller
        self.categoria_pai_id = categoria_pai_id

        self.setMinimumWidth(300)
        self.setWindowTitle("Nova Subcategoria")

        self._montar_ui()
        self._carregar_categorias_pai()
        self._selecionar_categoria_pai()

        # 🔥 precisa (labels + botões mudam idioma)
        TranslatorApp.bind(self._on_translate,self)

    # ==================================================
    # REATIVIDADE
    # ==================================================
    def _on_translate(self, *_):

        self.setWindowTitle(TranslatorApp.get("Nova Subcategoria"))

        self.form.labelForField(self.nome_input).setText(
            TranslatorApp.get("Nome") + ":"
        )

        self.form.labelForField(self.categoria_pai_combo).setText(
            TranslatorApp.get("Categoria Pai") + ":"
        )

        self.buttons.button(QDialogButtonBox.Ok).setText(TranslatorApp.get("OK"))

        self.buttons.button(QDialogButtonBox.Cancel).setText(
            TranslatorApp.get("Cancelar")
        )

    # ==================================================
    # UI
    # ==================================================
    def _montar_ui(self):

        layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # Nome
        self.nome_input = QLineEdit()
        self.form.addRow("", self.nome_input)

        # Categoria Pai
        self.categoria_pai_combo = QComboBox()
        self.form.addRow("", self.categoria_pai_combo)

        layout.addLayout(self.form)

        # Botões
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

    # ==================================================
    # CARREGAR CATEGORIAS PAI
    # ==================================================
    def _carregar_categorias_pai(self):

        try:
            categorias = self.controller.get_all_categories()

            self.categoria_pai_combo.clear()

            for cat in categorias:
                if cat["ID_Categoria_Pai"] is None:
                    self.categoria_pai_combo.addItem(cat["Nome"], cat["ID_Categoria"])

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                f"{TranslatorApp.get('Erro ao carregar categorias')}: {e}",
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
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("O nome da subcategoria não pode estar vazio."),
            )
            return None

        id_categoria_pai = self.categoria_pai_combo.currentData()

        if not id_categoria_pai:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("Selecione uma categoria pai."),
            )
            return None

        return {"Nome": nome, "ID_Categoria_Pai": id_categoria_pai}
    
    # ==================================================
    # CICLO DE VIDA 
    # ==================================================
    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)