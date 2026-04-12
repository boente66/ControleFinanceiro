import logging
from datetime import datetime

from core.session import Session
from services.fatura_service import FaturaService

logger = logging.getLogger(__name__)


class FaturaController:

    def __init__(self):
        self.service = FaturaService()

    # ==================================================
    # USUÁRIO
    # ==================================================
    def get_id_usuario(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")
        return usuario["ID_Usuario"]

    # ==================================================
    # FATURA (LISTAGEM)
    # ==================================================
    def listar_lancamentos_fatura(self, id_cartao, mes, ano):
        id_usuario = self.get_id_usuario()
        return self.service.obter_fatura(
            id_cartao, mes, ano, id_usuario
        )

    def obter_fatura_paginada(self, id_cartao, mes, ano, limit=50, offset=0):
        id_usuario = self.get_id_usuario()
        return self.service.obter_fatura_paginada(
            id_cartao, mes, ano, id_usuario, limit, offset
        )

    # ==================================================
    # REGISTRAR DESPESA
    # ==================================================
    def registrar_despesa_cartao(self, dados: dict) -> bool:
        id_usuario = self.get_id_usuario()
        self.service.registrar_despesa_cartao(dados, id_usuario)
        return True

    # ==================================================
    # PAGAMENTO
    # ==================================================
    def pagar_fatura(self, id_cartao, id_conta, mes, ano) -> bool:
        id_usuario = self.get_id_usuario()
        return self.service.pagar_fatura(
            id_cartao, mes, ano, id_conta, id_usuario
        )

    # ==================================================
    # LIMITE
    # ==================================================
    def obter_limite_disponivel(self, id_cartao):
        id_usuario = self.get_id_usuario()
        return self.service.calcular_limite_disponivel(
            id_cartao, id_usuario
        )

    # ==================================================
    # CARTÕES
    # ==================================================
    def listar_cartoes(self):
        return self.service.listar_cartoes(
            self.get_id_usuario()
        )

    def criar_cartao(self, dados: dict):
        return self.service.criar_cartao(
            dados,
            self.get_id_usuario()
        )

    def editar_cartao(self, id_cartao, dados: dict):
        return self.service.editar_cartao(
            id_cartao,
            dados,
            self.get_id_usuario()
        )

    def buscar_cartao_por_id(self, id_cartao):
        return self.service.buscar_cartao_por_id(
            id_cartao,
            self.get_id_usuario()
        )

    def excluir_cartao(self, id_cartao):
        return self.service.excluir_cartao(
            id_cartao,
            self.get_id_usuario()
        )

    def get_all_cartoes(self):
        return self.listar_cartoes()

    # ==================================================
    # EXPORTAÇÃO
    # ==================================================
    def exportar_fatura_pdf(self, cartao, lancamentos, caminho):
        return self.service.exportar_fatura_pdf(
            cartao,
            lancamentos,
            caminho
        )

    # ==================================================
    # VALORES
    # ==================================================
    def obter_valor_fatura_atual(self, id_cartao):
        id_usuario = self.get_id_usuario()

        hoje = datetime.today()

        return self.service.calcular_fatura_mes(
            id_cartao,
            hoje.month,
            hoje.year,
            id_usuario
        )

    def obter_fatura_mes(self, id_cartao, mes, ano):
        return self.listar_lancamentos_fatura(
            id_cartao,
            mes,
            ano
        )


    def get_painel_cartao(self, id_cartao, mes, ano, page, limit, status):

        id_usuario = self.session.get_user_id()

        return self.service.get_painel_cartao(
            id_cartao=id_cartao,
            id_usuario=id_usuario,
            page=page,
            limit=limit,
            status=status
        )

   