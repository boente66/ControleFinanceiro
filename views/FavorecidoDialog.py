from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)
from controllers.favorecido_controller import FavorecidoController
from utilitarios.name_format import NameFormat


class FavorecidoDialog(QDialog):

    def __init__(self, parent=None, favorecido=None):
        super().__init__(parent)

        self.controller = FavorecidoController()
        self.favorecido = favorecido

        self.setWindowTitle("Favorecido")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # ================= TIPO =================
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Pessoa Física", "Pessoa Jurídica"])
        self.type_combo.currentIndexChanged.connect(self.update_fields)
        self.form_layout.addRow("Tipo:", self.type_combo)

        # ================= PESSOA FÍSICA =================
        self.name_input = QLineEdit()
        self.form_layout.addRow("Nome:", self.name_input)

        self.cpf_input = QLineEdit()
        self.form_layout.addRow("CPF:", self.cpf_input)

        self.telefone_pf_input = QLineEdit()
        self.form_layout.addRow("Telefone:", self.telefone_pf_input)

        # ================= PESSOA JURÍDICA =================
        self.fantasia_input = QLineEdit()
        self.form_layout.addRow("Nome Fantasia:", self.fantasia_input)

        self.razao_input = QLineEdit()
        self.form_layout.addRow("Razão Social:", self.razao_input)

        self.cnpj_input = QLineEdit()
        self.form_layout.addRow("CNPJ:", self.cnpj_input)

        self.telefone_pj_input = QLineEdit()
        self.form_layout.addRow("Telefone:", self.telefone_pj_input)

        layout.addLayout(self.form_layout)

        self.update_fields()

        # ================= BOTÕES =================
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_favorecido)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        if self.favorecido:
            self.load_favorecido_data()

    # =========================================================
    # CARREGAR DADOS PARA EDIÇÃO
    # =========================================================
    def load_favorecido_data(self):

        tipo = self.favorecido.get("Tipo")
        self.type_combo.setCurrentText(tipo)
        self.update_fields()

        if tipo == "Pessoa Física":
            self.name_input.setText(self.favorecido.get("Nome", ""))
            self.cpf_input.setText(self.favorecido.get("CPF", ""))
            self.telefone_pf_input.setText(
                self.favorecido.get("Telefone_PF", "")
            )
        else:
            self.fantasia_input.setText(
                self.favorecido.get("Nome_Fantasia", "")
            )
            self.razao_input.setText(
                self.favorecido.get("Razao_Social", "")
            )
            self.cnpj_input.setText(
                self.favorecido.get("CNPJ", "")
            )
            self.telefone_pj_input.setText(
                self.favorecido.get("Telefone_PJ", "")
            )

    # =========================================================
    # CONTROLAR CAMPOS VISÍVEIS
    # =========================================================
    def update_fields(self):

        tipo = self.type_combo.currentText()
        is_fisica = tipo == "Pessoa Física"

        # PF
        self._set_field_visibility(
            self.name_input,
            self.cpf_input,
            self.telefone_pf_input,
            visible=is_fisica
        )

        # PJ
        self._set_field_visibility(
            self.fantasia_input,
            self.razao_input,
            self.cnpj_input,
            self.telefone_pj_input,
            visible=not is_fisica
        )

    def _set_field_visibility(self, *fields, visible):
        for field in fields:
            field.setVisible(visible)
            label = self.form_layout.labelForField(field)
            if label:
                label.setVisible(visible)

    # =========================================================
    # SALVAR
    # =========================================================
    def save_favorecido(self):

        try:
            tipo = self.type_combo.currentText()

            if tipo == "Pessoa Física":

                nome = self.name_input.text().strip()
                cpf = NameFormat.formatCPF(self.cpf_input.text().strip())
                telefone = self.telefone_pf_input.text().strip()

                if not nome or not cpf:
                    raise ValueError("Nome e CPF são obrigatórios.")

                data = {
                    "Tipo": tipo,
                    "Nome": nome,
                    "CPF": cpf,
                    "Telefone_PF": telefone
                }

            else:

                fantasia = self.fantasia_input.text().strip()
                razao = self.razao_input.text().strip()
                cnpj = NameFormat.formatCNPJ(
                    self.cnpj_input.text().strip()
                )
                telefone = self.telefone_pj_input.text().strip()

                if not fantasia or not razao or not cnpj:
                    raise ValueError(
                        "Nome Fantasia, Razão Social e CNPJ são obrigatórios."
                    )

                data = {
                    "Tipo": tipo,
                    "Nome_Fantasia": fantasia,
                    "Razao_Social": razao,
                    "CNPJ": cnpj,
                    "Telefone_PJ": telefone
                }

            # ================= EDIÇÃO =================
            if self.favorecido:

                idfav = self.favorecido["ID_Favorecido"]
                sucesso = self.controller.atualizar_favorecido(idfav, data)

                if not sucesso:
                    raise ValueError("Falha ao atualizar favorecido.")

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Favorecido atualizado com sucesso!"
                )
                self.accept()
                return

            # ================= CRIAÇÃO =================
            sucesso = self.controller.adicionar_favorecido(data)

            if not sucesso:
                raise ValueError("Falha ao criar favorecido.")

            QMessageBox.information(
                self,
                "Sucesso",
                "Favorecido criado com sucesso!"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao salvar favorecido:\n{e}"
            )