from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QComboBox, QFileDialog, QDateEdit, QSpinBox
)
from PyQt5.QtCore import QDate

from core.session import Session
from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController
from controllers.main_controller import MainController
from controllers.fatura_controller import FaturaController
from controllers.ia_import_controller import IAImportController


class TransactionDialog(QDialog):
    """
    Diálogo de lançamento:
    - Conta bancária
    - Cartão de crédito (fatura aplicada automaticamente)
    """

    def __init__(self, parent=None, contexto=None, id_contexto=None):
        super().__init__(parent)

        self.contexto = contexto            # conta | cartao
        self.id_contexto = id_contexto      # ID_Conta ou ID_Cartao

        self.usuario = Session.get_usuario()
        if not self.usuario:
            raise RuntimeError("Usuário não autenticado")

        self.usuario_id = self.usuario["ID_Usuario"]

        # controllers
        self.main_controller = MainController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self.import_controller = IAImportController()

        self.setWindowTitle("Novo Lançamento")
        self.setMinimumWidth(520)

        self._build_ui()
        self._carregar_favorecidos()
        self._carregar_categorias()

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Descrição + Data
        linha1 = QHBoxLayout()

        self.descricao_edit = QLineEdit()
        self.descricao_edit.setPlaceholderText("Descrição")
        linha1.addWidget(self.descricao_edit)

        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        linha1.addWidget(self.data_edit)

        layout.addLayout(linha1)

        # Favorecido
        layout.addWidget(QLabel("Favorecido"))
        self.favorecido_combo = QComboBox()
        layout.addWidget(self.favorecido_combo)

        # Categoria
        layout.addWidget(QLabel("Categoria"))
        self.categoria_combo = QComboBox()
        layout.addWidget(self.categoria_combo)

        # Valor
        layout.addWidget(QLabel("Valor"))
        self.valor_edit = QLineEdit()
        self.valor_edit.setPlaceholderText("0,00")
        layout.addWidget(self.valor_edit)

        # ==================================================
        # CONTEXTO CARTÃO
        # ==================================================
        if self.contexto == "cartao":
            layout.addWidget(QLabel("Parcelas"))
            self.parcelas_spin = QSpinBox()
            self.parcelas_spin.setMinimum(1)
            self.parcelas_spin.setMaximum(36)
            self.parcelas_spin.setValue(1)
            layout.addWidget(self.parcelas_spin)

        # Botões
        botoes = QHBoxLayout()

        importar_btn = QPushButton("Importar comprovante")
        importar_btn.clicked.connect(self.importar_comprovante)

        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self.salvar)

        botoes.addWidget(importar_btn)
        botoes.addStretch()
        botoes.addWidget(salvar_btn)

        layout.addLayout(botoes)

    # ======================================================
    # DADOS AUXILIARES
    # ======================================================
    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        self.favorecido_combo.addItem("—", None)

        favorecidos = self.favorecido_controller.listar_favorecidos()
        for f in favorecidos:
            self.favorecido_combo.addItem(f["Nome"], f["ID_Favorecido"])

    def _carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("—", None)

        categorias = self.category_controller.get_all_categories()
        for c in categorias:
            self.categoria_combo.addItem(c["Nome"], c["ID_Categoria"])

    # ======================================================
    # IMPORTAÇÃO
    # ======================================================
    def importar_comprovante(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Importar comprovante", "", "Arquivos (*.pdf *.csv *.xlsx)"
        )
        if not caminho:
            return

        try:
            dados = self.import_controller.importar_comprovante_pdf(
                caminho_pdf=caminho,
                id_usuario=self.usuario_id,
                id_conta=self.id_contexto if self.contexto == "conta" else None
            )

            if not dados:
                raise ValueError("Nenhum dado reconhecido.")

            self.descricao_edit.setText(dados.get("Descricao", ""))
            self.valor_edit.setText(str(dados.get("Valor", "")).replace(".", ","))

            if dados.get("Data"):
                self.data_edit.setDate(
                    QDate.fromString(dados["Data"], "yyyy-MM-dd")
                )

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):
        try:
            descricao = self.descricao_edit.text().strip()
            if not descricao:
                raise ValueError("Descrição obrigatória.")

            valor = float(self.valor_edit.text().replace(",", "."))
            data_compra = self.data_edit.date().toString("yyyy-MM-dd")

            # ------------------------------
            # CONTA BANCÁRIA
            # ------------------------------
            if self.contexto == "conta":
                dados = {
                    "Descricao": descricao,
                    "Valor": abs(valor),
                    "Data": data_compra,
                    "ID_Conta": self.id_contexto,
                    "ID_Favorecido": self.favorecido_combo.currentData(),
                    "ID_Categoria": self.categoria_combo.currentData(),
                    "ID_Usuario": self.usuario_id,
                    "Tipo": "Despesa",
                }

                self.main_controller.inserir_lancamento(dados)
                self.accept()
                return

            # ------------------------------
            # CARTÃO DE CRÉDITO
            # ------------------------------
            if self.contexto == "cartao":
                parcelas = int(self.parcelas_spin.value())

                dados = {
                    "ID_Cartao": self.id_contexto,
                    "ID_Usuario": self.usuario_id,

                    "Descricao": descricao,
                    "Valor": abs(valor),
                    "Data": data_compra,

                    "Parcelas": parcelas,

                    "ID_Categoria": self.categoria_combo.currentData(),
                    "Categoria": self.categoria_combo.currentText(),
                    "Notas": None,
                }

                # 🔥 Fatura aplicada automaticamente no Service
                self.fatura_controller.registrar_despesa_cartao(
                    dados, self.usuario_id
                )

                self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Atenção", str(e))
        except Exception:
            QMessageBox.critical(self, "Erro", "Erro ao salvar lançamento.")
