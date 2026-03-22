import json
import os
import sys

# ==========================================================
# IDENTIFICAÇÃO DO AMBIENTE (DEV OU EXECUTÁVEL)
# ==========================================================

def get_base_path():
    """
    Retorna o diretório base correto:
    - Executável → pasta do executável
    - Desenvolvimento → pasta raiz do projeto
    """

    if getattr(sys, "frozen", False):
        # Executável (PyInstaller, cx_Freeze, Nuitka)
        return os.path.dirname(sys.executable)

    # Desenvolvimento
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_base_path()

# ==========================================================
# DIRETÓRIO DE DADOS DO USUÁRIO (MODO PRODUÇÃO)
# ==========================================================

def get_app_data_dir():
    """
    Cria pasta oculta no diretório do usuário:
    ~/.financeassist
    """

    home = os.path.expanduser("~")
    app_dir = os.path.join(home, ".financeassist")

    os.makedirs(app_dir, exist_ok=True)

    return app_dir


# Se for executável → usa pasta do usuário
# Se for desenvolvimento → usa raiz do projeto
if getattr(sys, "frozen", False):
    DATA_DIR = get_app_data_dir()
else:
    DATA_DIR = BASE_DIR


# ==========================================================
# BANCO DE DADOS
# ==========================================================

DB_NAME = "financeiro.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

CONFIG_PATH = os.path.join(DATA_DIR, "configuracoes.json")

DEFAULTS = {
    "idioma": "Português",
    "tema": "Claro",
    "moeda": "BRL"
}


def carregar_config():
    """
    Carrega configurações do usuário.
    Se não existir, retorna padrão.
    """

    if not os.path.exists(CONFIG_PATH):
        return DEFAULTS.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        cfg = DEFAULTS.copy()
        cfg.update(data)

        return cfg

    except Exception:
        return DEFAULTS.copy()


def salvar_config(config: dict):
    """
    Salva configurações no diretório correto.
    """

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
