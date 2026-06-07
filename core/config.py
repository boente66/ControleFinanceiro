# -*- coding: utf-8 -*-
import os
import sys

from database.json_database import JsonDatabase


# ==========================================================
# IDENTIFICAÇÃO DO AMBIENTE
# ==========================================================
def get_base_path():
    """
    Retorna a pasta base da aplicação.

    - Em desenvolvimento: raiz do projeto.
    - Em executável: pasta onde está o binário.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


BASE_DIR = get_base_path()


# ==========================================================
# DIRETÓRIO DE DADOS DO USUÁRIO
# ==========================================================
def get_app_data_dir():
    """
    Diretório gravável do usuário.

    Usado principalmente quando o sistema estiver empacotado
    em .deb ou executável.
    """
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, ".financeassist")

    os.makedirs(app_dir, exist_ok=True)

    return app_dir


if getattr(sys, "frozen", False):
    DATA_DIR = get_app_data_dir()
else:
    DATA_DIR = BASE_DIR


# ==========================================================
# NORMALIZAÇÃO DE IDIOMA
# ==========================================================
IDIOMA_MAP = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "pt": "pt",
    "pt_BR": "pt",
    "pt-BR": "pt",
    "en": "en",
    "en_US": "en",
    "en-US": "en",
    "es": "es",
    "es_ES": "es",
    "es-ES": "es",
}


def _normalize_idioma(valor):
    return IDIOMA_MAP.get(valor, "pt")


# ==========================================================
# CONFIG PADRÃO
# ==========================================================
DB_NAME = "financeiro.db"
DEFAULT_DB_PATH = os.path.join(DATA_DIR, DB_NAME)

DEFAULTS = {
    "idioma": "pt",
    "tema": "Claro",
    "moeda": "BRL",
    "db_path": DEFAULT_DB_PATH,
}

CONFIG_PATH = os.path.join(DATA_DIR, "configuracoes.json")


# ==========================================================
# PERSISTÊNCIA JSON
# ==========================================================
_config_db = JsonDatabase(
    file_path=CONFIG_PATH,
    default_data=DEFAULTS
)


# ==========================================================
# NORMALIZAÇÃO DE CONFIG
# ==========================================================
def _normalizar_config(config: dict) -> dict:
    cfg = DEFAULTS.copy()

    if isinstance(config, dict):
        cfg.update(config)

    cfg["idioma"] = _normalize_idioma(
        cfg.get("idioma")
    )

    if not cfg.get("tema"):
        cfg["tema"] = "Claro"

    if not cfg.get("moeda"):
        cfg["moeda"] = "BRL"

    if not cfg.get("db_path"):
        cfg["db_path"] = DEFAULT_DB_PATH

    cfg["db_path"] = os.path.expanduser(
        str(cfg["db_path"])
    )

    return cfg


# ==========================================================
# CARREGAR CONFIG
# ==========================================================
def carregar_config():
    try:
        data = _config_db.load()
        return _normalizar_config(data)

    except Exception:
        return DEFAULTS.copy()


# ==========================================================
# SALVAR CONFIG
# ==========================================================
def salvar_config(config: dict):
    try:
        cfg = _normalizar_config(config)
        return _config_db.save(cfg)

    except Exception:
        return False


# ==========================================================
# BANCO
# ==========================================================
def get_db_path():
    """
    Retorna o caminho atual do banco.

    Permite usar:
    - padrão local da aplicação
    - caminho customizado no configuracoes.json
    - OneDrive / pasta externa
    """
    config = carregar_config()
    return config.get("db_path", DEFAULT_DB_PATH)


DB_PATH = get_db_path()
