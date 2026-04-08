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

        self._cache_fatura = {}

    # ============================================================
    # CACHE
    # ============================================================
    def _cache_key(self, id_cartao, mes, ano, id_usuario):
        return f"{id_cartao}_{mes}_{ano}_{id_usuario}"

    def _get_cache(self, key):
        return self._cache_fatura.get(key)

    def _set_cache(self, key, value):
        self._cache_fatura[key] = value

    def _clear_cache(self):
        self._cache_fatura.clear()

    # ============================================================
    # CARTÕES
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
    # COMPETÊNCIA
    # ============================================================
    def aplicar_fatura(self, data_compra, dia_fechamento):

        if isinstance(data_compra, str):
            data_compra = datetime.fromisoformat(data_compra)

        if isinstance(data_compra, datetime):
            data_compra = data_compra.date()

        if data_compra.day > dia_fechamento:
            data_compra += relativedelta(months=1)

        return data_compra.month, data_compra.year

    # ============================================================
    # FATURA
    # ============================================================
    def obter_fatura(self, id_cartao, mes, ano, id_usuario):

        cache_key = self._cache_key(id_cartao, mes, ano, id_usuario)

        cached = self._get_cache(cache_key)
        if cached:
            return cached

        lancamentos = self.lancamento_model.get_lancamentos_por_fatura(
            id_cartao, mes, ano, id_usuario
        )

        self._set_cache(cache_key, lancamentos)
        return lancamentos

    def obter_fatura_paginada(self, id_cartao, mes, ano, id_usuario, limit=50, offset=0):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        return {
            "dados": fatura[offset: offset + limit],
            "total": len(fatura)
        }

    # ============================================================
    # TOTAL
    # ============================================================
    def calcular_total_fatura(self, id_cartao, mes, ano, id_usuario):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        return sum(float(l["Valor"]) for l in fatura if not l.get("Paga"))

    # ============================================================
    # LIMITE
    # ============================================================
    def calcular_limite_disponivel(self, id_cartao, id_usuario):

        resumo = self.get_resumo_cartao(id_cartao, id_usuario)
        return resumo.get("disponivel", 0.0)

    def get_resumo_cartao(self, id_cartao, id_usuario):

    cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)
    if not cartao:
        return {}

    limite = float(cartao["Limite"])

    lancamentos = self.lancamento_model.get_lancamentos_nao_pagos(
        id_cartao, id_usuario
    )

    saldo_devedor = sum(float(l["Valor"]) for l in lancamentos)

    return {
        "limite": limite,
        "saldo_devedor": saldo_devedor,
        "disponivel": limite - saldo_devedor
    }

    def verificar_limite(self, id_cartao, id_usuario):

        resumo = self.get_resumo_cartao(id_cartao, id_usuario)

        if not resumo:
            return "OK"

        if resumo["disponivel"] < 0:
            return "ESTOUROU"

        if resumo["disponivel"] < resumo["limite"] * 0.2:
            return "ALERTA"

        return "OK"

    # ============================================================
    # DESPESA PARCELADA
    # ============================================================
    def registrar_despesa_cartao(self, data, id_usuario):

        valor_total = float(data["Valor"])
        parcelas = int(data.get("Parcelas", 1)) or 1

        valor_parcela = round(valor_total / parcelas, 2)

        cartao = self.buscar_cartao_por_id(data["ID_Cartao"], id_usuario)
        dia_fechamento = cartao["Dia_Fechamento"]

        data_base = datetime.fromisoformat(data["Data"])

        for i in range(parcelas):

            data_parcela = data_base + relativedelta(months=i)

            mes, ano = self.aplicar_fatura(data_parcela, dia_fechamento)

            self.lancamento_model.add_lancamento({
                "Descricao": data["Descricao"],
                "Valor": valor_parcela,
                "Data": data_parcela.strftime("%Y-%m-%d"),
                "ID_Cartao": data["ID_Cartao"],
                "ID_Usuario": id_usuario,
                "Competencia_Mes": mes,
                "Competencia_Ano": ano,
                "Parcela_Atual": i + 1,
                "Num_Parcelas": parcelas,
                "Paga": 0,
                "Previsto": 0,
                "ID_Categoria": data.get("ID_Categoria")
            })

        self._clear_cache()

    # ============================================================
    # PREVISÃO
    # ============================================================
    def registrar_previsto_cartao(self, dados: dict, id_usuario: int):

        cartao = self.buscar_cartao_por_id(dados["ID_Cartao"], id_usuario)
        if not cartao:
            return

        mes, ano = self.aplicar_fatura(
            dados["Data"],
            cartao["Dia_Fechamento"]
        )

        existe = self.lancamento_model.existe_previsto(
            dados["ID_Cartao"],
            dados["Descricao"],
            mes,
            ano,
            id_usuario
        )

        if existe:
            return

        self.lancamento_model.add_lancamento({
            "Descricao": dados["Descricao"],
            "Valor": dados["Valor"],
            "Data": dados["Data"],
            "ID_Cartao": dados["ID_Cartao"],
            "ID_Usuario": id_usuario,
            "Competencia_Mes": mes,
            "Competencia_Ano": ano,
            "Previsto": 1,
            "Paga": 0,
            "ID_Categoria": dados.get("ID_Categoria")
        })

        self._clear_cache()

    def prever_faturas_futuras(self, id_cartao, id_usuario):

        lancamentos = self.lancamento_model.get_lancamentos_nao_pagos(
            id_cartao, id_usuario
        )

        previsao = {}

        for l in lancamentos:
            chave = f"{l['Competencia_Mes']:02d}/{l['Competencia_Ano']}"
            previsao.setdefault(chave, 0)
            previsao[chave] += float(l["Valor"])

        return dict(sorted(previsao.items()))

    # ============================================================
    # PAGAMENTO
    # ============================================================
    def pagar_fatura(self, id_cartao, mes, ano, id_conta, id_usuario):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        total = sum(float(l["Valor"]) for l in fatura if not l.get("Paga"))

        conta = self.transaction_model.get_account_by_id(id_conta, id_usuario)

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

        self._clear_cache()
        return True

    # ============================================================
    # CATEGORIA
    # ============================================================
    def _get_categoria_pagamento_fatura(self, id_usuario):

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

        linhas = []
        for l in lancamentos:
            data = datetime.fromisoformat(str(l["Data"])).strftime("%d/%m/%Y")
            valor = f"R$ {float(l['Valor']):.2f}"
            desc = l["Descricao"]

            parcela = ""
            if l.get("Num_Parcelas", 1) > 1:
                parcela = f" ({l['Parcela_Atual']}/{l['Num_Parcelas']})"

            linhas.append(f"{data} - {desc}{parcela} - {valor}")

        conteudo = "\n".join(linhas)

        return PdfService().gerar_pdf(caminho, titulo, conteudo)

    # ============================================================
    # FATURA ATUAL
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
    # FATURA POR MÊS
    # ============================================================
    def calcular_fatura_mes(self, id_cartao, mes, ano, id_usuario):

        return self.calcular_total_fatura(
            id_cartao,
            mes,
            ano,
            id_usuario
        )
