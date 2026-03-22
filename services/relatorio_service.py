from models.relatorio_model import RelatorioModel
from utilitarios.name_format import NameFormat
from utilitarios.currency_formatter import CurrencyFormatter


class RelatorioService:
    def __init__(self):
        self.model = RelatorioModel()

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
    def gerar_texto_informe(self, usuario, ano):
        # ---------------------------
        #  Resolve ID do usuário
        # ---------------------------
        if isinstance(usuario, dict):
            id_usuario = usuario.get("ID_Usuario")
            nome = usuario.get("Nome", "")
            cpf = usuario.get("CPF", "")
        else:
            id_usuario = getattr(usuario, "ID_Usuario", usuario)
            nome = getattr(usuario, "Nome", "")
            cpf = getattr(usuario, "CPF", "")

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
            valor = CurrencyFormatter.format("pt_BR.UTF-8", item.get("Valor", 0))

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
            doc = item.get("CNPJ", "")
            doc_formatado = NameFormat.formatCNPJ(doc) if len(doc) > 11 else NameFormat.formatCPF(doc)
            valor = CurrencyFormatter.format("pt_BR.UTF-8", item.get("Valor", 0))

            texto += f"""
Favorecido: {fav}
Documento: {doc_formatado}
Total Pago: {valor}
"""

        return texto.strip()