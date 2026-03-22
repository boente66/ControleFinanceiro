import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QProgressBar,
    QMessageBox
)
from PyQt5.QtCore import Qt

from controllers.meta_controller import MetaController
from views.meta_dialog import MetaDialog  # 🔥 IMPORT NECESSÁRIO
from core.i18n import t
from core.session import Session
from utilitarios.currency_formatter import CurrencyFormatter

logger = logging.getLogger(__name__)


class MetaView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = MetaController()

        self._init_ui()
        self.carregar_metas()

        Session.on_idioma_change(self._retranslate)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        self.layout_principal = QVBoxLayout(self)

        self.titulo = QLabel("Metas Financeiras")
        self.titulo.setObjectName("pageTitle")
        self.titulo.setAlignment(Qt.AlignCenter)

        self.layout_principal.addWidget(self.titulo)

        self.btn_nova = QPushButton("Nova Meta")
        self.btn_nova.setObjectName("addButton")
        self.btn_nova.clicked.connect(self._nova_meta)

        self.layout_principal.addWidget(self.btn_nova)

        # Área scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.scroll.setWidget(self.container)
        self.layout_principal.addWidget(self.scroll)

        self.layout_principal.addStretch()

    # ==================================================
    # CARREGAR METAS
    # ==================================================
    def carregar_metas(self):

        # Limpar layout
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        metas = self.controller.listar_metas_ativas()

        if not metas:
            self.container_layout.addWidget(
                QLabel("Nenhuma meta cadastrada.")
            )
            self.container_layout.addStretch()
            return

        for meta in metas:
            card = self._criar_card(meta)
            self.container_layout.addWidget(card)

        self.container_layout.addStretch()

    # ==================================================
    # CARD
    # ==================================================
    def _criar_card(self, meta):

        frame = QFrame()
        frame.setObjectName("metaCard")
        frame.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(frame)

        nome = QLabel(meta["Nome"])
        nome.setObjectName("title")
        layout.addWidget(nome)

        progresso = meta["Progresso"]

        valor_texto = QLabel(
            f"{CurrencyFormatter.format(progresso['valor_atual'])} / "
            f"{CurrencyFormatter.format(progresso['valor_alvo'])}"
        )
        layout.addWidget(valor_texto)

        progress_bar = QProgressBar()
        progress_bar.setValue(min(int(progresso["percentual"]), 100))
        layout.addWidget(progress_bar)

        restante = QLabel(
            f"Restante: {CurrencyFormatter.format(progresso['restante'])}"
        )
        layout.addWidget(restante)

        # 🎯 Status visual
        percentual = progresso["percentual"]

        if percentual >= 100:
            nome.setObjectName("positivo")
        elif percentual >= 80:
            nome.setObjectName("warning")
        else:
            nome.setObjectName("negativo")

        nome.style().unpolish(nome)
        nome.style().polish(nome)

        # Botões
        botoes_layout = QHBoxLayout()

        btn_concluir = QPushButton("Concluir")
        btn_concluir.clicked.connect(
            lambda: self._concluir(meta["ID_Meta"])
        )

        btn_excluir = QPushButton("Excluir")
        btn_excluir.setObjectName("deleteButton")
        btn_excluir.clicked.connect(
            lambda: self._excluir(meta["ID_Meta"])
        )

        botoes_layout.addWidget(btn_concluir)
        botoes_layout.addWidget(btn_excluir)

        layout.addLayout(botoes_layout)

        return frame

    # ==================================================
    # AÇÕES
    # ==================================================
    def _nova_meta(self):

        dialog = MetaDialog(self)

        if dialog.exec_() == dialog.Accepted:
            self.carregar_metas()

    def _concluir(self, id_meta):

        self.controller.concluir_meta(id_meta)
        self.carregar_metas()

    def _excluir(self, id_meta):

        self.controller.excluir_meta(id_meta)
        self.carregar_metas()

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _retranslate(self, idioma):

        self.titulo.setText(t("Metas Financeiras", idioma))
        self.btn_nova.setText(t("Nova Meta", idioma))
        self.carregar_metas()