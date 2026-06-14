# -*- coding: utf-8 -*-

from database.json_database import JsonDatabase


# ==================================================
# ARQUIVO
# ==================================================
ARQUIVO_CONFIG = "configuracoes.json"


# ==================================================
# IDIOMAS
# ==================================================
IDIOMA_MAP = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",

    "pt": "pt",
    "en": "en",
    "es": "es",

    "pt_BR": "pt",
    "pt-BR": "pt",

    "en_US": "en",
    "en-US": "en",

    "es_ES": "es",
    "es-ES": "es",
}


def normalizar_idioma(valor):
    return IDIOMA_MAP.get(valor, "pt")


# ==================================================
# PADRÃO
# ==================================================
CONFIG_PADRAO = {
    "idioma": "pt",
    "tema": "Claro",
    "moeda": "BRL",
    "db_path": "financeiro.db",
}


# ==================================================
# PERSISTÊNCIA
# ==================================================
_db = JsonDatabase(
    ARQUIVO_CONFIG,
    default_data=CONFIG_PADRAO.copy()
)


# ==================================================
# HELPERS
# ==================================================
def _normalizar_config(config):
    cfg = CONFIG_PADRAO.copy()

    if isinstance(config, dict):
        cfg.update(config)

    cfg["idioma"] = normalizar_idioma(
        cfg.get("idioma")
    )

    return cfg


# ==================================================
# LOAD
# ==================================================
def carregar_config():
    try:
        config = _db.load()

        return _normalizar_config(config)

    except Exception:
        return CONFIG_PADRAO.copy()


# ==================================================
# SAVE
# ==================================================
def salvar_config(config):
    try:
        cfg = _normalizar_config(config)

        return _db.save(cfg)

    except Exception:
        return False