import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt

from controllers.meta_controller import MetaController
from views.meta_dialog import MetaDialog

from utilitarios.currency_formatter import CurrencyFormatter
from core.translator_app import TranslatorApp
from core.translator_binding import TranslatorBinding

logger = logging.getLogger(__name__)


class MetaView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = MetaController()

        # 🔥 título base
        self.setWindowTitle("Metas Financeiras")

        self._init_ui()
        self.carregar_metas()

        # 🔥 reatividade SOMENTE para recarregar dados
        TranslatorBinding.bind(self._on_translate)

    # ==================================================
    # REATIVIDADE
    # ==================================================
    def _on_translate(self, *_):
        self.carregar_metas()

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

        # limpa layout
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        metas = self.controller.listar_metas_ativas()

        if not metas:
            label = QLabel(TranslatorApp.get("Nenhuma meta cadastrada"))
            self.container_layout.addWidget(label)
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

        restante_label = QLabel(
            f"{TranslatorApp.get('Restante')}: "
            f"{CurrencyFormatter.format(progresso['restante'])}"
        )
        layout.addWidget(restante_label)

        percentual = progresso["percentual"]

        if percentual >= 100:
            nome.setObjectName("positivo")
        elif percentual >= 80:
            nome.setObjectName("warning")
        else:
            nome.setObjectName("negativo")

        nome.style().unpolish(nome)
        nome.style().polish(nome)

        botoes_layout = QHBoxLayout()

        btn_concluir = QPushButton(TranslatorApp.get("Concluir"))
        btn_concluir.clicked.connect(
            lambda: self._concluir(meta["ID_Meta"])
        )

        btn_excluir = QPushButton(TranslatorApp.get("Excluir"))
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