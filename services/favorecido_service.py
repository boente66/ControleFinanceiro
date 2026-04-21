from models.favorecido_model import FavorecidoModel


class FavorecidoService:
    def __init__(self):
        self.model = FavorecidoModel()

    # ---------------------------------------------------------
    # LISTAR
    # ---------------------------------------------------------
    def listar(self, id_usuario):
        return self.model.get_all_favorecidos(id_usuario)

    # ---------------------------------------------------------
    # OBTER
    # ---------------------------------------------------------
    def obter(self, id_favorecido, id_usuario):
        fav = self.model.get_favorecido_by_id(id_favorecido, id_usuario)
        if not fav:
            raise ValueError("Favorecido não encontrado.")
        return fav

    # ---------------------------------------------------------
    # CRIAR (AJUSTADO PARA PF/PJ)
    # ---------------------------------------------------------
    def criar(self, dados, id_usuario):
        nome = (dados.get("Nome") or "").strip()
        tipo = dados.get("Tipo")

        if not nome:
            raise ValueError("Nome é obrigatório.")

        if tipo not in ("PF", "PJ"):
            raise ValueError("Tipo inválido. Use PF ou PJ.")

        # 🔍 evitar duplicidade por nome
        existente = self.model.get_favorecido_by_name(nome, id_usuario)
        if existente:
            return existente["ID_Favorecido"]

        payload = {
            "Nome": nome,
            "Tipo": tipo,
            "Telefone": dados.get("Telefone")
        }

        # PF
        if tipo == "PF":
            cpf = dados.get("CPF")
            if not cpf:
                raise ValueError("CPF é obrigatório para Pessoa Física.")
            payload["CPF"] = cpf

        # PJ
        elif tipo == "PJ":
            cnpj = dados.get("CNPJ")
            if not cnpj:
                raise ValueError("CNPJ é obrigatório para Pessoa Jurídica.")

            payload["CNPJ"] = cnpj
            payload["Razao_Social"] = dados.get("Razao_Social")

        return self.model.add_favorecido(payload, id_usuario)

    # ---------------------------------------------------------
    # ATUALIZAR (AJUSTADO)
    # ---------------------------------------------------------
    def atualizar(self, id_favorecido, dados, id_usuario):
        fav = self.model.get_favorecido_by_id(id_favorecido, id_usuario)
        if not fav:
            raise ValueError("Favorecido não encontrado.")

        return self.model.update_favorecido(
            id_favorecido,
            dados,
            id_usuario
        )

    # ---------------------------------------------------------
    # DELETAR
    # ---------------------------------------------------------
    def deletar(self, id_favorecido, id_usuario):
        fav = self.model.get_favorecido_by_id(id_favorecido, id_usuario)
        if not fav:
            raise ValueError("Favorecido não encontrado.")

        return self.model.delete_favorecido(id_favorecido, id_usuario)

    # ---------------------------------------------------------
    # 🔑 RESOLVER (IMPORTAÇÃO / IA)
    # ---------------------------------------------------------
    def resolver_favorecido(self, dados, id_usuario):
        """
        Resolve favorecido a partir de dados de importação.
        Retorna ID_Favorecido ou None.
        NÃO cria favorecido apenas com nome.
        """

        nome = (dados.get("Nome") or "").strip()
        cpf = dados.get("CPF")
        cnpj = dados.get("CNPJ")

        if not nome and not cpf and not cnpj:
            return None

        # 🔍 tenta encontrar existente (precisa existir no model)
        favorecido = self.model.get_favorecido_by_name(nome, id_usuario)

        if favorecido:
            return favorecido["ID_Favorecido"]

        # só cria com documento válido
        if cpf:
            tipo = "PF"
        elif cnpj:
            tipo = "PJ"
        else:
            return None

        payload = {
            "Nome": nome,
            "Tipo": tipo,
            "Telefone": dados.get("Telefone")
        }

        if tipo == "PF":
            payload["CPF"] = cpf
        else:
            payload["CNPJ"] = cnpj
            payload["Razao_Social"] = dados.get("Razao_Social")

        return self.model.add_favorecido(payload, id_usuario)