from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit,
    QDialogButtonBox, QPushButton, QLineEdit,
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import QDate

from controllers.account_controller import AccountController
from controllers.category_controller import CategoryController
from controllers.favorecido_controller import FavorecidoController
from controllers.transaction_controller import TransactionController

from core.session import Session
from core.i18n import t


class EditTransactionDialog(QDialog):
    """
    Diálogo para edição de transações.
    Permite:
    - Editar Receita / Despesa
    - Converter explicitamente em Transferência
    """

    def __init__(self, transacao, parent=None, modo_temporario=False):
        super().__init__(parent)

        self.modo_temporario = modo_temporario
        # Sessão
        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado")

        self.id_usuario = self.usuario["ID_Usuario"]
        self.transacao = transacao or {}

        # Controllers
        self.transaction_controller = TransactionController()
        self.account_controller = AccountController()
        self.category_controller = CategoryController()
        self.favorecido_controller = FavorecidoController()

        self.setMinimumSize(520, 420)

        self._build_ui()
        self._preencher_campos()

        Session.on_idioma_change(self._retranslate)
        self._retranslate(Session.get_config("idioma", "Português"))

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # Conta origem
        self.conta_origem_combo = QComboBox()
        self.contas = self.account_controller.get_all_accounts(self.id_usuario) or []
        for conta in self.contas:
            self.conta_origem_combo.addItem(
                conta.get("Nome_Conta", ""),
                conta.get("ID_Conta")
            )
        self.form.addRow("", self.conta_origem_combo)

        # Tipo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Despesa", "Receita"])
        self.form.addRow("", self.tipo_combo)

        # Descrição
        self.desc_edit = QLineEdit()
        self.form.addRow("", self.desc_edit)

        # Valor
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setPrefix("R$ ")
        self.valor_spin.setRange(0.01, 1_000_000.00)
        self.valor_spin.setDecimals(2)
        self.form.addRow("", self.valor_spin)

        # Categoria
        self.categoria_combo = QComboBox()
        categorias = self.category_controller.get_all_categories() or []
        for cat in categorias:
            self.categoria_combo.addItem(
                cat.get("Nome", ""),
                cat.get("ID_Categoria")
            )
        self.form.addRow("", self.categoria_combo)

        # Favorecido
        self.favorecido_combo = QComboBox()
        self._carregar_favorecidos()
        self.form.addRow("", self.favorecido_combo)

        # Data
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        self.form.addRow("", self.data_edit)

        # Notas
        self.notas_edit = QTextEdit()
        self.notas_edit.setFixedHeight(80)
        self.form.addRow("", self.notas_edit)

        # 🔁 Converter em transferência
        self.transfer_checkbox = QCheckBox()
        self.transfer_checkbox.stateChanged.connect(self._toggle_transferencia)
        self.form.addRow("", self.transfer_checkbox)

        # Conta destino
        self.conta_destino_combo = QComboBox()
        for conta in self.contas:
            self.conta_destino_combo.addItem(
                conta.get("Nome_Conta", ""),
                conta.get("ID_Conta")
            )
        self.conta_destino_combo.setVisible(False)
        self.form.addRow("", self.conta_destino_combo)

        layout.addLayout(self.form)

        # Botões
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.salvar)
        self.button_box.rejected.connect(self.reject)

    # ======================================================
    # TRADUÇÃO
    # ======================================================
    def _retranslate(self, idioma):
        self.setWindowTitle(t("Editar Transação", idioma))

        self.form.setWidget(0, QFormLayout.LabelRole, 
                            QPushButton(t("Conta:", idioma)))
        self.form.setWidget(1, QFormLayout.LabelRole, 
                            QPushButton(t("Tipo:", idioma)))
        self.form.setWidget(2, QFormLayout.LabelRole, 
                            QPushButton(t("Descrição:", idioma)))
        self.form.setWidget(3, QFormLayout.LabelRole, 
                            QPushButton(t("Valor:", idioma)))
        self.form.setWidget(4, QFormLayout.LabelRole, 
                            QPushButton(t("Categoria:", idioma)))
        self.form.setWidget(5, QFormLayout.LabelRole, 
                            QPushButton(t("Favorecido:", idioma)))
        self.form.setWidget(6, QFormLayout.LabelRole, 
                            QPushButton(t("Data:", idioma)))
        self.form.setWidget(7, QFormLayout.LabelRole, 
                            QPushButton(t("Notas:", idioma)))
        self.form.setWidget(8, QFormLayout.LabelRole, 
                            QPushButton(""))
        self.form.setWidget(9, QFormLayout.LabelRole, 
                            QPushButton(t("Conta destino:", idioma)))

        self.transfer_checkbox.setText(
            t("Converter em transferência", idioma)
        )

        self.button_box.button(QDialogButtonBox.Save).setText(
            t("Salvar", idioma)
        )
        self.button_box.button(QDialogButtonBox.Cancel).setText(
            t("Cancelar", idioma)
        )

    # ======================================================
    # PREENCHER CAMPOS
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

    # ======================================================
    # FAVORECIDOS
    # ======================================================
    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        favorecidos = self.favorecido_controller.listar_favorecidos(
            self.id_usuario
        ) or []

        for fav in favorecidos:
            self.favorecido_combo.addItem(
                fav.get("Nome", ""),
                fav.get("ID_Favorecido")
            )

    # ======================================================
    # TOGGLE TRANSFERÊNCIA
    # ======================================================
    def _toggle_transferencia(self):
        ativo = self.transfer_checkbox.isChecked()
        self.conta_destino_combo.setVisible(ativo)

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):

        idioma = Session.get_config("idioma", "Português")

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

            # MODO TEMPORÁRIO
            if self.modo_temporario:
                self.dados_editados = dados
                self.accept()
                return

            # Controller injeta ID_Usuario
            self.transaction_controller.update_transaction(dados)

            QMessageBox.information(
                self,
                t("Sucesso", idioma),
                t("Transação atualizada com sucesso.", idioma)
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                t("Erro", idioma),
                str(e)
            )