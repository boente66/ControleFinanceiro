import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDoubleSpinBox,
    QSpinBox, QCheckBox, QMessageBox
)

from controllers.fatura_controller import FaturaController
from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


# ==========================================================
# CRIAR CARTÃO
# ==========================================================
class CriarCartaoDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = FaturaController()

        # 🔥 título base (auto traduzido)
        self.setWindowTitle("Cadastrar Cartão")

        self.setMinimumWidth(360)

        self._init_ui()

        # 🔥 ativa tradução automática
        TranslatorApp.enable_auto_translation(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Nome
        self.lbl_nome = QLabel("Nome do cartão")
        layout.addWidget(self.lbl_nome)

        self.nome_edit = QLineEdit()
        self.nome_edit.setPlaceholderText("Ex: Nubank, Itaú")
        layout.addWidget(self.nome_edit)

        # Limite
        self.lbl_limite = QLabel("Limite do cartão")
        layout.addWidget(self.lbl_limite)

        self.limite_edit = QDoubleSpinBox()
        self.limite_edit.setPrefix("R$ ")
        self.limite_edit.setRange(0.01, 1_000_000.00)
        self.limite_edit.setDecimals(2)
        layout.addWidget(self.limite_edit)

        # Fechamento
        self.lbl_fechamento = QLabel("Dia de fechamento da fatura")
        layout.addWidget(self.lbl_fechamento)

        self.fechamento_edit = QSpinBox()
        self.fechamento_edit.setRange(1, 31)
        layout.addWidget(self.fechamento_edit)

        # Vencimento
        self.lbl_vencimento = QLabel("Dia de vencimento da fatura")
        layout.addWidget(self.lbl_vencimento)

        self.vencimento_edit = QSpinBox()
        self.vencimento_edit.setRange(1, 31)
        layout.addWidget(self.vencimento_edit)

        # Ativo
        self.ativo_checkbox = QCheckBox("Cartão ativo")
        self.ativo_checkbox.setChecked(True)
        layout.addWidget(self.ativo_checkbox)

        # Botões
        btns = QHBoxLayout()

        self.salvar_btn = QPushButton("Salvar")
        self.cancelar_btn = QPushButton("Cancelar")

        self.salvar_btn.clicked.connect(self._salvar)
        self.cancelar_btn.clicked.connect(self.reject)

        btns.addWidget(self.salvar_btn)
        btns.addWidget(self.cancelar_btn)
        layout.addLayout(btns)

    # --------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------
    def _validar(self):
        nome = self.nome_edit.text().strip()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("Nome do cartão é obrigatório.")
            )
            return False

        if self.fechamento_edit.value() == self.vencimento_edit.value():
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("Dia de fechamento não pode ser igual ao dia de vencimento.")
            )
            return False

        return True

    # --------------------------------------------------
    # SALVAR
    # --------------------------------------------------
    def _salvar(self):
        if not self._validar():
            return

        dados = {
            "nome": self.nome_edit.text().strip(),
            "limite": round(self.limite_edit.value(), 2),
            "dia_fechamento": self.fechamento_edit.value(),
            "dia_vencimento": self.vencimento_edit.value(),
            "ativo": 1 if self.ativo_checkbox.isChecked() else 0,
        }

        try:
            self.controller.adicionar_cartao(dados)

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Cartão criado com sucesso.")
            )
            self.accept()

        except Exception:
            logger.exception("Erro ao criar cartão")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro ao salvar cartão.")
            )


# ==========================================================
# EDITAR CARTÃO
# ==========================================================
class EditCartaoDialog(QDialog):

    def __init__(self, parent=None, cartao=None):
        super().__init__(parent)

        self.cartao = cartao or {}
        self.controller = FaturaController()

        # 🔥 título base (auto traduzido)
        self.setWindowTitle("Editar Cartão")

        self.setMinimumWidth(360)

        self._init_ui()
        self._preencher_campos()

        # 🔥 tradução automática
        TranslatorApp.enable_auto_translation(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_nome = QLabel("Nome do cartão")
        layout.addWidget(self.lbl_nome)

        self.nome_edit = QLineEdit()
        layout.addWidget(self.nome_edit)

        self.lbl_limite = QLabel("Limite do cartão")
        layout.addWidget(self.lbl_limite)

        self.limite_edit = QDoubleSpinBox()
        self.limite_edit.setPrefix("R$ ")
        self.limite_edit.setRange(0.01, 1_000_000.00)
        self.limite_edit.setDecimals(2)
        layout.addWidget(self.limite_edit)

        self.lbl_fechamento = QLabel("Dia de fechamento da fatura")
        layout.addWidget(self.lbl_fechamento)

        self.fechamento_edit = QSpinBox()
        self.fechamento_edit.setRange(1, 31)
        layout.addWidget(self.fechamento_edit)

        self.lbl_vencimento = QLabel("Dia de vencimento da fatura")
        layout.addWidget(self.lbl_vencimento)

        self.vencimento_edit = QSpinBox()
        self.vencimento_edit.setRange(1, 31)
        layout.addWidget(self.vencimento_edit)

        self.ativo_checkbox = QCheckBox("Cartão ativo")
        layout.addWidget(self.ativo_checkbox)

        btns = QHBoxLayout()

        self.salvar_btn = QPushButton("Salvar")
        self.cancelar_btn = QPushButton("Cancelar")

        self.salvar_btn.clicked.connect(self._salvar)
        self.cancelar_btn.clicked.connect(self.reject)

        btns.addWidget(self.salvar_btn)
        btns.addWidget(self.cancelar_btn)
        layout.addLayout(btns)

    def _preencher_campos(self):
        self.nome_edit.setText(self.cartao.get("nome", ""))
        self.limite_edit.setValue(float(self.cartao.get("limite", 0)))
        self.fechamento_edit.setValue(int(self.cartao.get("dia_fechamento", 1)))
        self.vencimento_edit.setValue(int(self.cartao.get("dia_vencimento", 1)))
        self.ativo_checkbox.setChecked(bool(self.cartao.get("ativo", 1)))

    def _salvar(self):
        nome = self.nome_edit.text().strip()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Atenção"),
                TranslatorApp.get("Nome do cartão é obrigatório.")
            )
            return

        dados = {
            "nome": nome,
            "limite": round(self.limite_edit.value(), 2),
            "dia_fechamento": self.fechamento_edit.value(),
            "dia_vencimento": self.vencimento_edit.value(),
            "ativo": 1 if self.ativo_checkbox.isChecked() else 0,
        }

        try:
            self.controller.editar_cartao(
                self.cartao["ID_Cartao"],
                dados
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Cartão atualizado com sucesso.")
            )
            self.accept()

        except Exception:
            logger.exception("Erro ao editar cartão")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro ao salvar cartão.")
            )
