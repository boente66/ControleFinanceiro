from database.database import Database, DatabaseError


class FavorecidoModel(Database):

    # =========================================================
    # LISTAR (COM JOIN COMPLETO)
    # =========================================================
    def get_all_favorecidos(self, id_usuario):
        return self.fetch_all("""
             SELECT 
                 f.ID_Favorecido,
                 f.Nome,
                 f.Tipo,

                 pf.CPF,
                 pj.CNPJ,
                 pj.Razao_Social,

                 COALESCE(pf.CPF, pj.CNPJ) AS Documento,
                 COALESCE(pf.Telefone, pj.Telefone) AS Telefone

             FROM favorecido f
             LEFT JOIN pessoa_fisica pf 
                  ON pf.ID_Favorecido = f.ID_Favorecido
             LEFT JOIN pessoa_juridica pj 
                  ON pj.ID_Favorecido = f.ID_Favorecido
             WHERE f.ID_Usuario = ?
             ORDER BY f.Nome ASC
          """, (id_usuario,))

    # =========================================================
    # OBTER POR ID
    # =========================================================
    def get_favorecido_by_id(self, id_favorecido, id_usuario):
        return self.fetch_one(
            """
            SELECT 
                f.*,
                pf.CPF,
                pj.CNPJ,
                pj.Razao_Social,

                COALESCE(pf.CPF, pj.CNPJ) AS Documento

            FROM favorecido f

            LEFT JOIN pessoa_fisica pf 
                ON pf.ID_Favorecido = f.ID_Favorecido

            LEFT JOIN pessoa_juridica pj 
                ON pj.ID_Favorecido = f.ID_Favorecido

            WHERE f.ID_Favorecido = ? 
              AND f.ID_Usuario = ?
            """,
            (id_favorecido, id_usuario)
        )

    # =========================================================
    # BUSCAR POR NOME (ANTI DUPLICIDADE)
    # =========================================================
    def get_favorecido_by_name(self, nome, id_usuario):
        return self.fetch_one(
            """
            SELECT ID_Favorecido, Nome
            FROM favorecido
            WHERE Nome = ? AND ID_Usuario = ?
            """,
            (nome, id_usuario)
        )

    # =========================================================
    # OBTER TIPO
    # =========================================================
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

    # =========================================================
    # INSERIR (COM VALIDAÇÃO + TRANSAÇÃO)
    # =========================================================
    def add_favorecido(self, dados, id_usuario):

        nome = dados.get("Nome")
        tipo = dados.get("Tipo")

        if not nome:
            raise ValueError("Nome é obrigatório.")

        if tipo not in ("PF", "PJ"):
            raise ValueError("Tipo inválido (PF ou PJ).")

        # valida documento
        if tipo == "PF" and not dados.get("CPF"):
            raise ValueError("CPF é obrigatório para Pessoa Física.")

        if tipo == "PJ" and not dados.get("CNPJ"):
            raise ValueError("CNPJ é obrigatório para Pessoa Jurídica.")

        try:
            # 🔥 TRANSAÇÃO
            self.connection.execute("BEGIN")

            # 1️⃣ inserir base
            self.execute_query(
                """
                INSERT INTO favorecido (Nome, Tipo, Telefone, ID_Usuario)
                VALUES (?, ?, ?, ?)
                """,
                (
                    nome,
                    tipo,
                    dados.get("Telefone"),
                    id_usuario
                )
            )

            row = self.fetch_one("SELECT last_insert_rowid() AS id")
            id_favorecido = row["id"]

            # 2️⃣ inserir específico
            if tipo == "PF":
                self.execute_query(
                    """
                    INSERT INTO pessoa_fisica (ID_Favorecido, CPF)
                    VALUES (?, ?)
                    """,
                    (id_favorecido, dados.get("CPF"))
                )

            elif tipo == "PJ":
                self.execute_query(
                    """
                    INSERT INTO pessoa_juridica (ID_Favorecido, CNPJ, Razao_Social)
                    VALUES (?, ?, ?)
                    """,
                    (
                        id_favorecido,
                        dados.get("CNPJ"),
                        dados.get("Razao_Social")
                    )
                )

            self.connection.commit()
            return id_favorecido

        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(str(e))

    # =========================================================
    # ATUALIZAR (SEGURO)
    # =========================================================
    def update_favorecido(self, id_favorecido, dados, id_usuario):

        try:
            tipo = self.get_tipo(id_favorecido, id_usuario)
            if not tipo:
                raise ValueError("Favorecido não encontrado.")

            self.connection.execute("BEGIN")

            # base
            self.execute_query(
                """
                UPDATE favorecido
                SET Nome = ?, Telefone = ?
                WHERE ID_Favorecido = ? AND ID_Usuario = ?
                """,
                (
                    dados.get("Nome"),
                    dados.get("Telefone"),
                    id_favorecido,
                    id_usuario
                )
            )

            # PF
            if tipo == "PF":
                if "CPF" in dados:
                    self.execute_query(
                        """
                        UPDATE pessoa_fisica
                        SET CPF = ?
                        WHERE ID_Favorecido = ?
                        """,
                        (dados.get("CPF"), id_favorecido)
                    )

            # PJ
            elif tipo == "PJ":
                self.execute_query(
                    """
                    UPDATE pessoa_juridica
                    SET CNPJ = ?, Razao_Social = ?
                    WHERE ID_Favorecido = ?
                    """,
                    (
                        dados.get("CNPJ"),
                        dados.get("Razao_Social"),
                        id_favorecido
                    )
                )

            self.connection.commit()
            return True, "Favorecido atualizado."

        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(str(e))

    # =========================================================
    # DELETE (COM SEGURANÇA)
    # =========================================================
    def delete_favorecido(self, id_favorecido, id_usuario):
        try:
            self.execute_query(
                """
                DELETE FROM favorecido
                WHERE ID_Favorecido = ? AND ID_Usuario = ?
                """
                ,
                (id_favorecido, id_usuario)
            )
            return True
        except Exception as e:
            raise DatabaseError(str(e))