from models.relatorio_model import RelatorioModel
from utilitarios.name_format import NameFormat
from utilitarios.currency_formatter import CurrencyFormatter
from services.user_services import UserService


class RelatorioService:
    def __init__(self):
        self.model = RelatorioModel()
        self.usuario = UserService()

    # ============================================================
    # RELATÓRIO DIÁRIO
    # ============================================================
    def relatorio_diario(self, dias, id_usuario):
        if dias <= 0:
            raise ValueError("O período deve ser maior que zero.")
        return self.model.get_relatorio_diario(dias, id_usuario)

    # ============================================================
    # RELATÓRIO ANUAL
    # ============================================================
    def relatorio_anual(self, ano, id_usuario):
        if not str(ano).isdigit():
            raise ValueError("Ano inválido.")
        return self.model.get_relatorio_anual(ano, id_usuario)

    # ============================================================
    # INFORME DE RENDIMENTOS (RF)
    # ============================================================
    def informe_rendimentos(self, ano, id_usuario):
        receitas = self.model.get_informe_rendimentos(ano, id_usuario)
        gastos = self.model.get_informe_gastos(ano, id_usuario)

        return {
            "ano": ano,
            "receitas": receitas if receitas else [],
            "gastos": gastos if gastos else []
        }

    # ============================================================
    # GERA TEXTO FORMATADO PARA PDF
    # ============================================================
    def gerar_texto_informe(self, id_usuario, ano):
        # ---------------------------
        #  Resolve ID do usuário
        # ---------------------------

        usuarios = self.usuario.get_user_by_id(id_usuario)

        if not usuarios:
            raise ValueError("Usuário não encontrado.")

        nome = usuarios.get("Nome", "")
        cpf = usuarios.get("CPF", "")

        dados = self.informe_rendimentos(ano, id_usuario)

        # ---------------------------
        #  Cabeçalho
        # ---------------------------
        texto = f"""
INFORME DE RENDIMENTOS - ANO BASE {ano}

IDENTIFICAÇÃO DO CONTRIBUINTE:
Nome: {nome}
CPF: {NameFormat.formatCPF(cpf)}

RENDIMENTOS TRIBUTÁVEIS RECEBIDOS DE PESSOA JURÍDICA:
"""

        # ---------------------------
        #  Receitas
        # ---------------------------
        for item in dados["receitas"]:
            fonte = item.get("Fonte", "N/D")
            cnpj = NameFormat.formatCNPJ(item.get("CNPJ", ""))
            valor = CurrencyFormatter.format(item.get("Valor", 0))

            texto += f"""
Fonte Pagadora: {fonte}
CNPJ: {cnpj}
Valor Total Recebido: {valor}
IRRF: R$ 0,00
"""

        # ---------------------------
        #  Gastos
        # ---------------------------
        texto += """
DESPESAS DEDUTÍVEIS / PAGAMENTOS A PESSOAS JURÍDICAS OU FÍSICAS:
"""

        for item in dados["gastos"]:
            fav = item.get("Fonte", "N/D")
            doc = item.get("Documento", "")
            doc_formatado = NameFormat.formatCNPJ(doc) if len(doc) > 11 else NameFormat.formatCPF(doc)
            valor = CurrencyFormatter.format(item.get("Valor", 0),)

            texto += f"""
Favorecido: {fav}
Documento: {doc_formatado}
Total Pago: {valor}
"""

        return texto.strip()
