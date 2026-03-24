import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem,
    QLabel, QPushButton, QMenu,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt


from core.i18n import t

from controllers.account_controller import AccountController
from controllers.fatura_controller import FaturaController

from core.session import Session
from views.criar_conta_dialog import CriarContaDialog
from views.editar_conta_dialog import EditarContaDialog
from views.criar_cartao_dialog import CriarCartaoDialog, EditCartaoDialog
from views.ajustar_saldo_dialog import AjustarSaldoDialog

from views.painel_account import PainelAccount
from views.painel_fatura import PainelFatura

from utilitarios.currency_formatter import CurrencyFormatter

logger = logging.getLogger(__name__)


class TransacaoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
    

        self.account_controller = AccountController()
        self.fatura_controller = FaturaController()

        self.painel_ativo = None

        self.main_layout = QHBoxLayout(self)

        self._montar_painel_esquerdo()
        self._montar_area_painel()

        self.carregar_contas()
        self.carregar_cartoes()

        Session.on_idioma_change(self._retranslate)
        self._retranslate(Session.get_config("idioma", "Português"))

    # ==========================================================
    # PAINEL ESQUERDO
    # ==========================================================
    def _montar_painel_esquerdo(self):

        self.left = QVBoxLayout()
        self.left.setSpacing(10)

        idioma = Session.get_config("idioma", "Português")

        contas_box, self.lista_contas = self._criar_lista_com_header(
            t("Contas e Poupanças", idioma),
            self.criar_conta_dialog,
            altura_max=220
        )

        self.lista_contas.itemClicked.connect(self.selecionar_conta)
        self.lista_contas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista_contas.customContextMenuRequested.connect(self.menu_conta)

        self.lbl_saldo_total_contas = QLabel()
        self.lbl_saldo_total_contas.setAlignment(Qt.AlignRight)
        self.lbl_saldo_total_contas.setObjectName("muted")

        contas_box.addWidget(self.lbl_saldo_total_contas)
        self.left.addLayout(contas_box)

        cartoes_box, self.lista_cartoes = self._criar_lista_com_header(
            t("Cartões de Crédito", idioma),
            self.criar_cartao_dialog,
            altura_max=160
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
            self.painel_ativo.setParent(None)
            self.painel_ativo.deleteLater()

        self.painel_ativo = painel
        self.area_painel.addWidget(painel)

    # ==========================================================
    # SELEÇÃO
    # ==========================================================
    def selecionar_conta(self, item):

        self.lista_cartoes.clearSelection()

        conta = self.account_controller.get_account_by_id(
            item.data(Qt.UserRole)
        )

        if not conta:
            QMessageBox.warning(self, "Erro", "Conta não encontrada")
            return

        painel = PainelAccount(parent=self)
        painel.set_conta(conta)
        self._trocar_painel(painel)

    def selecionar_cartao(self, item):

        self.lista_contas.clearSelection()

        cartao = self.fatura_controller.buscar_cartao_por_id(
            item.data(Qt.UserRole)
        )

        if not cartao:
            QMessageBox.warning(self, "Erro", "Cartão não encontrado")
            return

        painel = PainelFatura(parent=self)
        painel.set_cartao(cartao)
        self._trocar_painel(painel)

    # ==========================================================
    # CARREGAMENTOS
    # ==========================================================
    def carregar_contas(self):

        idioma = Session.get_config("idioma", "Português")

        self.lista_contas.clear()
        contas = self.account_controller.get_all_accounts()

        saldo_total = 0.0

        for conta in contas:

            saldo = float(conta.get("Saldo_Atual", 0))
            saldo_total += saldo

            texto = (
                f"{conta.get('Nome_Conta')} ({conta.get('Tipo')})\n"
                f"{t('Saldo', idioma)}: {CurrencyFormatter.format(saldo)}"
            )

            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, conta.get("ID_Conta"))
            self.lista_contas.addItem(item)

        self.lbl_saldo_total_contas.setText(
            f"{t('Saldo total', idioma)}: "
            f"{CurrencyFormatter.format(saldo_total)}"
        )

    def carregar_cartoes(self):

        idioma = Session.get_config("idioma", "Português")

        self.lista_cartoes.clear()
        cartoes = self.fatura_controller.get_all_cartoes() 

        for cartao in cartoes:
            texto = (
                f"{cartao.get('nome', 'Cartão')}\n"
                f"{t('Vencimento', idioma)}: "
                f"{cartao.get('dia_vencimento', '--')}"
            )

            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, cartao.get("ID_Cartao"))
            self.lista_cartoes.addItem(item)

    # ==========================================================
    # MENUS
    # ==========================================================
    def menu_conta(self, pos):
        idioma = Session.get_config("idioma", "Português")

        menu = QMenu(self)
        menu.addAction(t("Ajustar saldo", idioma), self._ajustar_saldo_conta)
        menu.addSeparator()
        menu.addAction(t("Editar", idioma), self.editar_conta)
        menu.addAction(t("Copiar", idioma), self._copiar_conta)
        menu.addSeparator()
        menu.addAction(t("Excluir", idioma), self._excluir_conta)

        menu.exec_(self.lista_contas.mapToGlobal(pos))

    def menu_cartao(self, pos):
        idioma = Session.get_config("idioma", "Português")

        menu = QMenu(self)
        menu.addAction(t("Copiar", idioma), self._copiar_cartao)
        menu.addAction(t("Editar", idioma), self.editar_cartao)
        menu.addSeparator()
        menu.addAction(t("Excluir", idioma), self._excluir_cartao)

        menu.exec_(self.lista_cartoes.mapToGlobal(pos))

     # ========================================================
     # COPIADORES E AJUSTADORES
     # ========================================================
    def _copiar_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        conta_id = item.data(Qt.UserRole)
        conta = self.account_controller.get_account_by_id(conta_id)

        if conta:
            # Lógica para copiar a conta
            pass

    def _copiar_cartao(self):
        item = self.lista_cartoes.currentItem()
        if not item:
            return

        cartao_id = item.data(Qt.UserRole)
        cartao = self.fatura_controller.get_cartao_by_id(cartao_id, self.usuario_id)

        if cartao:
            try:
                idioma = Session.get_config("idioma", "Português")

                # Tenta carregar o cartão (compatível com nomes de método diferentes)
                cartao = None
                uid = getattr(self, "usuario_id", None)
                if uid is None and hasattr(Session, "get_user_id"):
                    try:
                        uid = Session.get_user_id()
                    except Exception:
                        uid = None

                # Preferir métodos já vistos no projeto, com fallback
                if hasattr(self.fatura_controller, "get_cartao_by_id"):
                    try:
                        cartao = self.fatura_controller.get_cartao_by_id(cartao_id, uid)
                    except TypeError:
                        cartao = self.fatura_controller.get_cartao_by_id(cartao_id)
                if not cartao and hasattr(self.fatura_controller, "buscar_cartao_por_id"):
                    cartao = self.fatura_controller.buscar_cartao_por_id(cartao_id)

                if not cartao:
                    QMessageBox.warning(self, t("Erro", idioma), t("Cartão não encontrado", idioma))
                    return

                # Criar cópia do dicionário/objeto do cartão
                if isinstance(cartao, dict):
                    novo = cartao.copy()
                else:
                    try:
                        novo = dict(cartao)
                    except Exception:
                        try:
                            novo = vars(cartao).copy()
                        except Exception:
                            novo = {}

                # Remover identificadores para forçar criação de novo registro
                for key in list(novo.keys()):
                    if key.lower().startswith("id"):
                        novo.pop(key, None)

                # Ajustar nome para indicar que é uma cópia
                name_key = None
                for k in ("nome", "Nome", "name", "nome_cartao", "Nome_Cartao"):
                    if k in novo:
                        name_key = k
                        break
                if name_key:
                    novo[name_key] = f"{novo.get(name_key)} (cópia)"

                # Tenta vários nomes de método para salvar/criar cartão no controller
                created = False
                for fn in ("create_cartao", "add_cartao", "salvar_cartao", "insert_cartao"):
                    if hasattr(self.fatura_controller, fn):
                        func = getattr(self.fatura_controller, fn)
                        try:
                            # tentar enviar uid se disponível
                            if uid is not None:
                                try:
                                    result = func(novo, uid)
                                except TypeError:
                                    result = func(novo)
                            else:
                                result = func(novo)
                            created = bool(result) if result is not None else True
                        except Exception as e:
                            logger.debug(f"Tentativa {fn} falhou: {e}")
                        break

                if not created:
                    QMessageBox.warning(
                        self,
                        t("Erro", idioma),
                        t("Não foi possível criar a cópia do cartão. Verifique o controller.", idioma)
                    )
                    return

                QMessageBox.information(
                    self,
                    t("Concluído", idioma),
                    t("Cartão copiado com sucesso.", idioma)
                )
                self.carregar_cartoes()

            except Exception as e:
                logger.error(f"Erro ao copiar cartão: {e}")
                QMessageBox.critical(self, t("Erro", idioma), t("Ocorreu um erro ao copiar o cartão.", idioma))
            pass

    def _ajustar_saldo_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        conta_id = item.data(Qt.UserRole)
        conta = self.account_controller.get_account_by_id(conta_id)

        if conta:
            dialog = AjustarSaldoDialog(self, conta)
            if dialog.exec_():
                self.carregar_contas()

    # ==========================================================
    # EDITORES
    # ==========================================================
    def _editar_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        conta_id = item.data(Qt.UserRole)
        conta = self.account_controller.get_account_by_id(conta_id)

        if conta:
            editar = EditarContaDialog(self, conta)
            if editar.exec_():
                self.carregar_contas()
            pass

    def _editar_cartao(self):
        item = self.lista_cartoes.currentItem()
        if not item:
            return

        cartao_id = item.data(Qt.UserRole)
        cartao = self.fatura_controller.buscar_cartao_por_id(cartao_id)

        if cartao:
            editar = EditCartaoDialog(self, cartao)
            if editar.exec_():
                self.carregar_cartoes()
            pass

    # ==========================================================
    # EXCLUSÕES
    # ==========================================================
    def _excluir_conta(self):
        item = self.lista_contas.currentItem()
        if not item:
            return

        idioma = Session.get_config("idioma", "Português")

        confirmar = QMessageBox.question(
            self,
            t("Excluir", idioma),
            t("Deseja realmente excluir esta conta?", idioma),
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            conta_id = item.data(Qt.UserRole)
            self.account_controller.delete_account(conta_id)
            self.carregar_contas()
            self._trocar_painel(QWidget())

    def _excluir_cartao(self):
        item = self.lista_cartoes.currentItem()
        if not item:
            return

        idioma = Session.get_config("idioma", "Português")

        confirmar = QMessageBox.question(
            self,
            t("Excluir", idioma),
            t("Deseja realmente excluir este cartão?", idioma),
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            cartao_id = item.data(Qt.UserRole)
            self.fatura_controller.delete_cartao(cartao_id, self.usuario_id)
            self.carregar_cartoes()
            self._trocar_painel(QWidget())

    # ==========================================================
    # I18N
    # ==========================================================
    def _retranslate(self, idioma):
        self.setWindowTitle(t("Transações", idioma))
        self.carregar_contas()
        self.carregar_cartoes()

    # ==========================================================
    # CRIADORES
    # ==========================================================
    def criar_conta_dialog(self):
        try:
            dlg = CriarContaDialog(self)
            if dlg.exec_():
                self.carregar_contas()
        except Exception as e:
            logger.error(f"Erro ao criar conta: {e}")

    def criar_cartao_dialog(self):
        try:
            dlg = CriarCartaoDialog(self)
            if dlg.exec_():
                self.carregar_cartoes()
        except Exception as e:
            logger.error(f"Erro ao criar cartão: {e}")

    # ==========================================================
    # UTIL
    # ==========================================================
    def _criar_lista_com_header(self, titulo, callback_novo, largura=220, altura_max=200):
        container = QVBoxLayout()
        container.setSpacing(6)

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

        return container, lista