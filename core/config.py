import json
import os
import sys

# ==========================================================
# IDENTIFICAÇÃO DO AMBIENTE (DEV OU EXECUTÁVEL)
# ==========================================================

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_base_path()

# ==========================================================
# DIRETÓRIO DE DADOS DO USUÁRIO
# ==========================================================

def get_app_data_dir():
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, ".financeassist")

    os.makedirs(app_dir, exist_ok=True)

    return app_dir


if getattr(sys, "frozen", False):
    DATA_DIR = get_app_data_dir()
else:
    DATA_DIR = BASE_DIR


# ==========================================================
# BANCO
# ==========================================================

DB_NAME = "financeiro.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# ==========================================================
# NORMALIZAÇÃO DE IDIOMA 🔥
# ==========================================================

IDIOMA_MAP = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "pt": "pt",
    "en": "en",
    "es": "es"
}

def _normalize_idioma(valor):
    return IDIOMA_MAP.get(valor, "pt")


# ==========================================================
# CONFIG PADRÃO
# ==========================================================

DEFAULTS = {
    "idioma": "pt",   # 🔥 PADRÃO CORRETO
    "tema": "Claro",
    "moeda": "BRL"
}

CONFIG_PATH = os.path.join(DATA_DIR, "configuracoes.json")


# ==========================================================
# CARREGAR CONFIG
# ==========================================================

def carregar_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULTS.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        cfg = DEFAULTS.copy()
        cfg.update(data)

        # 🔥 normaliza idioma automaticamente
        cfg["idioma"] = _normalize_idioma(cfg.get("idioma"))

        return cfg

    except Exception:
        return DEFAULTS.copy()


# ==========================================================
# SALVAR CONFIG
# ==========================================================

def salvar_config(config: dict):

    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        config = config.copy()

        # 🔥 garante padrão correto
        config["idioma"] = _normalize_idioma(config.get("idioma"))

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    except Exception:
        pass
