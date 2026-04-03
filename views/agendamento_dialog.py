import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QMessageBox, QDoubleSpinBox,
    QLabel, QCheckBox
)
from PyQt5.QtCore import QDate, Qt

from controllers.schedule_controller import ScheduleController
from controllers.account_controller import AccountController
from controllers.category_controller import CategoryController
from controllers.favorecido_controller import FavorecidoController

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class AgendamentoDialog(QDialog):

    TIPOS = ["Contas a Pagar", "Contas a Receber", "Transferências"]
    PERIODICIDADES = ["Mensal", "Anual"]

    def __init__(self, parent=None, agendamento_id=None):
        super().__init__(parent)

        self.agendamento_id = agendamento_id

        self.schedule_controller = ScheduleController()
        self.account_controller = AccountController()
        self.category_controller = CategoryController()
        self.favorecido_controller = FavorecidoController()

        # 🔥 TÍTULO REATIVO GLOBAL
        TranslatorApp.window_title(
            self,
            "Adicionar Agendamento" if agendamento_id is None else "Editar Agendamento"
        )

        self._build_ui()
        self._connect_signals()

        if self.agendamento_id:
            self._carregar_para_edicao()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignRight)

        # Tipo
        self.tipo_label = QLabel()
        TranslatorApp.text(self.tipo_label, "Tipo")

        self.tipo_combo = QComboBox()
        TranslatorApp.combo(self.tipo_combo, self.TIPOS)

        self.form.addRow(self.tipo_label, self.tipo_combo)

        # Descrição
        self.desc_label = QLabel()
        TranslatorApp.text(self.desc_label, "Descrição")

        self.descricao_input = QLineEdit()
        self.form.addRow(self.desc_label, self.descricao_input)

        # Conta
        self.conta_label = QLabel()
        TranslatorApp.text(self.conta_label, "Conta")

        self.conta_combo = QComboBox()
        self.form.addRow(self.conta_label, self.conta_combo)

        # Favorecido
        self.fav_label = QLabel()
        TranslatorApp.text(self.fav_label, "Favorecido")

        self.favorecido_combo = QComboBox()
        self.form.addRow(self.fav_label, self.favorecido_combo)

        # Categoria
        self.cat_label = QLabel()
        TranslatorApp.text(self.cat_label, "Categoria")

        self.categoria_combo = QComboBox()
        self.form.addRow(self.cat_label, self.categoria_combo)

        # Valor
        self.valor_label = QLabel()
        TranslatorApp.text(self.valor_label, "Valor")

        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setDecimals(2)
        self.valor_spin.setRange(0.01, 10_000_000)
        self.valor_spin.setPrefix("R$ ")

        self.form.addRow(self.valor_label, self.valor_spin)

        # Data
        self.data_label = QLabel()
        TranslatorApp.text(self.data_label, "Vencimento")

        self.data_vencimento = QDateEdit(QDate.currentDate())
        self.data_vencimento.setCalendarPopup(True)

        self.form.addRow(self.data_label, self.data_vencimento)

        # Recorrência
        self.recorrente_label = QLabel()
        TranslatorApp.text(self.recorrente_label, "Recorrente")

        self.recorrente_check = QCheckBox()
        self.form.addRow(self.recorrente_label, self.recorrente_check)

        self.periodicidade_label = QLabel()
        TranslatorApp.text(self.periodicidade_label, "Periodicidade")

        self.periodicidade_combo = QComboBox()
        TranslatorApp.combo(self.periodicidade_combo, self.PERIODICIDADES)
        self.periodicidade_combo.setEnabled(False)

        self.form.addRow(self.periodicidade_label, self.periodicidade_combo)

        layout.addLayout(self.form)

        # BOTÕES
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        layout.addWidget(self.button_box)

        # 🔥 BOTÕES REATIVOS
        TranslatorApp.text(
            self.button_box.button(QDialogButtonBox.Save),
            "Salvar"
        )
        TranslatorApp.text(
            self.button_box.button(QDialogButtonBox.Cancel),
            "Cancelar"
        )

        self.load_contas()
        self.load_favorecidos()
        self.load_categorias()

    # ==================================================
    # SIGNALS
    # ==================================================
    def _connect_signals(self):
        self.button_box.accepted.connect(self.save_agendamento)
        self.button_box.rejected.connect(self.reject)

        self.recorrente_check.stateChanged.connect(
            lambda: self.periodicidade_combo.setEnabled(
                self.recorrente_check.isChecked()
            )
        )

    # ==================================================
    # DADOS
    # ==================================================
    def load_contas(self):
        self.conta_combo.clear()
        contas = self.account_controller.get_all_accounts()
        for c in contas:
            self.conta_combo.addItem(c["Nome_Conta"], c["ID_Conta"])

    def load_favorecidos(self):
        self.favorecido_combo.clear()
        favs = self.favorecido_controller.listar_favorecidos()
        for f in favs:
            self.favorecido_combo.addItem(f["Nome"], f["ID_Favorecido"])

    def load_categorias(self):
        self.categoria_combo.clear()
        categorias = self.category_controller.get_all_categories() or []
        for c in categorias:
            self.categoria_combo.addItem(c["Nome"], c["ID_Categoria"])

    # ==================================================
    # EDIÇÃO
    # ==================================================
    def _carregar_para_edicao(self):
        dados = self.schedule_controller.get_schedule_by_id(
            self.agendamento_id
        )

        if not dados:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Aviso"),
                TranslatorApp.get("Agendamento não encontrado")
            )
            self.reject()
            return

        self.tipo_combo.setCurrentText(dados.get("Tipo"))
        self.descricao_input.setText(dados.get("Descricao", ""))
        self.valor_spin.setValue(float(dados.get("Valor", 0)))

        data = QDate.fromString(dados.get("Data"), "yyyy-MM-dd")
        if data.isValid():
            self.data_vencimento.setDate(data)

        recorrente = bool(dados.get("Recorrente", 0))
        self.recorrente_check.setChecked(recorrente)
        self.periodicidade_combo.setEnabled(recorrente)

        periodicidade = dados.get("Periodicidade")
        if periodicidade:
            index = self.periodicidade_combo.findText(periodicidade)
            if index >= 0:
                self.periodicidade_combo.setCurrentIndex(index)

    # ==================================================
    # SALVAR
    # ==================================================
    def save_agendamento(self):

        if not self.descricao_input.text().strip():
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("Descrição obrigatória.")
            )
            return

        data = {
            "Tipo": self.tipo_combo.currentText(),
            "Descricao": self.descricao_input.text().strip(),
            "ID_Conta": self.conta_combo.currentData(),
            "ID_Favorecido": self.favorecido_combo.currentData(),
            "ID_Categoria": self.categoria_combo.currentData(),
            "Valor": float(self.valor_spin.value()),
            "Data": self.data_vencimento.date().toString("yyyy-MM-dd"),
            "Recorrente": 1 if self.recorrente_check.isChecked() else 0,
            "Periodicidade": (
                self.periodicidade_combo.currentText()
                if self.recorrente_check.isChecked()
                else None
            ),
        }

        try:
            if self.agendamento_id:
                self.schedule_controller.update_schedule(
                    self.agendamento_id,
                    data
                )
            else:
                self.schedule_controller.add_schedule(data)

            self.accept()

        except Exception as e:
            logger.exception("Erro ao salvar agendamento")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                f"{TranslatorApp.get('Erro ao salvar')}:\n{e}"
            )
