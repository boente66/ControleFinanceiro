# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
)

from controllers.account_controller import AccountController
from core.translator_app import TranslatorApp


class EditarContaDialog(QDialog):

    def __init__(self, parent=None, conta=None):
        super().__init__(parent)

        if not conta:
            raise ValueError("Conta é obrigatória")

        self.conta = conta
        self.controller = AccountController()

        self.setMinimumWidth(400)

        self._init_ui()

        TranslatorApp.bind(self._atualizar_textos, self)
        self._atualizar_textos()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_nome = QLabel()
        layout.addWidget(self.lbl_nome)

        self.nome_edit = QLineEdit(
            self.conta.get("Nome_Conta", "")
        )
        layout.addWidget(self.nome_edit)

        self.lbl_inst = QLabel()
        layout.addWidget(self.lbl_inst)

        self.inst_edit = QLineEdit(
            self.conta.get("Instituicao", "")
        )
        layout.addWidget(self.inst_edit)

        self.lbl_tipo = QLabel()
        layout.addWidget(self.lbl_tipo)

        self.tipo_combo = QComboBox()

        tipos = [
            ("Corrente", "Corrente"),
            ("Poupança", "Poupança"),
            ("Investimento", "Investimento"),
        ]

        for texto, valor in tipos:
            self.tipo_combo.addItem(texto, valor)

        index = self.tipo_combo.findData(
            self.conta.get("Tipo", "Corrente")
        )

        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)

        layout.addWidget(self.tipo_combo)

        botoes = QHBoxLayout()

        self.salvar_btn = QPushButton()
        self.cancelar_btn = QPushButton()

        self.salvar_btn.clicked.connect(self.salvar)
        self.cancelar_btn.clicked.connect(self.reject)

        botoes.addWidget(self.salvar_btn)
        botoes.addWidget(self.cancelar_btn)

        layout.addLayout(botoes)

    # --------------------------------------------------
    # TRADUÇÃO
    # --------------------------------------------------
    def _atualizar_textos(self):
        self.setWindowTitle(
            TranslatorApp.get("Editar Conta")
        )

        self.lbl_nome.setText(
            TranslatorApp.get("Nome da Conta")
        )

        self.nome_edit.setPlaceholderText(
            TranslatorApp.get("Ex: Conta Principal")
        )

        self.lbl_inst.setText(
            TranslatorApp.get("Instituição")
        )

        self.inst_edit.setPlaceholderText(
            TranslatorApp.get("Ex: Nubank, Itaú")
        )

        self.lbl_tipo.setText(
            TranslatorApp.get("Tipo da Conta")
        )

        self.salvar_btn.setText(
            TranslatorApp.get("Salvar")
        )

        self.cancelar_btn.setText(
            TranslatorApp.get("Cancelar")
        )

    # --------------------------------------------------
    # SALVAR
    # --------------------------------------------------
    def salvar(self):
        nome = self.nome_edit.text().strip()
        instituicao = self.inst_edit.text().strip()
        tipo = self.tipo_combo.currentData()

        if not nome:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("O nome da conta é obrigatório.")
            )
            return

        try:
            dados = {
                "Nome_Conta": nome,
                "Instituicao": instituicao,
                "Tipo": tipo,
            }

            self.controller.update_account(
                self.conta["ID_Conta"],
                dados
            )

            QMessageBox.information(
                self,
                TranslatorApp.get("Sucesso"),
                TranslatorApp.get("Conta atualizada com sucesso.")
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                str(e)
            )

    # --------------------------------------------------
    # CICLO DE VIDA
    # --------------------------------------------------
    def closeEvent(self, event):
        try:
            TranslatorApp.unbind(self)
        except Exception:
            pass

        super().closeEvent(event)
