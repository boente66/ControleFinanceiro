
class FavorecidoForm:

    def __init__(self, tipo, nome, documento, telefone):
        from utilitarios.name_format import NameFormat

        self.tipo = tipo
        self.nome = (nome or "").strip()
        self.documento = NameFormat.somente_numeros(documento)
        self.telefone = NameFormat.somente_numeros(telefone)

    def validar(self):
        if not self.nome:
            raise ValueError("Nome obrigatório")

        if not self.documento:
            raise ValueError("Documento obrigatório")

        if self.tipo == "PF" and len(self.documento) != 11:
            raise ValueError("CPF inválido")

        if self.tipo == "PJ" and len(self.documento) != 14:
            raise ValueError("CNPJ inválido")

    def to_dict(self):
        dados = {
            "Tipo": self.tipo,
            "Nome": self.nome,
            "Telefone": self.telefone
        }

        if self.tipo == "PF":
            dados["CPF"] = self.documento
        else:
            dados["CNPJ"] = self.documento
            dados["Razao_Social"] = self.nome

        return dados