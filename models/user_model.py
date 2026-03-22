import hashlib
import logging
from database.database import Database


class UserModel(Database):

    def __init__(self):
        super().__init__()

    # ==================================================
    # UTILITÁRIOS
    # ==================================================

    def hash_senha(self, senha: str) -> str:
        """
        Retorna o hash SHA-256 da senha.
        (Recomendado futuramente usar bcrypt ou argon2)
        """
        return hashlib.sha256(senha.encode()).hexdigest()

    # ==================================================
    # CRIAÇÃO / AUTENTICAÇÃO
    # ==================================================

    def add_user(self, user_data: dict):

        query = """
        INSERT INTO usuarios (
            Nome, DataNascimento, Sexo, CPF, Telefone, Celular,
            Email, Login, Senha, Nivel_Acesso,
            Tema, Idioma
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        senha_hash = self.hash_senha(user_data["Senha"])

        self.execute_query(query, (
            user_data["Nome"],
            user_data.get("DataNascimento"),
            user_data.get("Sexo"),
            user_data.get("CPF"),
            user_data.get("Telefone"),
            user_data.get("Celular"),
            user_data["Email"],
            user_data["Login"],
            senha_hash,
            user_data.get("Nivel_Acesso", "usuario"),
            user_data.get("Tema", "Claro"),
            user_data.get("Idioma", "pt_BR"),
        ))

    def get_user_by_login(self, login: str):
        query = "SELECT * FROM usuarios WHERE Login = ?"
        return self.fetch_one(query, (login,))

    def authenticate_user(self, login: str, senha_digitada: str):

        usuario = self.get_user_by_login(login)
        if not usuario:
            return None

        senha_hash = self.hash_senha(senha_digitada)

        if usuario["Senha"] == senha_hash:
            return usuario

        return None

    # ==================================================
    # CONSULTAS
    # ==================================================

    def get_all_users(self):
        query = """
        SELECT ID_Usuario, Nome, Email, Login, Nivel_Acesso
        FROM usuarios
        """
        return self.fetch_all(query)

    def get_user_by_id(self, id_usuario: int):
        query = "SELECT * FROM usuarios WHERE ID_Usuario = ?"
        return self.fetch_one(query, (id_usuario,))

    def count_admins(self):
        """
        Retorna quantidade de usuários com nível admin.
        """
        query = """
        SELECT COUNT(*) as total
        FROM usuarios
        WHERE LOWER(Nivel_Acesso) = 'admin'
        """
        resultado = self.fetch_one(query)
        return resultado["total"] if resultado else 0

    # ==================================================
    # ATUALIZAÇÕES
    # ==================================================

    def update_user(self, id_usuario: int, user_data: dict):

        query = """
        UPDATE usuarios
        SET Nome = ?, DataNascimento = ?, Sexo = ?, CPF = ?, Telefone = ?,
            Celular = ?, Email = ?, Login = ?, Nivel_Acesso = ?
        WHERE ID_Usuario = ?
        """

        self.execute_query(query, (
            user_data["Nome"],
            user_data.get("DataNascimento"),
            user_data.get("Sexo"),
            user_data.get("CPF"),
            user_data.get("Telefone"),
            user_data.get("Celular"),
            user_data["Email"],
            user_data["Login"],
            user_data.get("Nivel_Acesso", "usuario"),
            id_usuario
        ))

    def update_access_level(self, id_usuario: int, novo_nivel: str):
        """
        Atualiza apenas nível de acesso.
        """
        query = """
        UPDATE usuarios
        SET Nivel_Acesso = ?
        WHERE ID_Usuario = ?
        """
        self.execute_query(query, (novo_nivel, id_usuario))

    def change_password(self, id_usuario: int, nova_senha: str):

        query = "UPDATE usuarios SET Senha = ? WHERE ID_Usuario = ?"

        nova_senha_hash = self.hash_senha(nova_senha)

        self.execute_query(query, (nova_senha_hash, id_usuario))

    def delete_user(self, id_usuario: int):
        """
        Exclusão física do usuário.
        (Recomendado futuramente usar exclusão lógica)
        """
        query = "DELETE FROM usuarios WHERE ID_Usuario = ?"
        self.execute_query(query, (id_usuario,))

    # ==================================================
    # PREFERÊNCIAS
    # ==================================================

    def update_preferences(self, id_usuario: int, tema: str, idioma: str):

        query = """
        UPDATE usuarios
        SET Tema = ?, Idioma = ?
        WHERE ID_Usuario = ?
        """

        self.execute_query(query, (tema, idioma, id_usuario))

    def get_preferences(self, id_usuario: int):

        query = """
        SELECT Tema, Idioma
        FROM usuarios
        WHERE ID_Usuario = ?
        """

        return self.fetch_one(query, (id_usuario,))

    # ==================================================
    # VALIDAÇÃO
    # ==================================================

    def user_exists(self, login=None, email=None) -> bool:

        try:
            if not login and not email:
                raise ValueError("Login ou email devem ser fornecidos")

            query = """
            SELECT ID_Usuario
            FROM usuarios
            WHERE Login = ? OR Email = ?
            """

            resultado = self.fetch_one(query, (login, email))

            return resultado is not None

        except ValueError:
            raise
        except Exception as exc:
            logging.exception(
                "Erro ao verificar existência de usuário: %s", exc
            )
            return False