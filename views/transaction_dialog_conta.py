# transaction_dialog_conta.py
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import QDate
import re

from utilitarios.ion_path import IonPath
from controllers.main_controller import MainController
from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController


class TransactionDialogConta(QDialog):

    def __init__(self, parent=None, id_conta=None):
        super().__init__(parent)

        if id_conta is None:
            raise ValueError("Conta inválida")

        self.id_conta = id_conta

        uic.loadUi(IonPath.resource("views", "ui", "transaction_dialog.ui"), self)

        self.main_controller = MainController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()

        self._configurar_ui()
        self._carregar_dados()
        self._conectar_eventos()

    def _configurar_ui(self):
        self.tipo_combo.addItem("Despesa", "Despesa")
        self.tipo_combo.addItem("Receita", "Receita")
        self.data_edit.setDate(QDate.currentDate())

    def _carregar_dados(self):
        self.categoria_combo.addItem("Nenhum", None)
        for c in self.category_controller.get_all_categories() or []:
            self.categoria_combo.addItem(c["Nome"], c["ID_Categoria"])

        self.favorecido_combo.addItem("Nenhum", None)
        for f in self.favorecido_controller.listar_favorecidos() or []:
            self.favorecido_combo.addItem(f["Nome"], f["ID_Favorecido"])

    def _conectar_eventos(self):
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.reject)
        self.valor_edit.textChanged.connect(self._formatar_moeda)

    def _formatar_moeda(self):
        texto = re.sub(r"[^\d]", "", self.valor_edit.text())
        if not texto:
            return
        valor = int(texto) / 100
        self.valor_edit.blockSignals(True)
        self.valor_edit.setText(f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.valor_edit.blockSignals(False)

    def salvar(self):
        try:
            valor = float(self.valor_edit.text().replace(".", "").replace(",", "."))
            tipo = self.tipo_combo.currentData()

            if tipo == "Despesa":
                valor = -abs(valor)

            dados = {
                "Descricao": self.descricao_edit.text(),
                "Valor": valor,
                "Data": self.data_edit.date().toString("yyyy-MM-dd"),
                "ID_Conta": self.id_conta,
                "Tipo": tipo,
                "ID_Categoria": self.categoria_combo.currentData(),
                "ID_Favorecido": self.favorecido_combo.currentData(),
            }

            self.main_controller.inserir_lancamento(dados)
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))
