from services.category_service import CategoryService
from core.session import Session


class CategoryController:

    def __init__(self):
        self.service = CategoryService()

    # ======================================================
    # UTIL
    # ======================================================
    def _get_user_id(self):
        usuario = Session.get_usuario()
        if not usuario:
            raise RuntimeError("Usuário não autenticado")
        return usuario["ID_Usuario"]

    # ======================================================
    # CATEGORIAS
    # ======================================================
    def get_all_categories(self):
        return self.service.get_all_categories(
            self._get_user_id()
        )

    def get_category_by_id(self, id_categoria):
        return self.service.model.get_category_by_id(
            id_categoria,
            self._get_user_id()
        )

    def get_category_by_name(self, nome):
        return self.service.get_category_by_name(
            nome,
            self._get_user_id()
        )

    def add_category(self, nome, tipo):
        return self.service.add_category(
            nome,
            tipo,
            self._get_user_id()
        )

    def update_category(self, id_categoria, nome, tipo):
        return self.service.model.update_category(
            id_categoria,
            nome,
            tipo,
            self._get_user_id()
        )

    def delete_category(self, id_categoria):
        return self.service.delete_category(
            id_categoria,
            self._get_user_id()
        )

    def get_nome_categoria_by_id(self, id_categoria):
        return self.service.get_nome_categoria_by_id(
            id_categoria,
            self._get_user_id()
        )

    # ======================================================
    # SUBCATEGORIAS
    # ======================================================
    def add_subcategory(self, nome, tipo, id_categoria_pai):
        return self.service.add_subcategory(
            nome,
            tipo,
            id_categoria_pai,
            self._get_user_id()
        )

    def get_subcategories(self, id_categoria_pai):
        return self.service.get_subcategories(
            id_categoria_pai,
            self._get_user_id()
        )