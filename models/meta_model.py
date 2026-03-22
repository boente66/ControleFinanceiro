import logging
from database.database import Database

logger = logging.getLogger(__name__)


class MetaModel(Database):
    """
    Model responsável apenas pela persistência de metas.
    Sem regra de negócio.
    """

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    def add_meta(
        self,
        nome,
        tipo,
        valor_alvo,
        id_usuario,
        id_categoria=None,
        data_inicio=None,
        data_fim=None
    ):
        query = """
        INSERT INTO metas (
            Nome,
            Tipo,
            Valor_Alvo,
            ID_Categoria,
            Data_Inicio,
            Data_Fim,
            ID_Usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        return self.execute_insert(query, (
            nome,
            tipo,
            valor_alvo,
            id_categoria,
            data_inicio,
            data_fim,
            id_usuario
        ))

    # --------------------------------------------------
    # READ
    # --------------------------------------------------
    def get_metas_by_user(self, id_usuario):
        query = """
        SELECT *
        FROM metas
        WHERE ID_Usuario = ?
        ORDER BY Criado_Em DESC
        """
        return self.fetch_all(query, (id_usuario,))

    def get_metas_by_status(self, id_usuario, status):
        query = """
        SELECT *
        FROM metas
        WHERE ID_Usuario = ?
        AND Status = ?
        ORDER BY Criado_Em DESC
        """
        return self.fetch_all(query, (id_usuario, status))

    def get_meta_by_id(self, id_meta, id_usuario):
        query = """
        SELECT *
        FROM metas
        WHERE ID_Meta = ?
        AND ID_Usuario = ?
        """
        return self.fetch_one(query, (id_meta, id_usuario))

    def get_metas_by_categoria(self, id_categoria, id_usuario):
        query = """
        SELECT *
        FROM metas
        WHERE ID_Categoria = ?
        AND ID_Usuario = ?
        AND Status = 'ATIVA'
        """
        return self.fetch_all(query, (id_categoria, id_usuario))

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update_meta(
        self,
        id_meta,
        nome,
        tipo,
        valor_alvo,
        id_categoria,
        data_inicio,
        data_fim,
        id_usuario
    ):
        query = """
        UPDATE metas
        SET Nome = ?,
            Tipo = ?,
            Valor_Alvo = ?,
            ID_Categoria = ?,
            Data_Inicio = ?,
            Data_Fim = ?
        WHERE ID_Meta = ?
        AND ID_Usuario = ?
        """

        self.execute_query(query, (
            nome,
            tipo,
            valor_alvo,
            id_categoria,
            data_inicio,
            data_fim,
            id_meta,
            id_usuario
        ))

    def update_status(self, id_meta, status, id_usuario):
        query = """
        UPDATE metas
        SET Status = ?,
            Concluido_Em = CASE
                WHEN ? = 'CONCLUIDA'
                THEN CURRENT_TIMESTAMP
                ELSE Concluido_Em
            END
        WHERE ID_Meta = ?
        AND ID_Usuario = ?
        """

        self.execute_query(query, (
            status,
            status,
            id_meta,
            id_usuario
        ))

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    def delete_meta(self, id_meta, id_usuario):
        query = """
        DELETE FROM metas
        WHERE ID_Meta = ?
        AND ID_Usuario = ?
        """
        self.execute_query(query, (id_meta, id_usuario))