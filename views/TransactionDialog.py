import logging
import re

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QFileDialog,
    QDateEdit, QSpinBox, QTextEdit
)
from PyQt5.QtCore import QDate

from core.translator_app import TranslatorApp

from controllers.favorecido_controller import FavorecidoController
from controllers.category_controller import CategoryController
from controllers.main_controller import MainController
from controllers.fatura_controller import FaturaController
from controllers.ia_import_controller import IAImportController

logger = logging.getLogger(__name__)


class TransactionDialog(QDialog):

    def __init__(self, parent=None, contexto=None, id_contexto=None):
        super().__init__(parent)

        self.contexto = contexto
        self.id_contexto = id_contexto
        self.usuario_id = getattr(parent, "usuario", {}).get("ID_Usuario")

        self.main_controller = MainController()
        self.fatura_controller = FaturaController()
        self.favorecido_controller = FavorecidoController()
        self.category_controller = CategoryController()
        self.import_controller = IAImportController()

        self.setMinimumWidth(820)

        self._build_ui()
        self._carregar_favorecidos()
        self._carregar_categorias()

        TranslatorApp.enable_auto_translation(self)

        # 🔥 UX bindings
        self.valor_edit.textChanged.connect(self._formatar_moeda)
        self.descricao_edit.textChanged.connect(self._auto_categoria)

        self.salvar_btn.setDefault(True)
        self.descricao_edit.setFocus()

    # ======================================================
    # UI
    # ======================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # LINHA 1
        l1 = QHBoxLayout()

        self.descricao_edit = QLineEdit()
        self.descricao_edit.setPlaceholderText("Descrição")

        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)

        l1.addWidget(self.descricao_edit, 3)
        l1.addWidget(self.data_edit, 1)
        layout.addLayout(l1)

        # LINHA 2
        l2 = QHBoxLayout()

        self.lbl_favorecido = QLabel("Favorecido")
        self.favorecido_combo = QComboBox()

        self.lbl_categoria = QLabel("Categoria")
        self.categoria_combo = QComboBox()

        bloco1 = QVBoxLayout()
        bloco1.addWidget(self.lbl_favorecido)
        bloco1.addWidget(self.favorecido_combo)

        bloco2 = QVBoxLayout()
        bloco2.addWidget(self.lbl_categoria)
        bloco2.addWidget(self.categoria_combo)

        l2.addLayout(bloco1)
        l2.addLayout(bloco2)

        layout.addLayout(l2)

        # LINHA 3
        l3 = QHBoxLayout()

        self.lbl_valor = QLabel("Valor")
        self.valor_edit = QLineEdit()
        self.valor_edit.setPlaceholderText("0,00")

        bloco_valor = QVBoxLayout()
        bloco_valor.addWidget(self.lbl_valor)
        bloco_valor.addWidget(self.valor_edit)

        l3.addLayout(bloco_valor)

        if self.contexto == "cartao":
            self.lbl_parcelas = QLabel("Parcelas")
            self.parcelas_spin = QSpinBox()
            self.parcelas_spin.setRange(1, 36)

            bloco_parc = QVBoxLayout()
            bloco_parc.addWidget(self.lbl_parcelas)
            bloco_parc.addWidget(self.parcelas_spin)

            l3.addLayout(bloco_parc)

        l3.addStretch()
        layout.addLayout(l3)

        # IMPORTAÇÃO
        l4 = QHBoxLayout()

        self.importar_btn = QPushButton("Importar comprovante")
        self.importar_btn.clicked.connect(self.importar_comprovante)

        self.lbl_anexos = QLabel("Nenhum arquivo")

        l4.addWidget(self.importar_btn)
        l4.addWidget(self.lbl_anexos)
        l4.addStretch()

        layout.addLayout(l4)

        # NOTAS
        self.lbl_notas = QLabel("Notas")
        self.notas_edit = QTextEdit()

        layout.addWidget(self.lbl_notas)
        layout.addWidget(self.notas_edit)

        # BOTÕES
        botoes = QHBoxLayout()

        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)

        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar)

        botoes.addStretch()
        botoes.addWidget(self.cancelar_btn)
        botoes.addWidget(self.salvar_btn)

        layout.addLayout(botoes)

    # ======================================================
    # 💰 MÁSCARA MOEDA
    # ======================================================
    def _formatar_moeda(self):
        texto = re.sub(r"[^\d]", "", self.valor_edit.text())

        if not texto:
            return

        valor = int(texto) / 100
        self.valor_edit.blockSignals(True)
        self.valor_edit.setText(f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.valor_edit.blockSignals(False)

    # ======================================================
    # 🧠 AUTO CATEGORIA
    # ======================================================
    def _auto_categoria(self):
        texto = self.descricao_edit.text().lower()

        mapa = {
            "uber": "Transporte",
            "99": "Transporte",
            "mercado": "Alimentação",
            "ifood": "Alimentação",
            "netflix": "Assinaturas",
            "energia": "Contas",
        }

        for chave, categoria in mapa.items():
            if chave in texto:
                index = self.categoria_combo.findText(categoria)
                if index >= 0:
                    self.categoria_combo.setCurrentIndex(index)

    # ======================================================
    # DADOS
    # ======================================================
    def _carregar_favorecidos(self):
        self.favorecido_combo.clear()
        self.favorecido_combo.addItem("Nenhum", None)

        for f in self.favorecido_controller.listar_favorecidos() or []:
            self.favorecido_combo.addItem(f["Nome"], f["ID_Favorecido"])

    def _carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Nenhum", None)

        for c in self.category_controller.get_all_categories() or []:
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
                id_conta=self.id_contexto if self.contexto == "conta" else None,
            )

            if not dados:
                raise ValueError("Nenhum dado reconhecido")

            self.descricao_edit.setText(dados.get("Descricao", ""))
            self.lbl_anexos.setText(caminho.split("/")[-1])

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    # ======================================================
    # SALVAR
    # ======================================================
    def salvar(self):
        try:
            if not self.descricao_edit.text().strip():
                self.descricao_edit.setStyleSheet("border: 1px solid red;")
                raise ValueError("Descrição obrigatória")

            valor = float(self.valor_edit.text().replace(".", "").replace(",", "."))
            data = self.data_edit.date().toString("yyyy-MM-dd")

            dados = {
                "Descricao": self.descricao_edit.text(),
                "Valor": abs(valor),
                "Data": data,
                "Notas": self.notas_edit.toPlainText(),
                "ID_Categoria": self.categoria_combo.currentData(),
            }

            if self.contexto == "conta":
                dados["ID_Conta"] = self.id_contexto
                self.main_controller.inserir_lancamento(dados)

            else:
                dados["ID_Cartao"] = self.id_contexto
                dados["Parcelas"] = int(self.parcelas_spin.value())
                self.fatura_controller.registrar_despesa_cartao(dados, self.usuario_id)

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Atenção", str(e))

        except Exception:
            logger.exception("Erro ao salvar")
            QMessageBox.critical(self, "Erro", "Erro ao salvar lançamento")
