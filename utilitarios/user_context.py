# utilitarios/user_context.py
class UserContext:
    _usuario = None

    @classmethod
    def set_usuario(cls, usuario: dict):
        cls._usuario = usuario

    @classmethod
    def get_usuario(cls):
        if not cls._usuario:
            raise RuntimeError("Usuário não autenticado.")
        return cls._usuario

    @classmethod
    def get_user_id(cls):
        return cls.get_usuario()["ID_Usuario"]

    @classmethod
    def clear(cls):
        cls._usuario = None