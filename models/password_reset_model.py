import secrets
from database.database import Database, DatabaseError


class PasswordResetModel(Database):
    """
    Model responsável EXCLUSIVAMENTE pela tabela de recuperação de senha.
    """

    # --------------------------------------------------
    # CRIAR TOKEN DE RECUPERAÇÃO
    # --------------------------------------------------
    def create_token(self, id_usuario: int, minutos_validade: int = 30) -> str:
        """
        Cria um token único para recuperação de senha.
        Retorna o token gerado.
        """
        try:
            token = secrets.token_urlsafe(32)

            sql = """
            INSERT INTO recuperacao_senha (
                ID_Usuario, Token, Expira_Em
            )
            VALUES (
                ?, ?, datetime('now', ?)
            )
            """

            self.execute_query(
                sql,
                (
                    id_usuario,
                    token,
                    f"+{minutos_validade} minutes",
                )
            )

            return token

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                f"Erro ao criar token de recuperação: {e}"
            )

    # --------------------------------------------------
    # BUSCAR TOKEN VÁLIDO
    # --------------------------------------------------
    def get_valid_token(self, token: str):
        """
        Retorna o registro do token se:
        - existir
        - não estiver expirado
        - não estiver usado
        """
        sql = """
        SELECT *
        FROM recuperacao_senha
        WHERE Token = ?
          AND Usado = 0
          AND Expira_Em >= datetime('now')
        """
        return self.fetch_one(sql, (token,))

    # --------------------------------------------------
    # MARCAR TOKEN COMO USADO
    # --------------------------------------------------
    def mark_token_used(self, token: str):
        """
        Marca o token como usado após redefinição de senha.
        """
        sql = """
        UPDATE recuperacao_senha
        SET Usado = 1
        WHERE Token = ?
        """
        self.execute_query(sql, (token,))

    # --------------------------------------------------
    # LIMPAR TOKENS EXPIRADOS (OPCIONAL)
    # --------------------------------------------------
    def cleanup_expired_tokens(self):
        """
        Remove tokens expirados ou já utilizados.
        Pode ser chamado no login ou via rotina.
        """
        sql = """
        DELETE FROM recuperacao_senha
        WHERE Usado = 1
           OR Expira_Em < datetime('now')
        """
        self.execute_query(sql)