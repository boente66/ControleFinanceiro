from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from models.lancamento_model import LancamentoModel
from models.credito_model import CreditoModel
from models.transaction_model import TransactionModel
from models.category_model import CategoryModel


class FaturaService:

    def __init__(self):
        self.lancamento_model = LancamentoModel()
        self.credito_model = CreditoModel()
        self.transaction_model = TransactionModel()
        self.category_model = CategoryModel()

    # ============================================================
    # CARTÃO (CRUD)
    # ============================================================
    def criar_cartao(self, dados: dict, id_usuario: int):
        dados["ID_Usuario"] = id_usuario
        return self.credito_model.add_cartao(dados)

    def editar_cartao(self, id_cartao: int, dados: dict, id_usuario: int):
        cartao = self.credito_model.get_cartao_by_id(id_cartao, id_usuario)
        if not cartao:
            raise ValueError("Cartão não encontrado.")
        return self.credito_model.update_cartao(id_cartao, dados, id_usuario)

    def excluir_cartao(self, id_cartao: int, id_usuario: int):
        cartao = self.credito_model.get_cartao_by_id(id_cartao, id_usuario)
        if not cartao:
            raise ValueError("Cartão não encontrado.")
        return self.credito_model.delete_cartao(id_cartao, id_usuario)

    def listar_cartoes(self, id_usuario: int):
        return self.credito_model.get_all_cartoes(id_usuario)

    def buscar_cartao_por_id(self, id_cartao: int, id_usuario: int):
        return self.credito_model.get_cartao_by_id(id_cartao, id_usuario)

    # ============================================================
    # REGRA DE FECHAMENTO
    # ============================================================
    def aplicar_fatura(self, data_compra, dia_fechamento: int):
        """
        Retorna (mes, ano) da competência da fatura.
        """

        if isinstance(data_compra, str):
            data_compra = datetime.fromisoformat(data_compra).date()

        if data_compra.day > dia_fechamento:
            competencia = data_compra + relativedelta(months=1)
        else:
            competencia = data_compra

        return competencia.month, competencia.year

    # ============================================================
    # OBTER FATURA
    # ============================================================
    def obter_fatura(self, id_cartao: int, mes: int, ano: int, id_usuario: int):

        cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)
        if not cartao:
            return []

        dia_fechamento = cartao["Dia_Fechamento"]

        lancamentos = self.lancamento_model.get_lancamentos_por_fatura(
            id_cartao, mes, ano
        )

        fatura = []

        for l in lancamentos:

            mes_f, ano_f = self.aplicar_fatura(
                l["Data"], dia_fechamento
            )

            if mes_f == mes and ano_f == ano:
                fatura.append(l)

        return fatura

    # ============================================================
    # TOTAL DA FATURA
    # ============================================================
    def calcular_total_fatura(self, id_cartao, mes, ano, id_usuario):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        return sum(
            float(l["Valor"])
            for l in fatura
            if not l.get("Paga")
        )

    # ============================================================
    # LIMITE DISPONÍVEL
    # ============================================================
    def calcular_limite_disponivel(self, id_cartao, id_usuario):

        cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)
        if not cartao:
            return 0.0

        limite = float(cartao["Limite"])

        lancamentos_abertos = self.lancamento_model.get_lancamentos_nao_pagos(
            id_cartao, id_usuario
        )

        usado = sum(float(l["Valor"]) for l in lancamentos_abertos)

        return limite - usado

    # ============================================================
    # REGISTRAR DESPESA
    # ============================================================
    def registrar_despesa_cartao(self, data: dict, id_usuario: int):

        valor_total = float(data["Valor"])
        parcelas = int(data.get("Parcelas", 1)) or 1

        base = round(valor_total / parcelas, 2)
        restante = round(valor_total - base * (parcelas - 1), 2)

        for i in range(parcelas):

            valor_parcela = restante if i == parcelas - 1 else base

            lancamento = {
                "Descricao": data["Descricao"],
                "Valor": valor_parcela,
                "Data": data["Data"],
                "ID_Cartao": data["ID_Cartao"],
                "ID_Usuario": id_usuario,
                "Paga": 0,
                "Parcela_Atual": i + 1,
                "Num_Parcelas": parcelas,
            }

            self.lancamento_model.add_lancamento(lancamento)

    # ============================================================
    # PAGAR FATURA
    # ============================================================
    def pagar_fatura(
        self,
        id_cartao: int,
        mes: int,
        ano: int,
        id_conta: int,
        id_usuario: int
    ):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        if not fatura:
            raise ValueError("Nenhum lançamento encontrado.")

        total = sum(
            float(l["Valor"])
            for l in fatura
            if not l.get("Paga")
        )

        conta = self.transaction_model.get_account_by_id(
            id_conta, id_usuario
        )

        if not conta:
            raise ValueError("Conta não encontrada.")

        if float(conta["Saldo_Atual"]) < total:
            raise ValueError("Saldo insuficiente.")

        categoria_id = self._get_categoria_pagamento_fatura(id_usuario)

        transacao_id = self.transaction_model.add_transaction({
            "Descricao": "Pagamento de Fatura",
            "Valor": -abs(total),
            "Data": date.today().isoformat(),
            "Tipo": "Despesa",
            "ID_Conta": id_conta,
            "ID_Usuario": id_usuario,
            "ID_Categoria": categoria_id
        })

        for l in fatura:
            if not l.get("Paga"):
                self.lancamento_model.marcar_como_pago(
                    l["ID_Lancamento"],
                    transacao_id
                )

        return True

    # ============================================================
    # CATEGORIA AUTOMÁTICA
    # ============================================================
    def _get_categoria_pagamento_fatura(self, id_usuario: int):

        categoria = self.category_model.get_by_nome(
            "Pagamento de Fatura",
            id_usuario
        )

        if categoria:
            return categoria["ID_Categoria"]

        return self.category_model.add_categoria({
            "Nome": "Pagamento de Fatura",
            "Tipo": "Despesa",
            "ID_Usuario": id_usuario
        })

    # ============================================================
    # EXPORTAR PDF
    # ============================================================
    def exportar_fatura_pdf(self, cartao, lancamentos, caminho):

        from services.infrastructure.pdf_service import PdfService

        titulo = f"Fatura {cartao['Nome']}"

        conteudo = f"Cartão: {cartao['Nome']}\n"
        conteudo += f"Limite: R$ {float(cartao['Limite']):.2f}\n"
        conteudo += f"Dia de Fechamento: {cartao['Dia_Fechamento']}\n\n"
        conteudo += "Lançamentos:\n"

        for l in lancamentos:

            data_valor = l["Data"]
            if isinstance(data_valor, str):
                data_valor = datetime.fromisoformat(data_valor).date()

            data_str = data_valor.strftime("%d/%m/%Y")
            valor_str = f"R$ {float(l['Valor']):.2f}"
            descricao = l["Descricao"]

            parcela_info = ""
            if l.get("Num_Parcelas", 1) > 1:
                parcela_info = (
                    f" ({l['Parcela_Atual']}/{l['Num_Parcelas']})"
                )

            conteudo += (
                f"- {data_str}: {descricao}"
                f"{parcela_info} - {valor_str}\n"
            )

        pdf_service = PdfService()
        return pdf_service.gerar_pdf(caminho, titulo, conteudo)

    # ============================================================
    # FATURA MÊS ATUAL
    # ============================================================
    def calcular_fatura_mes_atual(self, id_cartao, id_usuario):

        cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)
        if not cartao:
            return 0.0

        hoje = date.today()
        dia_fechamento = cartao["Dia_Fechamento"]

        if hoje.day <= dia_fechamento:
            competencia = hoje - relativedelta(months=1)
        else:
            competencia = hoje

        return self.calcular_total_fatura(
            id_cartao,
            competencia.month,
            competencia.year,
            id_usuario
        )

    # ============================================================
    # FATURA MÊS ESPECÍFICO
    # ============================================================
    def calcular_fatura_mes(self, id_cartao, mes, ano, id_usuario):

        return self.calcular_total_fatura(
            id_cartao,
            mes,
            ano,
            id_usuario
        )
