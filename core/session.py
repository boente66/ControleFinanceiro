# core/session.py

class Session:
    """
    Estado global da aplicação.

    Responsável por:
    - Usuário logado
    - Configurações globais (idioma, tema, moeda)
    - Notificação de mudanças (idioma / tema)
    """

    # ---------------------------------------
    # ESTADO
    # ---------------------------------------
    usuario = None

    _config_padrao = {
        "idioma": "pt",     # 🔥 PADRÃO CORRETO
        "tema": "Claro",
        "moeda": "BRL"
    }

    configuracoes = _config_padrao.copy()

    # listeners
    _idioma_listeners = []
    _tema_listeners = []

    # ---------------------------------------
    # NORMALIZAÇÃO 🔥 (NOVA)
    # ---------------------------------------
    _idioma_map = {
        "Português": "pt",
        "Inglês": "en",
        "Espanhol": "es",
        "pt": "pt",
        "en": "en",
        "es": "es"
    }

    @classmethod
    def _normalize_idioma(cls, valor):
        return cls._idioma_map.get(valor, "pt")

    # ---------------------------------------
    # USUÁRIO
    # ---------------------------------------
    @classmethod
    def set_usuario(cls, usuario: dict | None):
        cls.usuario = usuario

        if not usuario:
            return

        # 🔥 normaliza antes de aplicar
        if "Idioma" in usuario:
            idioma = cls._normalize_idioma(usuario["Idioma"])
            cls.set_config("idioma", idioma, notify=False)

        if "Tema" in usuario:
            cls.set_config("tema", usuario["Tema"], notify=False)

    @classmethod
    def get_usuario(cls):
        return cls.usuario

    # ---------------------------------------
    # CONFIGURAÇÕES
    # ---------------------------------------
    @classmethod
    def set_config(cls, chave: str, valor, notify: bool = True):

        if chave not in cls._config_padrao:
            return

        # 🔥 NORMALIZA IDIOMA
        if chave == "idioma":
            valor = cls._normalize_idioma(valor)

        cls.configuracoes[chave] = valor

        if not notify:
            return

        if chave == "idioma":
            cls._notify_idioma(valor)

        elif chave == "tema":
            cls._notify_tema(valor)

    @classmethod
    def load_config(cls, config: dict):
        for chave, valor in config.items():
            if chave in cls._config_padrao:

                if chave == "idioma":
                    valor = cls._normalize_idioma(valor)

                cls.configuracoes[chave] = valor

    @classmethod
    def get_config(cls, chave: str, default=None):
        return cls.configuracoes.get(chave, default)

    @classmethod
    def reset_config(cls):
        cls.configuracoes = cls._config_padrao.copy()

    # ---------------------------------------
    # LISTENERS — IDIOMA
    # ---------------------------------------
    @classmethod
    def on_idioma_change(cls, callback):
        if callback not in cls._idioma_listeners:
            cls._idioma_listeners.append(callback)

    @classmethod
    def _notify_idioma(cls, idioma):
        for callback in list(cls._idioma_listeners):
            try:
                callback(idioma)
            except Exception:
                pass

    # ---------------------------------------
    # LISTENERS — TEMA
    # ---------------------------------------
    @classmethod
    def on_tema_change(cls, callback):
        if callback not in cls._tema_listeners:
            cls._tema_listeners.append(callback)

    @classmethod
    def _notify_tema(cls, tema):
        for callback in list(cls._tema_listeners):
            try:
                callback(tema)
            except Exception:
                pass