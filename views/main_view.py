from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os

from core.session import Session
from core.i18n import t
from core.theme_manager import ThemeManager

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


class MainView(QMainWindow):

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self, usuario_logado):
        super().__init__()

        Session.set_usuario(usuario_logado)
        self.usuario = usuario_logado

        self._current_view_class = None
        self._current_widget = None
        self._menu_buttons = []
        self._user_menu_buttons = []
        self._user_menu_expanded = False

        self.setWindowTitle("Controle Financeiro")
        self.setGeometry(100, 100, 1200, 800)

        self._init_ui()
        self._criar_menu()
        self.aplicar_tema()

        Session.on_idioma_change(self._retranslate_menu)
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

        main_layout.addWidget(self.content, 4)

    # ==================================================
    # UTILIDADES
    # ==================================================

    def _is_admin(self):
        return self.usuario.get("Nivel_Acesso", "").lower() == "admin"

    def _icon(self, nome):
        """
        Retorna QIcon com validação segura.
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_path, ".."))
        icon_path = os.path.join(project_root, "assets", "icons", f"{nome}.svg")

        if not os.path.exists(icon_path):
            print(f"[Ícone não encontrado] {icon_path}")
            return QIcon()

        return QIcon(icon_path)

    # ==================================================
    # MENU PRINCIPAL
    # ==================================================

    def _criar_menu(self):

        idioma = Session.get_config("idioma", "Português")

        def add_btn(texto_chave, view_cls, icon_name):

            btn = QPushButton(t(texto_chave, idioma))
            btn.setObjectName("menuButton")
            btn.setProperty("active", False)
            btn.setCursor(Qt.PointingHandCursor)

            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setContentsMargins(15, 8, 10, 8)

            btn.clicked.connect(
                lambda _, b=btn, v=view_cls: self._handle_menu_click(b, v)
            )

            self.sidebar_layout.addWidget(btn)
            self._menu_buttons.append((btn, texto_chave, view_cls))

        # BLOCO PRINCIPAL
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

        idioma = Session.get_config("idioma", "Português")

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

        idioma = Session.get_config("idioma", "Português")

        def add_user_btn(texto_chave, view_cls, icon_name):

            btn = QPushButton(t(texto_chave, idioma))
            btn.setObjectName("menuButton")
            btn.setCursor(Qt.PointingHandCursor)

            btn.setIcon(self._icon(icon_name))
            btn.setIconSize(QSize(16, 16))
            btn.setContentsMargins(30, 8, 10, 8)

            btn.clicked.connect(lambda _, v=view_cls: self._carregar_view(v))

            self.user_menu_layout.addWidget(btn)
            self._user_menu_buttons.append((btn, texto_chave))

        add_user_btn("Perfil", PerfilView, "perfil")

        if self._is_admin():
            add_user_btn("Gerenciamento de Usuários",
                         GerenciamentoUsuariosView,
                         "gerenciar_usuarios")

        add_user_btn("Configurações", ConfiguracoesView, "configuracoes")
        add_user_btn("Backup e Restauração", BackupView, "backup")

    # ==================================================
    # TOGGLE MENU USUÁRIO
    # ==================================================

    def _toggle_user_menu(self, event):
        self._user_menu_expanded = not self._user_menu_expanded
        self.user_menu_container.setVisible(self._user_menu_expanded)

    # ==================================================
    # NAVEGAÇÃO
    # ==================================================

    def _abrir_primeira_view(self):
        if self._menu_buttons:
            btn, _, view_cls = self._menu_buttons[0]
            self._handle_menu_click(btn, view_cls)

    def _handle_menu_click(self, clicked_button, view_cls):

        if self._current_view_class == view_cls:
            return

        self._ativar_botao(clicked_button)
        self._carregar_view(view_cls)

    def _ativar_botao(self, clicked_button):

        for btn, _, _ in self._menu_buttons:
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        clicked_button.setProperty("active", True)
        clicked_button.style().unpolish(clicked_button)
        clicked_button.style().polish(clicked_button)

    def _carregar_view(self, view_cls):

        if self._current_widget:
            self.content_layout.removeWidget(self._current_widget)
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

    # ==================================================
    # IDIOMA
    # ==================================================

    def _retranslate_menu(self, idioma):

        for btn, texto_chave, _ in self._menu_buttons:
            btn.setText(t(texto_chave, idioma))

        for btn, texto_chave in self._user_menu_buttons:
            btn.setText(t(texto_chave, idioma))

    # ==================================================
    # LOGOUT
    # ==================================================

    def _logout(self):

        self.close()

        login = LoginDialog()
        if login.exec_() == QDialog.Accepted:
            nova_main = MainView(login.usuario_logado)
            nova_main.show()

    # ==================================================
    # TEMA
    # ==================================================

    def aplicar_tema(self):
        tema = Session.get_config("tema", "Claro")
        ThemeManager.aplicar_tema(tema)