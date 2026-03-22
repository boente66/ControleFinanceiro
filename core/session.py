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
        "idioma": "Português",
        "tema": "Claro",
        "moeda": "BRL"
    }

    configuracoes = _config_padrao.copy()

    # listeners
    _idioma_listeners = []
    _tema_listeners = []

    # ---------------------------------------
    # USUÁRIO
    # ---------------------------------------
    @classmethod
    def set_usuario(cls, usuario: dict | None):
        """
        Define usuário logado e aplica preferências, se existirem.
        """
        cls.usuario = usuario

        if not usuario:
            return

        # aplica preferências do banco, sem notificar (startup)
        if "Idioma" in usuario:
            cls.set_config("idioma", usuario["Idioma"], notify=False)

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
        """
        Atualiza configuração global.
        notify=True dispara eventos visuais.
        """
        if chave not in cls._config_padrao:
            return  # ignora chaves inválidas

        cls.configuracoes[chave] = valor

        if not notify:
            return

        if chave == "idioma":
            cls._notify_idioma(valor)

        elif chave == "tema":
            cls._notify_tema(valor)

    @classmethod
    def load_config(cls, config: dict):
        """
        Carrega configurações persistidas (JSON / DB).
        Não dispara eventos.
        """
        for chave, valor in config.items():
            if chave in cls._config_padrao:
                cls.configuracoes[chave] = valor

    @classmethod
    def get_config(cls, chave: str, default=None):
        return cls.configuracoes.get(chave, default)

    @classmethod
    def reset_config(cls):
        """
        Restaura configurações padrão.
        """
        cls.configuracoes = cls._config_padrao.copy()

    # ---------------------------------------
    # LISTENERS — IDIOMA
    # ---------------------------------------
    @classmethod
    def on_idioma_change(cls, callback):
        """
        Registra callback para mudança de idioma.
        callback(idioma)
        """
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
        """
        Registra callback para mudança de tema.
        callback(tema)
        """
        if callback not in cls._tema_listeners:
            cls._tema_listeners.append(callback)

    @classmethod
    def _notify_tema(cls, tema):
        for callback in list(cls._tema_listeners):
            try:
                callback(tema)
            except Exception:
                pass