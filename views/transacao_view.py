import logging

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QMenu,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt

from controllers.account_controller import AccountController
from controllers.fatura_controller import FaturaController

from core.translator_binding import TranslatorBinding
from views.criar_conta_dialog import CriarContaDialog
from views.editar_conta_dialog import EditarContaDialog
from views.criar_cartao_dialog import CriarCartaoDialog, EditCartaoDialog
from views.ajustar_saldo_dialog import AjustarSaldoDialog

from views.painel_account import PainelAccount
from views.painel_fatura import PainelFatura

from utilitarios.currency_formatter import CurrencyFormatter

from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class TransacaoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.account_controller = AccountController()
        self.fatura_controller = FaturaController()

        self.painel_ativo = None

        self.setWindowTitle("Contas e Lançamentos")

        self.main_layout = QHBoxLayout(self)

        self._montar_painel_esquerdo()
        self._montar_area_painel()

        self.carregar_contas()
        self.carregar_cartoes()

        # 🔥 precisa (listas + labels dinâmicos)
        TranslatorBinding.bind(self._on_translate)

    # ==========================================================
    # REATIVIDADE
    # ==========================================================
    def _on_translate(self, *_):
        self.lbl_contas.setText(TranslatorApp.get("Contas e Poupanças"))
        self.lbl_cartoes.setText(TranslatorApp.get("Cartões de Crédito"))

        self.carregar_contas()
        self.carregar_cartoes()

    # ==========================================================
    # PAINEL ESQUERDO
    # ==========================================================
    def _montar_painel_esquerdo(self):

        self.left = QVBoxLayout()
        self.left.setSpacing(10)

        contas_box, self.lista_contas, self.lbl_contas = self._criar_lista_com_header(
            "Contas e Poupanças", self.criar_conta_dialog, altura_max=220
        )

        self.lista_contas.itemClicked.connect(self.selecionar_conta)
        self.lista_contas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista_contas.customContextMenuRequested.connect(self.menu_conta)

        self.lbl_saldo_total_contas = QLabel()
        self.lbl_saldo_total_contas.setAlignment(Qt.AlignRight)
        self.lbl_saldo_total_contas.setObjectName("muted")

        contas_box.addWidget(self.lbl_saldo_total_contas)
        self.left.addLayout(contas_box)

        cartoes_box, self.lista_cartoes, self.lbl_cartoes = (
            self._criar_lista_com_header(
                "Cartões de Crédito", self.criar_cartao_dialog, altura_max=160
            )
        )

        self.lista_cartoes.itemClicked.connect(self.selecionar_cartao)
        self.lista_cartoes.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista_cartoes.customContextMenuRequested.connect(self.menu_cartao)

        self.left.addLayout(cartoes_box)

        self.left.addStretch()
        self.main_layout.addLayout(self.left, 0)

    # ==========================================================
    # ÁREA DE PAINEL
    # ==========================================================
    def _montar_area_painel(self):
        self.area_painel = QVBoxLayout()
        self.main_layout.addLayout(self.area_painel, 1)

    def _trocar_painel(self, painel):
        if self.painel_ativo:
            self.area_painel.removeWidget(self.painel_ativo)
            self.painel_ativo.deleteLater()

        self.painel_ativo = painel
        self.area_painel.addWidget(painel)

    # ==========================================================
    # SELEÇÃO
    # ==========================================================
    def selecionar_conta(self, item):

        self.lista_cartoes.clearSelection()

        conta = self.account_controller.get_account_by_id(item.data(Qt.UserRole))

        if not conta:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Conta não encontrada"),
            )
            return

        painel = PainelAccount(parent=self)
        painel.set_conta(conta)
        self._trocar_painel(painel)

    def selecionar_cartao(self, item):

        self.lista_contas.clearSelection()

        cartao = self.fatura_controller.buscar_cartao_por_id(item.data(Qt.UserRole))

        if not cartao:
            QMessageBox.warning(
                self,
                TranslatorApp.get("Erro"),
                TranslatorApp.get("Cartão não encontrado"),
            )
            return

        painel = PainelFatura(parent=self)
        painel.set_cartao(cartao)
        self._trocar_painel(painel)

    # ==========================================================
    # CARREGAMENTOS
    # ==========================================================
    def carregar_contas(self):

        self.lista_contas.clear()
        contas = self.account_controller.get_all_accounts()

        saldo_total = 0.0

        for conta in contas:

            saldo = float(conta.get("Saldo_Atual", 0))
            saldo_total += saldo

            tipo = TranslatorApp.get(conta.get("Tipo", ""))

            texto = (
                f"{conta.get('Nome_Conta')} ({tipo})\n"
                f"{TranslatorApp.get('Saldo')}: {CurrencyFormatter.format(saldo)}"
            )

            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, conta.get("ID_Conta"))
            self.lista_contas.addItem(item)

        self.lbl_saldo_total_contas.setText(
            f"{TranslatorApp.get('Saldo total')}: "
            f"{CurrencyFormatter.format(saldo_total)}"
        )

    def carregar_cartoes(self):

        self.lista_cartoes.clear()
        cartoes = self.fatura_controller.get_all_cartoes()

        for cartao in cartoes:
            texto = (
                f"{cartao.get('nome', 'Cartão')}\n"
                f"{TranslatorApp.get('Vencimento')}: "
                f"{cartao.get('dia_vencimento', '--')}"
            )

            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, cartao.get("ID_Cartao"))
            self.lista_cartoes.addItem(item)

    # ==========================================================
    # MENUS
    # ==========================================================
    def menu_conta(self, pos):

        menu = QMenu(self)

        menu.addAction(TranslatorApp.get("Ajustar saldo"), self._ajustar_saldo_conta)
        menu.addSeparator()
        menu.addAction(TranslatorApp.get("Editar"), self._editar_conta)
        menu.addAction(TranslatorApp.get("Copiar"), self._copiar_conta)
        menu.addSeparator()
        menu.addAction(TranslatorApp.get("Excluir"), self._excluir_conta)

        menu.exec_(self.lista_contas.mapToGlobal(pos))

    def menu_cartao(self, pos):

        menu = QMenu(self)

        menu.addAction(TranslatorApp.get("Copiar"), self._copiar_cartao)
        menu.addAction(TranslatorApp.get("Editar"), self._editar_cartao)
        menu.addSeparator()
        menu.addAction(TranslatorApp.get("Excluir"), self._excluir_cartao)

        menu.exec_(self.lista_cartoes.mapToGlobal(pos))

    # ==========================================================
    # AÇÕES
    # ==========================================================
    def _ajustar_saldo_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        conta = self.account_controller.get_account_by_id(item.data(Qt.UserRole))

        if conta:
            dialog = AjustarSaldoDialog(self, conta)
            if dialog.exec_():
                self.carregar_contas()

    def _editar_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        conta = self.account_controller.get_account_by_id(item.data(Qt.UserRole))

        if conta:
            dlg = EditarContaDialog(self, conta)
            if dlg.exec_():
                self.carregar_contas()

    def _editar_cartao(self):
        item = self.lista_cartoes.currentItem()
        if not item:
            return

        cartao = self.fatura_controller.buscar_cartao_por_id(item.data(Qt.UserRole))

        if cartao:
            dlg = EditCartaoDialog(self, cartao)
            if dlg.exec_():
                self.carregar_cartoes()

    def _copiar_conta(self):
        item = self.lista_contas.currentItem()
        if item:
            QApplication.clipboard().setText(item.text())

    def _copiar_cartao(self):
        item = self.lista_cartoes.currentItem()
        if item:
            QApplication.clipboard().setText(item.text())

    def _excluir_conta(self):

        item = self.lista_contas.currentItem()
        if not item:
            return

        confirm = QMessageBox.question(
            self,
            TranslatorApp.get("Excluir"),
            TranslatorApp.get("Deseja realmente excluir esta conta"),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            self.account_controller.delete_account(item.data(Qt.UserRole))
            self.carregar_contas()
            self._trocar_painel(QWidget())

    def _excluir_cartao(self):

        item = self.lista_cartoes.currentItem()
        if not item:
            return

        confirm = QMessageBox.question(
            self,
            TranslatorApp.get("Excluir"),
            TranslatorApp.get("Deseja realmente excluir este cartão"),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            self.fatura_controller.delete_cartao(item.data(Qt.UserRole))
            self.carregar_cartoes()
            self._trocar_painel(QWidget())

    # ==========================================================
    # CRIADORES
    # ==========================================================
    def criar_conta_dialog(self):
        dlg = CriarContaDialog(self)
        if dlg.exec_():
            self.carregar_contas()

    def criar_cartao_dialog(self):
        dlg = CriarCartaoDialog(self)
        if dlg.exec_():
            self.carregar_cartoes()

    # ==========================================================
    # UTIL
    # ==========================================================
    def _criar_lista_com_header(
        self, titulo, callback_novo, largura=220, altura_max=200
    ):

        container = QVBoxLayout()

        header = QHBoxLayout()

        label = QLabel(titulo)
        label.setStyleSheet("font-size: 15px; font-weight: bold;")

        btn = QPushButton("+")
        btn.setFixedSize(24, 24)
        btn.clicked.connect(callback_novo)

        header.addWidget(label)
        header.addStretch()
        header.addWidget(btn)

        lista = QListWidget()
        lista.setFixedWidth(largura)
        lista.setMaximumHeight(altura_max)

        container.addLayout(header)
        container.addWidget(lista)

        return container, lista, label
