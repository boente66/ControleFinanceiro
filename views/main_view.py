import logging
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from core.session import Session
from core.theme_manager import ThemeManager
from core.translator_app import TranslatorApp

from utilitarios.ion_path import IonPath

from views.transacao_view import TransacaoView
from views.agendamento_view import AgendamentoView
from views.favorecido_view import FavorecidoView
from views.relatorio_view import RelatorioView
from views.lista_categorias_view import ListaCategoriasView
from views.configuracoes_view import ConfiguracoesView
from views.backup_view import BackupView
from views.perfil_view import PerfilView
from views.gerenciamento_usuarios_view import GerenciamentoUsuariosView
from views.resumo_financeiro_view import ResumoFinanceiroView
from views.meta_view import MetaView
from views.login_dialog import LoginDialog


logger = logging.getLogger(__name__)


class MainView(QMainWindow):

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self, usuario_logado):
        super().__init__()

        Session.set_usuario(usuario_logado)
        self.usuario = usuario_logado or {}

        self._current_view_class = None
        self._current_widget = None
        self._menu_buttons = []
        self._user_menu_buttons = []
        self._user_menu_expanded = False

        self._icon_cache = {}

        self.setGeometry(100, 100, 1200, 800)

        # 🔥 título traduzível
        TranslatorApp.text(self, "Controle Financeiro")

        self._init_ui()
        self._criar_menu()
        self.aplicar_tema()

        Session.on_tema_change(lambda _: self.aplicar_tema())

        self._abrir_primeira_view()

    # ==================================================
    # UI BASE
    # ==================================================

    def _init_ui(self):

        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # SIDEBAR
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 15, 0, 15)
        self.sidebar_layout.setSpacing(4)

        main_layout.addWidget(self.sidebar, 1)

        # CONTENT
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        main_layout.addWidget(self.content, 4)

    # ==================================================
    # UTILIDADES
    # ==================================================

    def _is_admin(self):
        return (self.usuario.get("Nivel_Acesso") or "").lower() == "admin"

    def _icon(self, nome):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        try:
            path = IonPath.resource("assets", "icons", f"{nome}.svg")

            if not os.path.exists(path):
                logger.warning(f"[Ícone não encontrado] {path}")
                icon = QIcon()
            else:
                icon = QIcon(path)

            self._icon_cache[nome] = icon
            return icon

        except Exception:
            logger.exception(f"Erro ao carregar ícone: {nome}")
            return QIcon()

    # ==================================================
    # MENU PRINCIPAL
    # ==================================================

    def _criar_menu(self):

        def add_btn(texto_chave, view_cls, icon_name):

            btn = QPushButton()
            btn.setObjectName("menuButton")
            btn.setProperty("active", False)
            btn.setCursor(Qt.PointingHandCursor)

            # 🔥 tradução automática
            TranslatorApp.text(btn, texto_chave)

            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setContentsMargins(15, 8, 10, 8)

            btn.clicked.connect(
                lambda _, b=btn, v=view_cls: self._handle_menu_click(b, v)
            )

            self.sidebar_layout.addWidget(btn)
            self._menu_buttons.append((btn, view_cls))

        add_btn("Resumo Financeiro", ResumoFinanceiroView, "resumo")
        add_btn("Contas e Lançamentos", TransacaoView, "transacoes")
        add_btn("Metas Financeiras", MetaView, "metas")
        add_btn("Lista de Categorias", ListaCategoriasView, "categorias")
        add_btn("Relatórios", RelatorioView, "relatorios")
        add_btn("Favorecidos", FavorecidoView, "favorecidos")
        add_btn("Agendamentos", AgendamentoView, "agendamentos")

        self.sidebar_layout.addStretch()

        divisor = QFrame()
        divisor.setFrameShape(QFrame.HLine)
        divisor.setFrameShadow(QFrame.Sunken)
        self.sidebar_layout.addWidget(divisor)

        self._criar_bloco_usuario()

    # ==================================================
    # BLOCO USUÁRIO
    # ==================================================

    def _criar_bloco_usuario(self):

        self.lbl_usuario = QLabel(self.usuario.get("Nome", "Usuário"))
        self.lbl_usuario.setObjectName("sidebarUser")
        self.lbl_usuario.setAlignment(Qt.AlignLeft)
        self.lbl_usuario.setContentsMargins(15, 10, 10, 10)
        self.lbl_usuario.setCursor(Qt.PointingHandCursor)
        self.lbl_usuario.mousePressEvent = self._toggle_user_menu

        self.sidebar_layout.addWidget(self.lbl_usuario)

        self.user_menu_container = QWidget()
        self.user_menu_layout = QVBoxLayout(self.user_menu_container)
        self.user_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.user_menu_layout.setSpacing(2)
        self.user_menu_container.setVisible(False)

        self.sidebar_layout.addWidget(self.user_menu_container)

        self._criar_menu_usuario()

    # ==================================================
    # MENU USUÁRIO
    # ==================================================

    def _criar_menu_usuario(self):

        def add_user_btn(texto_chave, view_cls, icon_name):

            btn = QPushButton()
            btn.setObjectName("menuButton")
            btn.setCursor(Qt.PointingHandCursor)

            # 🔥 tradução automática
            TranslatorApp.text(btn, texto_chave)

            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(16, 16))
            btn.setContentsMargins(30, 8, 10, 8)

            btn.clicked.connect(lambda _, v=view_cls: self._carregar_view(v))

            self.user_menu_layout.addWidget(btn)
            self._user_menu_buttons.append(btn)

        add_user_btn("Perfil", PerfilView, "perfil")

        if self._is_admin():
            add_user_btn(
                "Gerenciamento de Usuários",
                GerenciamentoUsuariosView,
                "gerenciar_usuarios"
            )

        add_user_btn("Configurações", ConfiguracoesView, "configuracoes")
        add_user_btn("Backup e Restauração", BackupView, "backup")

    # ==================================================
    # TOGGLE MENU USUÁRIO
    # ==================================================

    def _toggle_user_menu(self, event=None):
        self._user_menu_expanded = not self._user_menu_expanded
        self.user_menu_container.setVisible(self._user_menu_expanded)

    # ==================================================
    # NAVEGAÇÃO
    # ==================================================

    def _abrir_primeira_view(self):
        if self._menu_buttons:
            btn, view_cls = self._menu_buttons[0]
            self._handle_menu_click(btn, view_cls)

    def _handle_menu_click(self, clicked_button, view_cls):

        if self._current_view_class == view_cls:
            return

        self._ativar_botao(clicked_button)
        self._carregar_view(view_cls)

    def _ativar_botao(self, clicked_button):

        for btn, _ in self._menu_buttons:
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        clicked_button.setProperty("active", True)
        clicked_button.style().unpolish(clicked_button)
        clicked_button.style().polish(clicked_button)

    def _carregar_view(self, view_cls):

        if self._current_widget:
            self.content_layout.removeWidget(self._current_widget)
            self._current_widget.setParent(None)
            self._current_widget.deleteLater()
            self._current_widget = None

        try:
            view = view_cls(parent=self)
        except TypeError:
            view = view_cls(parent=self, usuario=self.usuario)

        if hasattr(view, "logout_requested"):
            view.logout_requested.connect(self._logout)

        self.content_layout.addWidget(view)

        self._current_view_class = view_cls
        self._current_widget = view

        logger.info(f"View carregada: {view_cls.__name__}")

    # ==================================================
    # LOGOUT
    # ==================================================

    def _logout(self):

        self.close()

        try:
            login = LoginDialog()
            if login.exec_() == QDialog.Accepted:
                nova_main = MainView(login.usuario_logado)
                nova_main.show()
        except Exception:
            logger.exception("Erro ao realizar logout")

    # ==================================================
    # TEMA
    # ==================================================

    def aplicar_tema(self):
        try:
            tema = Session.get_config("tema", "Claro")
            ThemeManager.aplicar_tema(tema)
        except Exception:
            logger.exception("Erro ao aplicar tema")