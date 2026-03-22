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
    # CRIAR (EXPLÍCITO)
    # ---------------------------------------------------------
    def criar(self, dados, id_usuario):
        nome = dados.get("Nome")
        tipo = dados.get("Tipo")
        cpf = dados.get("CPF")
        telefone = dados.get("Telefone")

        if not nome:
            raise ValueError("Nome é obrigatório.")

        if tipo not in ("Pessoa Física", "Pessoa Jurídica"):
            raise ValueError("Tipo inválido.")

        payload = {
            "Nome": nome,
            "Tipo": tipo,
            "CPF": cpf,
            "Telefone": telefone,
            "ID_Usuario": id_usuario
        }

        return self.model.add_favorecido(payload)

    # ---------------------------------------------------------
    # ATUALIZAR
    # ---------------------------------------------------------
    def atualizar(self, id_favorecido, dados, id_usuario):
        fav = self.model.get_favorecido_by_id(id_favorecido, id_usuario)
        if not fav:
            raise ValueError("Favorecido não encontrado.")

        nome = dados.get("Nome", fav["Nome"])
        cpf = dados.get("CPF", fav["CPF"])
        telefone = dados.get("Telefone", fav["Telefone"])

        return self.model.update_favorecido(
            id_favorecido, nome, cpf, telefone
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
    # 🔑 RESOLVER (IA / IMPORTAÇÃO)
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

        # nada informado
        if not nome and not cpf and not cnpj:
            return None

        # 1️⃣ tenta localizar existente
        favorecido = self.model.buscar_favorecido(
            nome=nome,
            cpf=cpf,
            cnpj=cnpj,
            id_usuario=id_usuario
        )

        if favorecido:
            return favorecido["ID_Favorecido"]

        # 2️⃣ só cria se houver documento
        if cnpj:
            tipo = "Pessoa Jurídica"
        elif cpf:
            tipo = "Pessoa Física"
        else:
            # só nome → NÃO cria automaticamente
            return None

        payload = {
            "Nome": nome,
            "Tipo": tipo,
            "CPF": cpf,
            "ID_Usuario": id_usuario
        }

        return self.model.add_favorecido(payload)