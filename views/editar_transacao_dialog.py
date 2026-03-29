from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit,
    QDialogButtonBox, QLineEdit,
    QMessageBox, QCheckBox, QLabel
)
from PyQt5.QtCore import QDate

from controllers.account_controller import AccountController
from controllers.category_controller import CategoryController
from controllers.favorecido_controller import FavorecidoController
from controllers.transaction_controller import TransactionController

from core.session import Session
from core.translator_app import TranslatorApp


class EditTransactionDialog(QDialog):

    def __init__(self, transacao, parent=None, modo_temporario=False):
        super().__init__(parent)

        self.modo_temporario = modo_temporario

        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado")

        self.transacao = transacao or {}

        self.transaction_controller = TransactionController()
        self.account_controller = AccountController()
        self.category_controller = CategoryController()
        self.favorecido_controller = FavorecidoController()

        self.setMinimumSize(520, 420)

        self._build_ui()
        self._preencher_campos()

        # 🔥 título dinâmico
        TranslatorApp.window_title(self, "Editar Transação")

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # Labels
        self.lbl_conta = QLabel()
        self.lbl_tipo = QLabel()
        self.lbl_desc = QLabel()
        self.lbl_valor = QLabel()
        self.lbl_categoria = QLabel()
        self.lbl_favorecido = QLabel()
        self.lbl_data = QLabel()
        self.lbl_notas = QLabel()
        self.lbl_destino = QLabel()

        TranslatorApp.text(self.lbl_conta, "Conta:")
        TranslatorApp.text(self.lbl_tipo, "Tipo:")
        TranslatorApp.text(self.lbl_desc, "Descrição:")
        TranslatorApp.text(self.lbl_valor, "Valor:")
        TranslatorApp.text(self.lbl_categoria, "Categoria:")
        TranslatorApp.text(self.lbl_favorecido, "Favorecido:")
        TranslatorApp.text(self.lbl_data, "Data:")
        TranslatorApp.text(self.lbl_notas, "Notas:")
        TranslatorApp.text(self.lbl_destino, "Conta destino:")

        # Conta origem
        self.conta_origem_combo = QComboBox()
        self.contas = self.account_controller.get_all_accounts() or []
        for conta in self.contas:
            self.conta_origem_combo.addItem(
                conta.get("Nome_Conta", ""),
                conta.get("ID_Conta")
            )
        self.form.addRow(self.lbl_conta, self.conta_origem_combo)

        # Tipo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Despesa", "Receita"])
        self.form.addRow(self.lbl_tipo, self.tipo_combo)

        # Descrição
        self.desc_edit = QLineEdit()
        TranslatorApp.placeholder(self.desc_edit, "Descrição")
        self.form.addRow(self.lbl_desc, self.desc_edit)

        # Valor
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setPrefix("R$ ")
        self.valor_spin.setRange(0.01, 1_000_000.00)
        self.valor_spin.setDecimals(2)
        self.form.addRow(self.lbl_valor, self.valor_spin)

        # Categoria
        self.categoria_combo = QComboBox()
        categorias = self.category_controller.get_all_categories() or []
        for cat in categorias:
            self.categoria_combo.addItem(
                cat.get("Nome", ""),
                cat.get("ID_Categoria")
            )
        self.form.addRow(self.lbl_categoria, self.categoria_combo)

        # Favorecido
        self.favorecido_combo = QComboBox()
        self._carregar_favorecidos()
        self.form.addRow(self.lbl_favorecido, self.favorecido_combo)

        # Data
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        self.form.addRow(self.lbl_data, self.data_edit)

        # Notas
        self.notas_edit = QTextEdit()
        self.notas_edit.setFixedHeight(80)
        self.form.addRow(self.lbl_notas, self.notas_edit)

        # Transferência
        self.transfer_checkbox = QCheckBox()
        TranslatorApp.text(self.transfer_checkbox, "Converter em transferência")
        self.transfer_checkbox.stateChanged.connect(self._toggle_transferencia)
        self.form.addRow(QLabel(""), self.transfer_checkbox)

        # Conta destino
        self.conta_destino_combo = QComboBox()
        for conta in self.contas:
            self.conta_destino_combo.addItem(
                conta.get("Nome_Conta", ""),
                conta.get("ID_Conta")
            )
        self.conta_destino_combo.setVisible(False)
        self.form.addRow(self.lbl_destino, self.conta_destino_combo)

        layout.addLayout(self.form)

        # Botões
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        layout.addWidget(self.button_box)

        # 🔥 tradução dos botões
        TranslatorApp._bind(lambda _: self.button_box.button(
            QDialogButtonBox.Save
        ).setText(TranslatorApp.get("Salvar")))

        TranslatorApp._bind(lambda _: self.button_box.button(
            QDialogButtonBox.Cancel
        ).setText(TranslatorApp.get("Cancelar")))

        self.button_box.accepted.connect(self.salvar)
        self.button_box.rejected.connect(self.reject)

    # ======================================================
    # DADOS
    # ======================================================
    def _preencher_campos(self):
        self.desc_edit.setText(self.transacao.get("Descricao", ""))

        valor = abs(float(self.transacao.get("Valor", 0)))
        self.valor_spin.setValue(valor)

        tipo = self.transacao.get("Tipo", "Despesa")
        self.tipo_combo.setCurrentText(tipo)

        idx_conta = self.conta_origem_combo.findData(
            self.transacao.get("ID_Conta")
        )
        if idx_conta >= 0:
            self.conta_origem_combo.setCurrentIndex(idx_conta)

        idx_cat = self.categoria_combo.findData(
            self.transacao.get("ID_Categoria")
        )
        if idx_cat >= 0:
            self.categoria_combo.setCurrentIndex(idx_cat)

        idx_fav = self.favorecido_combo.findData(
            self.transacao.get("ID_Favorecido")
        )
        if idx_fav >= 0:
            self.favorecido_combo.setCurrentIndex(idx_fav)

        data = self.transacao.get("Data")
        if data:
            self.data_edit.setDate(QDate.fromString(data, "yyyy-MM-dd"))

        self.notas_edit.setText(self.transacao.get("Notas", ""))

    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        favorecidos = self.favorecido_controller.listar_favorecidos() or []

        for fav in favorecidos:
            self.favorecido_combo.addItem(
                fav.get("Nome", ""),
                fav.get("ID_Favorecido")
            )

    def _toggle_transferencia(self):
        self.conta_destino_combo.setVisible(
            self.transfer_checkbox.isChecked()
        )

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):
        try:
            valor = self.valor_spin.value()

            if self.tipo_combo.currentText() == "Despesa":
                valor = -abs(valor)
            else:
                valor = abs(valor)

            dados = {
                "ID_Conta": self.conta_origem_combo.currentData(),
                "Tipo": self.tipo_combo.currentText(),
                "Descricao": self.desc_edit.text().strip(),
                "Valor": valor,
                "ID_Categoria": self.categoria_combo.currentData(),
                "ID_Favorecido": self.favorecido_combo.currentData(),
                "Data": self.data_edit.date().toString("yyyy-MM-dd"),
                "Notas": self.notas_edit.toPlainText(),
                "ID_Transacao": self.transacao.get("ID_Transacao")
            }

            if self.modo_temporario:
                self.dados_editados = dados
                self.accept()
                return

            self.transaction_controller.update_transaction(dados)

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Transação atualizada com sucesso.")
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )