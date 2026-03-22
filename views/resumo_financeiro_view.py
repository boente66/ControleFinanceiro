import logging
import traceback
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controllers.account_controller import AccountController
from controllers.schedule_controller import ScheduleController
from controllers.transaction_controller import TransactionController
from controllers.fatura_controller import FaturaController
from controllers.meta_controller import MetaController

from core.session import Session
from core.i18n import t

from utilitarios.currency_formatter import CurrencyFormatter
from utilitarios.date_formatter import DateFormatter

logger = logging.getLogger(__name__)


class ResumoFinanceiroView(QWidget):
    """
    Painel de Resumo Financeiro
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        if not Session.get_usuario():
            raise RuntimeError("Usuário não autenticado")

        # Controllers
        self.account_controller = AccountController()
        self.schedule_controller = ScheduleController()
        self.transaction_controller = TransactionController()
        self.fatura_controller = FaturaController()
        self.meta_controller = MetaController()

        self._init_ui()
        self.load_data()

        Session.on_idioma_change(self._retranslate)

    # ==================================================
    # UTIL
    # ==================================================
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def format_currency(self, value):
        try:
            return CurrencyFormatter.format(float(value))
        except Exception:
            return CurrencyFormatter.format(0)

    # ==================================================
    # UI
    # ==================================================
    def _init_ui(self):

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("pageTitle")
        self.main_layout.addWidget(self.title)

        # ---------- TOP ----------
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        self.contas_group = QGroupBox()
        self.contas_layout = QVBoxLayout(self.contas_group)
        top_layout.addWidget(self.contas_group)

        self.cartoes_group = QGroupBox()
        self.cartoes_layout = QVBoxLayout(self.cartoes_group)
        top_layout.addWidget(self.cartoes_group)

        self.lancamentos_group = QGroupBox()
        self.lancamentos_layout = QVBoxLayout(self.lancamentos_group)
        top_layout.addWidget(self.lancamentos_group)

        self.main_layout.addLayout(top_layout)

        # ---------- BOTTOM ----------
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        self.receitas_group = QGroupBox()
        self.receitas_layout = QVBoxLayout(self.receitas_group)
        bottom_layout.addWidget(self.receitas_group)

        self.analise_group = QGroupBox()
        self.analise_layout = QVBoxLayout(self.analise_group)
        bottom_layout.addWidget(self.analise_group)

        self.metas_group = QGroupBox()
        self.metas_layout = QVBoxLayout(self.metas_group)
        bottom_layout.addWidget(self.metas_group)

        self.main_layout.addLayout(bottom_layout)

        self._retranslate(Session.get_config("idioma", "Português"))

    # ==================================================
    # TRADUÇÃO
    # ==================================================
    def _retranslate(self, idioma):

        self.title.setText(t("Resumo Financeiro", idioma))
        self.contas_group.setTitle(t("Saldos das Contas", idioma))
        self.cartoes_group.setTitle(t("Cartões de Crédito", idioma))
        self.lancamentos_group.setTitle(t("Próximos Lançamentos Agendados", idioma))
        self.receitas_group.setTitle(t("Receitas e Despesas do Mês", idioma))
        self.analise_group.setTitle(t("Análise do Mês", idioma))
        self.metas_group.setTitle(t("Metas Financeiras", idioma))

        self.load_data()

    # ==================================================
    # LOAD DATA
    # ==================================================
    def load_data(self):
        try:
            self.load_accounts()
            self.load_credit_cards()
            self.load_scheduled_transactions()
            self.load_monthly_summary()
            self.load_monthly_analysis()
            self.load_metas()  # ✅ agora corretamente chamado
        except Exception as e:
            logger.error(f"Erro ao carregar resumo financeiro: {e}")
            traceback.print_exc()

    # ==================================================
    # CONTAS
    # ==================================================
    def load_accounts(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.contas_layout)

        try:
            accounts = self.account_controller.get_all_accounts()

            if not accounts:
                self.contas_layout.addWidget(
                    QLabel(t("Nenhuma conta encontrada.", idioma))
                )
                return

            for acc in accounts:
                nome = acc.get("Nome_Conta", "Conta")
                tipo = acc.get("Tipo", "")
                saldo = float(acc.get("Saldo_Atual", 0))

                label = QLabel(
                    f"{nome} ({tipo})\n{self.format_currency(saldo)}"
                )
                label.setObjectName("negativo" if saldo < 0 else "positivo")
                self.contas_layout.addWidget(label)

        except Exception:
            self.contas_layout.addWidget(
                QLabel(t("Erro ao carregar contas.", idioma))
            )

    # ==================================================
    # CARTÕES
    # ==================================================
    def load_credit_cards(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.cartoes_layout)

        try:
            cards = self.fatura_controller.get_all_cartoes()

            if not cards:
                self.cartoes_layout.addWidget(
                    QLabel(t("Nenhum cartão encontrado.", idioma))
                )
                return

            hoje = datetime.today()

            for card in cards:
                nome = card.get("Nome", "Cartão")
                dia_vencimento = int(card.get("Dia_Vencimento", 1))

                vencimento = datetime(hoje.year, hoje.month, dia_vencimento)
                if vencimento < hoje:
                    if hoje.month == 12:
                        vencimento = datetime(hoje.year + 1, 1, dia_vencimento)
                    else:
                        vencimento = datetime(hoje.year, hoje.month + 1, dia_vencimento)

                dias_restantes = (vencimento - hoje).days

                fatura = self.fatura_controller.obter_valor_fatura_atual(card["ID_Cartao"])
                disponivel = self.fatura_controller.obter_limite_disponivel(card["ID_Cartao"])

                texto = QLabel(
                    f"{nome}\n"
                    f"{t('Fatura Atual', idioma)}: {self.format_currency(fatura)}\n"
                    f"{t('Vencimento', idioma)}: {vencimento.strftime('%d/%m')}\n"
                    f"{t('Disponível', idioma)}: {self.format_currency(disponivel)}"
                )

                if dias_restantes <= 3:
                    texto.setObjectName("negativo")
                elif dias_restantes <= 7:
                    texto.setObjectName("warning")
                else:
                    texto.setObjectName("positivo")

                self.cartoes_layout.addWidget(texto)

        except Exception:
            self.cartoes_layout.addWidget(
                QLabel(t("Erro ao carregar cartões.", idioma))
            )

    # ==================================================
    # AGENDAMENTOS
    # ==================================================
    def load_scheduled_transactions(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.lancamentos_layout)

        try:
            scheduled = self.schedule_controller.get_upcoming_schedules()

            if not scheduled:
                self.lancamentos_layout.addWidget(
                    QLabel(t("Nenhum lançamento agendado.", idioma))
                )
                return

            for item in scheduled:
                data = DateFormatter.iso_to_br(item.get("Data"))
                desc = item.get("Descricao", "")
                valor = float(item.get("Valor", 0))

                label = QLabel(
                    f"{data} - {desc}\n{self.format_currency(valor)}"
                )
                label.setObjectName("negativo" if valor < 0 else "positivo")
                self.lancamentos_layout.addWidget(label)

        except Exception:
            self.lancamentos_layout.addWidget(
                QLabel(t("Erro ao carregar agendamentos.", idioma))
            )

    # ==================================================
    # GRÁFICO
    # ==================================================
    def load_monthly_summary(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.receitas_layout)

        try:
            dados = self.transaction_controller.get_resumo_mes_atual()

            receitas = float(dados.get("Receitas", 0))
            despesas = abs(float(dados.get("Despesas", 0)))

            fig = Figure(figsize=(4, 3))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            ax.bar(
                [t("Receitas", idioma), t("Despesas", idioma)],
                [receitas, despesas],
                color=["#16a34a", "#dc2626"]
            )

            ax.set_title(t("Resumo Mensal", idioma))
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            fig.tight_layout()

            self.receitas_layout.addWidget(canvas)

        except Exception:
            self.receitas_layout.addWidget(
                QLabel(t("Erro ao gerar gráfico.", idioma))
            )

    # ==================================================
    # ANÁLISE
    # ==================================================
    def load_monthly_analysis(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.analise_layout)

        try:
            analise = self.transaction_controller.get_analise_mensal()

            if not analise:
                self.analise_layout.addWidget(
                    QLabel(t("Sem análise disponível.", idioma))
                )
                return

            saldo_atual = float(analise.get("Saldo_Atual", 0))
            receitas = float(analise.get("Receitas", 0))
            despesas = float(analise.get("Despesas", 0))
            balanco = saldo_atual + receitas - despesas

            for texto, valor in [
                (t("Saldo atual", idioma), saldo_atual),
                (t("Receitas do mês", idioma), receitas),
                (t("Despesas do mês", idioma), despesas),
                (t("Balanço do mês", idioma), balanco),
            ]:
                label = QLabel(f"{texto}\n{self.format_currency(valor)}")
                label.setObjectName("positivo" if valor >= 0 else "negativo")
                self.analise_layout.addWidget(label)

        except Exception:
            self.analise_layout.addWidget(
                QLabel(t("Erro ao carregar análise mensal.", idioma))
            )

    # ==================================================
    # METAS
    # ==================================================
    def load_metas(self):

        idioma = Session.get_config("idioma", "Português")
        self.clear_layout(self.metas_layout)

        try:
            metas = self.meta_controller.listar_metas_ativas()

            if not metas:
                self.metas_layout.addWidget(
                    QLabel(t("Nenhuma meta ativa.", idioma))
                )
                return

            for meta in metas:

                nome = QLabel(meta["Nome"])
                progresso = meta["Progresso"]

                barra = QProgressBar()
                barra.setValue(int(progresso["percentual"]))

                valor = QLabel(
                    f"{CurrencyFormatter.format(progresso['valor_atual'])} / "
                    f"{CurrencyFormatter.format(progresso['valor_alvo'])}"
                )

                if progresso["percentual"] >= 100:
                    nome.setObjectName("positivo")
                elif progresso["percentual"] >= 70:
                    nome.setObjectName("warning")
                else:
                    nome.setObjectName("negativo")

                self.metas_layout.addWidget(nome)
                self.metas_layout.addWidget(valor)
                self.metas_layout.addWidget(barra)

        except Exception:
            self.metas_layout.addWidget(
                QLabel(t("Erro ao carregar metas.", idioma))
            )