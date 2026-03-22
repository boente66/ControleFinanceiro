import logging
from models.category_model import CategoryModel

logger = logging.getLogger(__name__)


class CategoryService:

    def __init__(self):
        self.model = CategoryModel()

    # ==================================================
    # CATEGORIAS BÁSICAS
    # ==================================================

    def get_all_categories(self, id_usuario):
        return self.model.get_all_categories(id_usuario)

    def get_category_by_id(self, id_categoria, id_usuario):
        return self.model.get_category_by_id(id_categoria, id_usuario)

    def get_category_by_name(self, nome, id_usuario):
        return self.model.get_category_by_name(nome, id_usuario)

    def add_category(self, nome, tipo, id_usuario, id_categoria_pai=None):
        return self.model.add_category(
            nome=nome,
            tipo=tipo,
            id_usuario=id_usuario,
            id_categoria_pai=id_categoria_pai
        )

    def update_category(self, id_categoria, nome, tipo, id_usuario):
        return self.model.update_category(
            id_categoria,
            nome,
            tipo,
            id_usuario
        )

    def delete_category(self, id_categoria, id_usuario):
        return self.model.delete_category(id_categoria, id_usuario)

    def get_nome_categoria_by_id(self, id_categoria, id_usuario):
        return self.model.get_nome_categoria_by_id(id_categoria, id_usuario)

    def get_subcategories(self, id_categoria_pai, id_usuario):
        return self.model.get_subcategories(id_categoria_pai, id_usuario)

    # ==================================================
    # 🔥 RESOLVER CATEGORIA NA IMPORTAÇÃO (1:N CORRETO)
    # ==================================================

    def resolver_categoria_importacao(
        self,
        categoria_pai_nome,
        subcategoria_nome,
        valor,
        id_usuario
    ):

        if not categoria_pai_nome:
            return None

        categoria_pai_nome = categoria_pai_nome.strip()
        subcategoria_nome = (
            subcategoria_nome.strip()
            if subcategoria_nome else None
        )

        tipo = "Receita" if valor > 0 else "Despesa"

        # 1️⃣ Buscar categoria pai correta por tipo
        categoria_pai = self._buscar_categoria_pai(
            categoria_pai_nome,
            tipo,
            id_usuario
        )

        if categoria_pai:
            id_categoria_pai = categoria_pai["ID_Categoria"]
        else:
            id_categoria_pai = self.model.add_category(
                nome=categoria_pai_nome,
                tipo=tipo,
                id_usuario=id_usuario,
                id_categoria_pai=None
            )

        # 2️⃣ Se não houver subcategoria → retorna pai
        if not subcategoria_nome:
            return id_categoria_pai

        # 3️⃣ Buscar subcategoria vinculada ao pai correto
        subcategorias = self.model.get_subcategories(
            id_categoria_pai,
            id_usuario
        )

        for sub in subcategorias:
            if sub["Nome"].strip().lower() == subcategoria_nome.lower():
                return sub["ID_Categoria"]

        # 4️⃣ Criar subcategoria corretamente vinculada
        return self.model.add_category(
            nome=subcategoria_nome,
            tipo=tipo,
            id_usuario=id_usuario,
            id_categoria_pai=id_categoria_pai
        )

    # ==================================================
    # 🔎 BUSCAR CATEGORIA PAI (TIPO + NOME)
    # ==================================================

    def _buscar_categoria_pai(self, nome, tipo, id_usuario):

        categorias = self.model.get_all_categories(id_usuario)

        for cat in categorias:
            if (
                cat["ID_Categoria_Pai"] is None
                and cat["Tipo"] == tipo
                and cat["Nome"].strip().lower() == nome.lower()
            ):
                return cat

        return None

    # ==================================================
    # 🏗 GARANTIR CATEGORIAS PADRÃO
    # ==================================================

    def garantir_categorias_padrao(self, id_usuario):
        """
        Cria categorias padrão apenas se não existirem.
        Estrutura 1:N correta.
        """

        categorias = self.get_all_categories(id_usuario)

        # Mapa rápido
        mapa = {
            (c["Nome"].strip().lower(), c["ID_Categoria_Pai"]): c
            for c in categorias
        }

        # --------------------------------------------------
        # 1️⃣ Categoria Pai Receita
        # --------------------------------------------------
        receita = self._buscar_categoria_pai("Receita", "Receita", id_usuario)

        if not receita:
            id_receita = self.add_category(
                nome="Receita",
                tipo="Receita",
                id_usuario=id_usuario,
                id_categoria_pai=None
            )
        else:
            id_receita = receita["ID_Categoria"]

        # --------------------------------------------------
        # 2️⃣ Categoria Pai Despesa
        # --------------------------------------------------
        despesa = self._buscar_categoria_pai("Despesa", "Despesa", id_usuario)

        if not despesa:
            id_despesa = self.add_category(
                nome="Despesa",
                tipo="Despesa",
                id_usuario=id_usuario,
                id_categoria_pai=None
            )
        else:
            id_despesa = despesa["ID_Categoria"]

        # --------------------------------------------------
        # 3️⃣ Subcategorias padrão Despesa
        # --------------------------------------------------
        sub_despesa = [
            "Alimentação",
            "Transporte",
            "Moradia",
            "Saúde",
            "Educação",
            "Lazer",
            "Outros"
        ]

        for nome in sub_despesa:
            chave = (nome.lower(), id_despesa)
            if chave not in mapa:
                self.add_category(
                    nome=nome,
                    tipo="Despesa",
                    id_usuario=id_usuario,
                    id_categoria_pai=id_despesa
                )

        # --------------------------------------------------
        # 4️⃣ Subcategorias padrão Receita
        # --------------------------------------------------
        sub_receita = [
            "Salário",
            "Investimentos",
            "Freelance",
            "Outras Receitas"
        ]

        for nome in sub_receita:
            chave = (nome.lower(), id_receita)
            if chave not in mapa:
                self.add_category(
                    nome=nome,
                    tipo="Receita",
                    id_usuario=id_usuario,
                    id_categoria_pai=id_receita
                )