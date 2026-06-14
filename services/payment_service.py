# -*- coding: utf-8 -*-
import logging

from services.transaction_service import TransactionService
from services.schedule_service import ScheduleService

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Serviço responsável pela baixa de agendamentos.
    """

    TIPO_PAGAR = "Contas a Pagar"
    TIPO_RECEBER = "Contas a Receber"
    TIPO_TRANSFERENCIA = "Transferências"

    STATUS_PERMITIDOS = ("AGENDADO", "ATRASADO")

    def __init__(self):
        self.transaction_service = TransactionService()
        self.schedule_service = ScheduleService()

    # ======================================================
    # BAIXAR AGENDAMENTO
    # ======================================================
    def baixar_agendamento(self, dados_execucao: dict, id_usuario: int):
        if not dados_execucao:
            raise ValueError("Dados da baixa não informados.")

        if not id_usuario:
            raise ValueError("Usuário não informado.")

        id_agendamento = dados_execucao.get("ID_Agendamento")

        if not id_agendamento:
            raise ValueError("ID_Agendamento é obrigatório.")

        agendamento = self.schedule_service.get_schedule_by_id(
            id_agendamento,
            id_usuario
        )

        if not agendamento:
            raise ValueError("Agendamento não encontrado.")

        self._validar_agendamento(agendamento)

        valor_final = self._calcular_valor_final(dados_execucao)
        tipo_transacao = self._tipo_transacao(agendamento)

        valor_transacao = (
            abs(valor_final)
            if tipo_transacao == "Receita"
            else -abs(valor_final)
        )

        transacao = {
            "ID_Conta": dados_execucao.get("ID_Conta"),
            "Descricao": (
                dados_execucao.get("Descricao")
                or agendamento.get("Descricao")
                or "Baixa de agendamento"
            ),
            "Valor": valor_transacao,
            "Data": dados_execucao.get("Data"),
            "Tipo": tipo_transacao,
            "ID_Usuario": id_usuario,
            "ID_Categoria": (
                dados_execucao.get("ID_Categoria")
                or agendamento.get("ID_Categoria")
            ),
            "ID_Favorecido": (
                dados_execucao.get("ID_Favorecido")
                or agendamento.get("ID_Favorecido")
            ),
            "Notas": self._montar_notas(
                dados_execucao,
                valor_final
            ),
        }

        self._validar_transacao(transacao)

        self.transaction_service.criar_transacao(transacao)

        sucesso = self.schedule_service.executar_agendamento(
            id_agendamento,
            id_usuario
        )

        if not sucesso:
            raise RuntimeError(
                "Transação criada, mas agendamento não foi baixado."
            )

        return True

    # ======================================================
    # VALIDAÇÕES
    # ======================================================
    def _validar_agendamento(self, agendamento: dict):
        tipo = agendamento.get("Tipo")
        status = agendamento.get("Status")

        if tipo == self.TIPO_TRANSFERENCIA:
            raise ValueError(
                "Transferência deve ser baixada pelo fluxo de transferência."
            )

        if tipo not in (self.TIPO_PAGAR, self.TIPO_RECEBER):
            raise ValueError(
                f"Tipo de agendamento inválido: {tipo}"
            )

        if status not in self.STATUS_PERMITIDOS:
            raise ValueError(
                f"Agendamento com status '{status}' não pode ser baixado."
            )

    def _validar_transacao(self, transacao: dict):
        if not transacao.get("ID_Conta"):
            raise ValueError("Conta obrigatória.")

        if not transacao.get("Data"):
            raise ValueError("Data obrigatória.")

        if not transacao.get("Descricao"):
            raise ValueError("Descrição obrigatória.")

        if float(transacao.get("Valor", 0)) == 0:
            raise ValueError("Valor inválido.")

    # ======================================================
    # CÁLCULO
    # ======================================================
    def _calcular_valor_final(self, dados_execucao: dict) -> float:
        valor_previsto = float(
            dados_execucao.get("Valor_Previsto", 0)
        )

        desconto = float(
            dados_execucao.get("Desconto", 0)
        )

        multa = float(
            dados_execucao.get("Multa", 0)
        )

        juros = float(
            dados_execucao.get("Juros", 0)
        )

        valor_final = valor_previsto + multa + juros - desconto

        if valor_final <= 0:
            raise ValueError("Valor final inválido.")

        return valor_final

    def _tipo_transacao(self, agendamento: dict) -> str:
        tipo = agendamento.get("Tipo")

        if tipo == self.TIPO_RECEBER:
            return "Receita"

        if tipo == self.TIPO_PAGAR:
            return "Despesa"

        raise ValueError(
            f"Tipo de agendamento inválido: {tipo}"
        )

    # ======================================================
    # NOTAS
    # ======================================================
    def _montar_notas(
        self,
        dados_execucao: dict,
        valor_final: float
    ) -> str:
        notas_usuario = dados_execucao.get("Notas") or ""

        partes = []

        if notas_usuario:
            partes.append(notas_usuario)

        partes.append("Baixa de agendamento:")
        partes.append(
            f"Valor previsto: {dados_execucao.get('Valor_Previsto', 0)}"
        )
        partes.append(
            f"Desconto: {dados_execucao.get('Desconto', 0)}"
        )
        partes.append(
            f"Multa: {dados_execucao.get('Multa', 0)}"
        )
        partes.append(
            f"Juros: {dados_execucao.get('Juros', 0)}"
        )
        partes.append(
            f"Valor final: {valor_final}"
        )

        return "\n".join(partes)