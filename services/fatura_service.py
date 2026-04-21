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

        for l in lancamentos:
            id_cat = l.get("ID_Categoria")

            if id_cat:
                l["Categoria"] = self.category_model.get_nome_categoria_by_id(
                    id_cat,
                    id_usuario
                )
            else:
                l["Categoria"] = "Sem categoria"

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

    def calcular_limite_disponivel(self, id_cartao, id_usuario):
        resumo = self.get_resumo_cartao(id_cartao, id_usuario)
        return resumo.get("disponivel", 0.0)

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
    # PAGAMENTO
    # ============================================================
    def pagar_fatura(self, id_cartao, mes, ano, id_conta, id_usuario):

        fatura = self.obter_fatura(id_cartao, mes, ano, id_usuario)

        total = sum(float(l["Valor"]) for l in fatura if not l.get("Paga"))

        if total <= 0:
            raise ValueError("Nenhum valor em aberto para pagamento.")

        conta = self.transaction_model.get_account_by_id(id_conta, id_usuario)

        if not conta:
            raise ValueError("Conta não encontrada.")

        if float(conta["Saldo_Atual"]) < total:
            raise ValueError("Saldo insuficiente.")

        cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)

        descricao = f"Pagamento Fatura {mes:02d}/{ano} - {cartao.get('Nome', '')}"

        categoria_id = self._get_categoria_pagamento_fatura(id_usuario)

        transacao_id = self.transaction_model.add_transaction({
            "Descricao": descricao,
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
    # PAINEL
    # ============================================================
    def get_painel_cartao(self, id_cartao, id_usuario, page=0, limit=50, status="Todos"):

        hoje = date.today()

        cartao = self.buscar_cartao_por_id(id_cartao, id_usuario)
        if not cartao:
            return {}

        dia_fechamento = cartao["Dia_Fechamento"]

        competencia = hoje - relativedelta(months=1) if hoje.day <= dia_fechamento else hoje

        mes = competencia.month
        ano = competencia.year

        lancamentos = self.lancamento_model.get_lancamentos_nao_pagos(
            id_cartao, id_usuario
        )

        fatura_atual = []
        futuras = {}

        for l in lancamentos:

            valor = float(l["Valor"])

            comp_mes = l["Competencia_Mes"]
            comp_ano = l["Competencia_Ano"]

            if comp_mes == mes and comp_ano == ano:
                fatura_atual.append(l)
            else:
                chave = f"{comp_mes:02d}/{comp_ano}"
                futuras.setdefault(chave, 0)
                futuras[chave] += valor

        if status == "Abertos":
            fatura_atual = [l for l in fatura_atual if not l.get("Paga")]
        elif status == "Pagos":
            fatura_atual = [l for l in fatura_atual if l.get("Paga")]

        total_registros = len(fatura_atual)

        inicio = page * limit
        fim = inicio + limit
        fatura_paginada = fatura_atual[inicio:fim]

        total = sum(float(l["Valor"]) for l in fatura_atual)
        abertos = sum(float(l["Valor"]) for l in fatura_atual if not l.get("Paga"))
        pagos = total - abertos

        resumo = self.get_resumo_cartao(id_cartao, id_usuario)

        return {
            "resumo": resumo,
            "fatura": {
                "total": total,
                "abertos": abertos,
                "pagos": pagos
            },
            "futuras": dict(sorted(futuras.items())),
            "lancamentos": fatura_paginada,
            "total_registros": total_registros
        }
