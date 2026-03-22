import logging
from core.session import Session
from services.fatura_service import FaturaService

logger = logging.getLogger(__name__)


class FaturaController:
    """
    Controller do cartão de crédito.
    Ponte entre Views e FaturaService.
    """

    def __init__(self):
        self.service = FaturaService()



    def get_id_usuario(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise PermissionError("Usuário não autenticado.")
        return usuario["ID_Usuario"]

    # ==================================================
    # REGISTRAR DESPESA NO CARTÃO
    # ==================================================
    def registrar_despesa_cartao(self, dados: dict) -> bool:

        id_usuario = self.get_id_usuario()
        try:
            self.service.registrar_despesa_cartao(dados, id_usuario)
            return True
        except Exception:
            logger.error(
                "Erro no controller ao registrar despesa no cartão",
                exc_info=True
            )
            raise

    # ==================================================
    # LISTAR LANÇAMENTOS DA FATURA (MÊS/ANO)
    # ==================================================
    def listar_lancamentos_fatura(self, id_cartao, mes, ano):
        """
        Retorna os lançamentos da fatura selecionada.
        """

        id_usuario = self.get_id_usuario()
        try:
            return self.service.obter_fatura(
                id_cartao=id_cartao,
                mes=mes,
                ano=ano,
                id_usuario=id_usuario
            )
              
            
        except Exception:
            logger.error(
                "Erro ao listar lançamentos da fatura",
                exc_info=True
            )
            raise

    # ==================================================
    # PAGAR FATURA
    # ==================================================
    def pagar_fatura(
        self,
        id_cartao,
        id_conta,
        mes,
        ano
        
    ) -> bool:
        """
        Efetua o pagamento da fatura selecionada (mes/ano).
        """
        id_usuario = self.get_id_usuario()
        try:
            return self.service.pagar_fatura(
                id_cartao=id_cartao,
                id_conta=id_conta,
                mes=mes,
                ano=ano,
                id_usuario=id_usuario
            )
        except Exception:
            logger.error(
                "Erro no controller ao pagar fatura",
                exc_info=True
            )
            raise

    # ==================================================
    # LIMITE DISPONÍVEL
    # ==================================================
    def obter_limite_disponivel(self, id_cartao):
        id_usuario = self.get_id_usuario()
        try:
            return self.service.calcular_limite_disponivel(
                id_cartao, id_usuario
            )
        except Exception:
            logger.error(
                "Erro no controller ao obter limite disponível",
                exc_info=True
            )
            raise

    # ==================================================
    # CARTÕES (CRUD)
    # ==================================================
    def listar_cartoes(self):
        id_usuario = self.get_id_usuario()
        try:
            return self.service.listar_cartoes(id_usuario)
        except Exception:
            logger.error("Erro ao listar cartões", exc_info=True)
            return []

    def criar_cartao(self, dados: dict):
        id_usuario = self.get_id_usuario()
        try:
            return self.service.criar_cartao(dados, id_usuario)
        except Exception:
            logger.error("Erro ao criar cartão", exc_info=True)
            raise

    def editar_cartao(self, id_cartao, dados: dict):
        id_usuario = self.getID_Usuario()
        try:
            return self.service.editar_cartao(
                id_cartao, dados, id_usuario
            )
        except Exception:
            logger.error("Erro ao editar cartão", exc_info=True)
            raise

    def buscar_cartao_por_id(self, id_cartao):
        id_usuario = self.get_id_usuario()
        try:
            return self.service.buscar_cartao_por_id(
                id_cartao, id_usuario
            )
        except Exception:
            logger.error(
                "Erro ao obter cartão por ID",
                exc_info=True
            )
            raise

    def excluir_cartao(self, id_cartao):
        id_usuario = self.get_id_usuario()
        try:
            return self.service.excluir_cartao(
                id_cartao, id_usuario
            )
        except Exception:
            logger.error(
                "Erro ao excluir cartão",
                exc_info=True
            )
            raise

    def get_all_cartoes(self):

        """
        Retorna todos os cartões do usuário (alias de listar_cartoes).
        """
        try:
            return self.service.listar_cartoes(self.get_id_usuario())
        except Exception:
            logger.error("Erro ao obter todos os cartões", exc_info=True)
            return []


    def exportar_fatura_pdf(
        self,
        cartao: dict,
        resumo: dict,
        tabela,
        caminho: str
    ):
        id_usuario = self.get_id_usuario()
        return self.service.exportar_fatura_pdf(
            cartao,
            resumo,
            tabela,
            caminho,
            id_usuario
           
        )

   # ==================================================
   # VALOR DA FATURA ATUAL
   # ==================================================

    def obter_valor_fatura_atual(self, id_cartao):
        """
        Retorna o valor total da fatura do mês atual.
        """
        id_usuario = self.get_id_usuario()
        try:
            from datetime import datetime

            hoje = datetime.today()
            mes = hoje.month
            ano = hoje.year

            return self.service.calcular_fatura_mes(
                id_cartao=id_cartao,
                mes=mes,
                ano=ano,
                id_usuario=id_usuario
            )
        except Exception:
            logger.error(
                "Erro ao obter valor da fatura atual",
                exc_info=True
            )
            raise


    def obter_fatura_mes(self, id_cartao, mes, ano):
        """
        Retorna a fatura do mês e ano especificados.
        """
        id_usuario = self.get_id_usuario()
        try:
            return self.service.obter_fatura(
                id_cartao=id_cartao,
                mes=mes,
                ano=ano,
                id_usuario=id_usuario
            )
        except Exception:
            logger.error(
                "Erro ao obter fatura do mês",
                exc_info=True
            )
            raise