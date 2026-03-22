import logging
from database.database import Database, DatabaseError

logger = logging.getLogger(__name__)


class CategoryModel(Database):

    def __init__(self):
        super().__init__()
        try:
            self.connect()
        except Exception:
            pass

    # ==================================================
    # CATEGORIAS
    # ==================================================

    def add_category(self, nome, tipo, id_usuario, id_categoria_pai=None):
        """
        Cria categoria principal.
        """

        query = """
        INSERT INTO categorias
        (Nome, Tipo, ID_Usuario, ID_Categoria_Pai)
        VALUES (?, ?, ?, ?)
        """

        return self.execute_insert(
            query,
            (nome, tipo, id_usuario, id_categoria_pai)
        )

    def get_all_categories(self, id_usuario):
        """
        Retorna todas as categorias principais do usuário.
        """

        query = """
        SELECT * FROM categorias
        WHERE ID_Usuario = ?
        ORDER BY Nome
        """

        return self.fetch_all(query, (id_usuario,))

    def get_category_by_id(self, id_categoria, id_usuario):

        query = """
        SELECT ID_Categoria, Nome, Tipo
        FROM categorias
        WHERE ID_Categoria = ?
        AND ID_Usuario = ?
        """

        return self.fetch_one(query, (id_categoria, id_usuario))

    def get_category_by_name(self, nome, id_usuario):

        query = """
        SELECT ID_Categoria, Nome, Tipo
        FROM categorias
        WHERE Nome = ?
        AND ID_Usuario = ?
        """

        return self.fetch_one(query, (nome, id_usuario))

    def update_category(self, id_categoria, nome, tipo, id_usuario):

        query = """
        UPDATE categorias
        SET Nome = ?, Tipo = ?
        WHERE ID_Categoria = ?
        AND ID_Usuario = ?
        """

        self.execute_query(
            query,
            (nome, tipo, id_categoria, id_usuario)
        )

        return True

    # ==================================================
    # SUBCATEGORIAS
    # ==================================================

    
    def get_subcategories(self, id_categoria_pai, id_usuario):

        query = """
        SELECT * FROM categorias
        WHERE ID_Categoria_Pai = ?
        AND ID_Usuario = ?
        ORDER BY Nome
        """

        return self.fetch_all(query, (id_categoria_pai, id_usuario))

    
    # ==================================================
    # EXCLUSÃO
    # ==================================================

    def delete_category(self, id_categoria, id_usuario):
        """
        Exclui categoria somente se:
        - Não possuir subcategorias
        - Não estiver vinculada a transações
        """

        # 1️⃣ Verificar subcategorias
        query_filhos = """
        SELECT COUNT(*) as total
        FROM categorias
        WHERE ID_Categoria_Pai = ?
        AND ID_Usuario = ?
        """

        filhos = self.fetch_one(query_filhos, (id_categoria, id_usuario))

        if filhos and filhos["total"] > 0:
            return False, "Categoria possui subcategorias vinculadas."

        # 2️⃣ Verificar transações
        query_trans = """
        SELECT COUNT(*) as total
        FROM transacoes
        WHERE ID_Categoria = ?
        AND ID_Usuario = ?
        """

        trans = self.fetch_one(query_trans, (id_categoria, id_usuario))

        if trans and trans["total"] > 0:
            return False, "Categoria está em uso por transações."

        # 3️⃣ Excluir
        query_delete = """
        DELETE FROM categorias
        WHERE ID_Categoria = ?
        AND ID_Usuario = ?
        """

        self.execute_query(query_delete, (id_categoria, id_usuario))

        return True, None

    # ==================================================
    # NOME PELO ID
    # ==================================================

    def get_nome_categoria_by_id(self, id_categoria, id_usuario):

        try:
            query = """
            SELECT Nome
            FROM categorias
            WHERE ID_Categoria = ?
            AND ID_Usuario = ?
            """

            categoria = self.fetch_one(query, (id_categoria, id_usuario))

            if categoria:
                return categoria["Nome"]

            return "Categoria Desconhecida"

        except DatabaseError as e:
            logger.error(f"Erro ao buscar nome da categoria: {e}")
            return "Categoria Desconhecida"

    # ==================================================
    # CRIAR SUBCATEGORIA
    # ==================================================
    def add_subcategory(self, nome, id_categoria, id_usuario):

        query = """
        INSERT INTO subcategorias
        (Nome, ID_Categoria, ID_Usuario)
        VALUES (?, ?, ?)
        """

        return self.execute_insert(
            query,
            (nome, id_categoria, id_usuario)
        )


