# -*- coding: utf-8 -*-
import secrets
from database.database import Database, DatabaseError


class PasswordResetModel(Database):
    """
    Model responsável exclusivamente pela tabela recuperacao_senha.

    Responsabilidades:
    - criar token de recuperação
    - validar token ativo
    - marcar token como utilizado
    - limpar tokens expirados/usados
    """

    # --------------------------------------------------
    # CRIAR TOKEN DE RECUPERAÇÃO
    # --------------------------------------------------
    def create_token(self, id_usuario: int, minutos_validade: int = 30) -> str:
        """
        Cria um token único para recuperação de senha.
        Retorna o token gerado.
        """

        if not id_usuario:
            raise ValueError("Usuário inválido.")

        try:
            token = secrets.token_urlsafe(32)

            sql = """
                INSERT INTO recuperacao_senha (
                    ID_Usuario,
                    Token,
                    Expira_Em,
                    Utilizado
                )
                VALUES (
                    ?,
                    ?,
                    datetime('now', ?),
                    0
                )
            """

            self.execute_query(
                sql,
                (
                    id_usuario,
                    token,
                    f"+{int(minutos_validade)} minutes",
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
        - não estiver utilizado
        """

        if not token:
            return None

        sql = """
            SELECT *
            FROM recuperacao_senha
            WHERE Token = ?
              AND Utilizado = 0
              AND Expira_Em >= datetime('now')
            LIMIT 1
        """

        return self.fetch_one(sql, (token,))

    # --------------------------------------------------
    # MARCAR TOKEN COMO UTILIZADO
    # --------------------------------------------------
    def mark_token_used(self, token: str) -> bool:
        """
        Marca o token como utilizado após redefinição de senha.
        """

        if not token:
            raise ValueError("Token inválido.")

        sql = """
            UPDATE recuperacao_senha
            SET Utilizado = 1
            WHERE Token = ?
              AND Utilizado = 0
        """

        self.execute_query(sql, (token,))
        return True

    # --------------------------------------------------
    # INVALIDAR TOKENS DO USUÁRIO
    # --------------------------------------------------
    def invalidate_user_tokens(self, id_usuario: int) -> bool:
        """
        Marca todos os tokens ativos do usuário como utilizados.
        Útil antes de criar um novo token.
        """

        if not id_usuario:
            raise ValueError("Usuário inválido.")

        sql = """
            UPDATE recuperacao_senha
            SET Utilizado = 1
            WHERE ID_Usuario = ?
              AND Utilizado = 0
        """

        self.execute_query(sql, (id_usuario,))
        return True

    # --------------------------------------------------
    # LIMPAR TOKENS EXPIRADOS OU UTILIZADOS
    # --------------------------------------------------
    def cleanup_expired_tokens(self) -> bool:
        """
        Remove tokens expirados ou já utilizados.
        Pode ser chamado no login ou na abertura do sistema.
        """

        sql = """
            DELETE FROM recuperacao_senha
            WHERE Utilizado = 1
               OR Expira_Em < datetime('now')
        """

        self.execute_query(sql)
        return True

    # --------------------------------------------------
    # BUSCAR ÚLTIMO TOKEN DO USUÁRIO
    # --------------------------------------------------
    def get_last_token_by_user(self, id_usuario: int):
        """
        Retorna o último token criado para o usuário.
        """

        if not id_usuario:
            return None

        sql = """
            SELECT *
            FROM recuperacao_senha
            WHERE ID_Usuario = ?
            ORDER BY Criado_Em DESC, ID_Recuperacao DESC
            LIMIT 1
        """

        return self.fetch_one(sql, (id_usuario,))