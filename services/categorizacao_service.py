from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from services.category_service import CategoryService


class CategorizacaoService:

    def __init__(self):
        self.category_service = CategoryService()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self._categorias_cache = {}
        self._embeddings_cache = {}

    # ======================================================
    # MÉTODO PRINCIPAL
    # ======================================================
    def categorizar(self, descricao: str, valor: float, id_usuario: int):

        if not descricao:
            return None, 0.0

        categorias = self._obter_categorias_usuario(id_usuario)

        if not categorias:
            return None, 0.0

        emb_desc = self.model.encode([descricao])
        emb_cats = self._embeddings_cache[id_usuario]

        similaridades = cosine_similarity(emb_desc, emb_cats)[0]

        indice = int(np.argmax(similaridades))
        score = float(similaridades[indice])

        if score < 0.45:
            return None, 0.3

        categoria = categorias[indice]

        id_categoria = self.category_service.resolver_categoria_importacao(
            categoria_pai_nome=categoria["CategoriaPai"],
            subcategoria_nome=categoria["Subcategoria"],
            valor=valor,
            id_usuario=id_usuario
        )

        return id_categoria, round(score, 2)

    # ======================================================
    # CARREGAR CATEGORIAS
    # ======================================================
    def _obter_categorias_usuario(self, id_usuario):

        if id_usuario in self._categorias_cache:
            return self._categorias_cache[id_usuario]

        categorias_db = self.category_service.get_all_categories(id_usuario)

        categorias_formatadas = []

        for cat in categorias_db:

            if cat.get("ID_Categoria_Pai") is None:
                continue

            categorias_formatadas.append({
                "CategoriaPai": self._obter_nome_pai(
                    categorias_db,
                    cat.get("ID_Categoria_Pai")
                ),
                "Subcategoria": cat.get("Nome"),
                "Texto": cat.get("Nome")
            })

        if not categorias_formatadas:
            return None

        textos = [c["Texto"] for c in categorias_formatadas]

        self._categorias_cache[id_usuario] = categorias_formatadas
        self._embeddings_cache[id_usuario] = self.model.encode(textos)

        return categorias_formatadas

    # ======================================================
    # AUXILIAR
    # ======================================================
    def _obter_nome_pai(self, categorias, id_pai):

        for cat in categorias:
            if cat.get("ID_Categoria") == id_pai:
                return cat.get("Nome")

        return None