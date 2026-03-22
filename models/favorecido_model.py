from database.database import Database, DatabaseError

class FavorecidoModel(Database):

    # ---------------------------------------------------------
    # LISTAR
    # ---------------------------------------------------------
    def get_all_favorecidos(self, id_usuario):
        return self.fetch_all(
            """
            SELECT ID_Favorecido, Nome, Tipo, CPF, Telefone
            FROM favorecido
            WHERE ID_Usuario = ?
            ORDER BY Nome ASC
            """,
            (id_usuario,)
        )

    # ---------------------------------------------------------
    # OBTER POR ID
    # ---------------------------------------------------------
    def get_favorecido_by_id(self, id_favorecido, id_usuario):
        return self.fetch_one(
            """
            SELECT *
            FROM favorecido
            WHERE ID_Favorecido = ? AND ID_Usuario = ?
            """,
            (id_favorecido, id_usuario)
        )

    # ---------------------------------------------------------
    # Obter tipo
    # ---------------------------------------------------------
    def get_tipo(self, id_favorecido, id_usuario):
        row = self.fetch_one(
            """
            SELECT Tipo
            FROM favorecido
            WHERE ID_Favorecido = ? AND ID_Usuario = ?
            """,
            (id_favorecido, id_usuario)
        )
        return row["Tipo"] if row else None

    # ---------------------------------------------------------
    # INSERIR
    # ---------------------------------------------------------
    def add_favorecido(self, dados, id_usuario):
        try:
            self.execute_query(
                """
                INSERT INTO favorecido (Nome, Tipo, CPF, Telefone, ID_Usuario)
                VALUES (?, ?, ?, ?, ?)
                """,
                (dados["Nome"], dados["Tipo"], dados.get("CPF"), dados.get("Telefone"), id_usuario)
            )
        except Exception as e:
            raise DatabaseError(str(e))

        row = self.fetch_one("SELECT last_insert_rowid() AS id")
        return row["id"]

    # ---------------------------------------------------------
    # DELETE — pessoa física
    # ---------------------------------------------------------
    def delete_pessoa_fisica(self, id_favorecido, id_usuario):
        try:
            self.execute_query(
                "DELETE FROM pessoa_fisica WHERE ID_PessoaFisica IN "
                "(SELECT ID_PessoaFisica FROM favorecido WHERE ID_Favorecido = ?)",
                (id_favorecido,)
            )

            self.execute_query(
                "DELETE FROM favorecido WHERE ID_Favorecido = ? AND ID_Usuario = ?",
                (id_favorecido, id_usuario)
            )
            return True, "Pessoa Física removida."
        except Exception as e:
            raise DatabaseError(str(e))

    # ---------------------------------------------------------
    # DELETE — pessoa jurídica
    # ---------------------------------------------------------
    def delete_pessoa_juridica(self, id_favorecido, id_usuario):
        try:
            self.execute_query(
                "DELETE FROM pessoa_juridica WHERE ID_PessoaJuridica IN "
                "(SELECT ID_PessoaJuridica FROM favorecido WHERE ID_Favorecido = ?)",
                (id_favorecido,)
            )

            self.execute_query(
                "DELETE FROM favorecido WHERE ID_Favorecido = ? AND ID_Usuario = ?",
                (id_favorecido, id_usuario)
            )
            return True, "Pessoa Jurídica removida."
        except Exception as e:
            raise DatabaseError(str(e))

    # ---------------------------------------------------------
    # DELETE — tipo indefinido (plano B)
    # ---------------------------------------------------------
    def delete_favorecido(self, id_favorecido, id_usuario):
        """Fallback: remove só da tabela favorecido."""
        try:
            self.execute_query(
                "DELETE FROM favorecido WHERE ID_Favorecido = ? AND ID_Usuario = ?",
                (id_favorecido, id_usuario)
            )
            return True
        except Exception as e:
            raise DatabaseError(str(e))

    # ---------------------------------------------------------
    # ATUALIZAR
    # ---------------------------------------------------------
    def update_favorecido(self, id_favorecido, nome, cpf, telefone):
        try:
            self.execute_query(
                """
                UPDATE favorecido
                SET Nome = ?, CPF = ?, Telefone = ?
                WHERE ID_Favorecido = ?
                """,
                (nome, cpf, telefone, id_favorecido)
            )
            return True, "Favorecido atualizado."
        except Exception as e:
            raise DatabaseError(str(e))