import importlib
import logging
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QLabel, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from core.session import Session
from core.theme_manager import ThemeManager
from core.translator_app import TranslatorApp

from utilitarios.ion_path import IonPath

logger = logging.getLogger(__name__)


class MainView(QMainWindow):

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
        self.setWindowTitle("Controle Financeiro")

        self._init_ui()
        self._criar_menu()
        self.aplicar_tema()

        Session.on_tema_change(lambda _: self.aplicar_tema())

        self._abrir_primeira_view()

        TranslatorApp.enable_auto_translation(self)

    # ==================================================
    # UI BASE
    # ==================================================
    def _init_ui(self):

        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 15, 0, 15)
        self.sidebar_layout.setSpacing(4)

        main_layout.addWidget(self.sidebar, 1)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        main_layout.addWidget(self.content, 4)

    # ==================================================
    # UTIL
    # ==================================================
    def _is_admin(self):
        return (self.usuario.get("Nivel_Acesso") or "").lower() == "admin"

    def _icon(self, nome):
        if nome in self._icon_cache:
            return self._icon_cache[nome]

        try:
            path = IonPath.resource("assets", "icons", f"{nome}.svg")
            icon = QIcon(path) if os.path.exists(path) else QIcon()
            self._icon_cache[nome] = icon
            return icon

        except Exception:
            logger.exception(f"Erro ao carregar ícone: {nome}")
            return QIcon()

    # ==================================================
    # MENU PRINCIPAL
    # ==================================================
    def _criar_menu(self):

        def add_btn(texto, view_ref, icon_name):

            btn = QPushButton(texto)
            btn.setObjectName("menuButton")
            btn.setProperty("active", False)
            btn.setCursor(Qt.PointingHandCursor)

            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setContentsMargins(15, 8, 10, 8)

            btn.clicked.connect(
                lambda _, b=btn, v=view_ref: self._handle_menu_click(b, v)
            )

            self.sidebar_layout.addWidget(btn)
            self._menu_buttons.append((btn, view_ref))

        add_btn(
            "Resumo Financeiro",
            ("views.resumo_financeiro_view", "ResumoFinanceiroView"),
            "resumo"
        )
        add_btn(
            "Contas e Lançamentos",
            ("views.transacao_view", "TransacaoView"),
            "transacoes"
        )
        add_btn("Metas Financeiras", ("views.meta_view", "MetaView"), "metas")
        add_btn(
            "Lista de Categorias",
            ("views.lista_categorias_view", "ListaCategoriasView"),
            "categorias"
        )
        add_btn(
            "Relatórios",
            ("views.relatorio_view", "RelatorioView"),
            "relatorios"
        )
        add_btn(
            "Favorecidos",
            ("views.favorecido_view", "FavorecidoView"),
            "favorecidos"
        )
        add_btn(
            "Agendamentos",
            ("views.agendamento_view", "AgendamentoView"),
            "agendamentos"
        )

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

        nome = self.usuario.get("Nome") or "Usuário"

        self.lbl_usuario = QLabel(nome)
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

        def add_user_btn(texto, view_ref, icon_name):

            btn = QPushButton(texto)
            btn.setObjectName("menuButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(16, 16))
            btn.setContentsMargins(30, 8, 10, 8)

            btn.clicked.connect(lambda _, v=view_ref: self._carregar_view(v))

            self.user_menu_layout.addWidget(btn)
            self._user_menu_buttons.append((btn, view_ref))

        add_user_btn("Perfil", ("views.perfil_view", "PerfilView"), "perfil")

        if self._is_admin():
            add_user_btn(
                "Gerenciamento de Usuários",
                ("views.gerenciamento_usuarios_view", "GerenciamentoUsuariosView"),
                "gerenciar_usuarios"
            )

        add_user_btn(
            "Configurações",
            ("views.configuracoes_view", "ConfiguracoesView"),
            "configuracoes"
        )
        add_user_btn(
            "Backup e Restauração",
            ("views.backup_view", "BackupView"),
            "backup"
        )

    # ==================================================
    # TOGGLE MENU
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
        resolved_view = self._resolve_view_class(view_cls)

        if self._current_view_class == resolved_view:
            return

        self._ativar_botao(clicked_button)
        self._carregar_view(resolved_view)

    def _ativar_botao(self, clicked_button):

        for btn, _ in self._menu_buttons:
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if clicked_button:
            clicked_button.setProperty("active", True)
            clicked_button.style().unpolish(clicked_button)
            clicked_button.style().polish(clicked_button)

    def _resolve_view_class(self, view_ref):
        if isinstance(view_ref, tuple):
            module_name, class_name = view_ref
            module = importlib.import_module(module_name)
            return getattr(module, class_name)

        return view_ref

    # ==================================================
    # TROCA DE VIEW (CORRIGIDO)
    # ==================================================
    def _carregar_view(self, view_cls):

        try:
            view_cls = self._resolve_view_class(view_cls)

            if self._current_widget:

                if self._current_widget.parent() is not None:
                    self.content_layout.removeWidget(self._current_widget)

                self._current_widget.setParent(None)
                self._current_widget.deleteLater()
                self._current_widget = None

            view = view_cls(parent=self)

            if hasattr(view, "usuario"):
                view.usuario = self.usuario

            if hasattr(view, "logout_requested"):
                view.logout_requested.connect(self._logout)

            if hasattr(view, "on_load"):
                view.on_load()

            self.content_layout.addWidget(view)

            self._current_widget = view
            self._current_view_class = view_cls

        except Exception:
            view_name = getattr(view_cls, "__name__", str(view_cls))
            logger.exception(f"Erro ao carregar view {view_name}")

    # ==================================================
    # LOGOUT
    # ==================================================
    def _logout(self):

        self.close()

        try:
            from views.login_dialog import LoginDialog

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
            app = QApplication.instance()
            ThemeManager.aplicar_tema(tema, app)
        except Exception:
            logger.exception("Erro ao aplicar tema")
