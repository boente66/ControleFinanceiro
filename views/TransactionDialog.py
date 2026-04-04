import logging

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QFileDialog,
    QDateEdit,
    QSpinBox,
)
from PyQt5.QtCore import QDate

from core.translator_app import TranslatorApp

from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController
from controllers.main_controller import MainController
from controllers.fatura_controller import FaturaController
from controllers.ia_import_controller import IAImportController
from core.translator_binding import TranslatorBinding


logger = logging.getLogger(__name__)


class TransactionDialog(QDialog):

    def __init__(self, parent=None, contexto=None, id_contexto=None):
        super().__init__(parent)

        self.contexto = contexto
        self.id_contexto = id_contexto

        # 🔥 importante (corrige bug oculto)
        self.usuario_id = getattr(parent, "usuario", {}).get("ID_Usuario")

        self.main_controller = MainController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self.import_controller = IAImportController()

        self.setMinimumWidth(520)
        self.setWindowTitle("Novo Lançamento")

        self._build_ui()

        self._carregar_favorecidos()
        self._carregar_categorias()

        # 🔥 bind necessário (labels + combos dinâmicos)
        TranslatorBinding.bind(self._on_translate)

    # ======================================================
    # REATIVIDADE
    # ======================================================
    def _on_translate(self, *_):

        self.setWindowTitle(TranslatorApp.get("Novo Lançamento"))

        self.lbl_favorecido.setText(TranslatorApp.get("Favorecido"))
        self.lbl_categoria.setText(TranslatorApp.get("Categoria"))
        self.lbl_valor.setText(TranslatorApp.get("Valor"))

        self.descricao_edit.setPlaceholderText(TranslatorApp.get("Descrição"))
        self.valor_edit.setPlaceholderText("0,00")

        self.importar_btn.setText(TranslatorApp.get("Importar comprovante"))
        self.salvar_btn.setText(TranslatorApp.get("Salvar"))

        if self.contexto == "cartao":
            self.lbl_parcelas.setText(TranslatorApp.get("Parcelas"))

        # 🔥 recarregar dados traduzidos
        self._carregar_favorecidos()
        self._carregar_categorias()

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -------------------------
        # LINHA 1
        # -------------------------
        linha1 = QHBoxLayout()

        self.descricao_edit = QLineEdit()
        linha1.addWidget(self.descricao_edit)

        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        linha1.addWidget(self.data_edit)

        layout.addLayout(linha1)

        # -------------------------
        # FAVORECIDO
        # -------------------------
        self.lbl_favorecido = QLabel()
        layout.addWidget(self.lbl_favorecido)

        self.favorecido_combo = QComboBox()
        layout.addWidget(self.favorecido_combo)

        # -------------------------
        # CATEGORIA
        # -------------------------
        self.lbl_categoria = QLabel()
        layout.addWidget(self.lbl_categoria)

        self.categoria_combo = QComboBox()
        layout.addWidget(self.categoria_combo)

        # -------------------------
        # VALOR
        # -------------------------
        self.lbl_valor = QLabel()
        layout.addWidget(self.lbl_valor)

        self.valor_edit = QLineEdit()
        layout.addWidget(self.valor_edit)

        # -------------------------
        # CARTÃO (parcelas)
        # -------------------------
        if self.contexto == "cartao":
            self.lbl_parcelas = QLabel()
            layout.addWidget(self.lbl_parcelas)

            self.parcelas_spin = QSpinBox()
            self.parcelas_spin.setMinimum(1)
            self.parcelas_spin.setMaximum(36)
            self.parcelas_spin.setValue(1)
            layout.addWidget(self.parcelas_spin)

        # -------------------------
        # BOTÕES
        # -------------------------
        botoes = QHBoxLayout()

        self.importar_btn = QPushButton()
        self.importar_btn.clicked.connect(self.importar_comprovante)

        self.salvar_btn = QPushButton()
        self.salvar_btn.clicked.connect(self.salvar)

        botoes.addWidget(self.importar_btn)
        botoes.addStretch()
        botoes.addWidget(self.salvar_btn)

        layout.addLayout(botoes)

    # ======================================================
    # DADOS
    # ======================================================
    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        self.favorecido_combo.addItem(TranslatorApp.get("Nenhum"), None)

        for f in self.favorecido_controller.listar_favorecidos():
            self.favorecido_combo.addItem(f["Nome"], f["ID_Favorecido"])

    def _carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem(TranslatorApp.get("Nenhum"), None)

        for c in self.category_controller.get_all_categories():
            self.categoria_combo.addItem(c["Nome"], c["ID_Categoria"])

    # ======================================================
    # IMPORTAÇÃO
    # ======================================================
    def importar_comprovante(self):

        caminho, _ = QFileDialog.getOpenFileName(
            self,
            TranslatorApp.get("Importar comprovante"),
            "",
            "Arquivos (*.pdf *.csv *.xlsx)",
        )

        if not caminho:
            return

        try:
            dados = self.import_controller.importar_comprovante_pdf(
                caminho_pdf=caminho,
                id_usuario=self.usuario_id,
                id_conta=self.id_contexto if self.contexto == "conta" else None,
            )

            if not dados:
                raise ValueError(TranslatorApp.get("Nenhum dado reconhecido"))

            self.descricao_edit.setText(dados.get("Descricao", ""))
            self.valor_edit.setText(str(dados.get("Valor", "")).replace(".", ","))

            if dados.get("Data"):
                self.data_edit.setDate(QDate.fromString(dados["Data"], "yyyy-MM-dd"))

        except Exception as e:
            QMessageBox.critical(self, TranslatorApp.get("Erro"), str(e))

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):
        try:
            descricao = self.descricao_edit.text().strip()
            if not descricao:
                raise ValueError(TranslatorApp.get("Descrição obrigatória"))

            valor = float(self.valor_edit.text().replace(",", "."))
            data_compra = self.data_edit.date().toString("yyyy-MM-dd")

            if self.contexto == "conta":

                dados = {
                    "Descricao": descricao,
                    "Valor": abs(valor),
                    "Data": data_compra,
                    "ID_Conta": self.id_contexto,
                    "ID_Favorecido": self.favorecido_combo.currentData(),
                    "ID_Categoria": self.categoria_combo.currentData(),
                    "Tipo": "Despesa",
                }

                self.main_controller.inserir_lancamento(dados)
                self.accept()
                return

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

                self.fatura_controller.registrar_despesa_cartao(dados, self.usuario_id)

                self.accept()

        except ValueError as e:
            QMessageBox.warning(self, TranslatorApp.get("Atenção"), str(e))

        except Exception:
            logger.exception("Erro ao salvar transação")
            QMessageBox.critical(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Erro ao salvar lançamento"),
            )
