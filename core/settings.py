# core/settings.py

import json
import os

# ---------------------------------------
# ARQUIVO DE CONFIGURAÇÃO
# ---------------------------------------
ARQUIVO_CONFIG = "configuracoes.json"

# ---------------------------------------
# NORMALIZAÇÃO DE IDIOMA 🔥
# ---------------------------------------
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


# ---------------------------------------
# CONFIGURAÇÕES PADRÃO
# ---------------------------------------
CONFIG_PADRAO = {
    "idioma": "pt",   # 🔥 corrigido
    "tema": "Claro",
    "moeda": "BRL"
}

# ---------------------------------------
# CARREGAR CONFIGURAÇÕES
# ---------------------------------------
def carregar_config() -> dict:
    """
    Carrega configurações do JSON
    - aplica defaults
    - normaliza idioma
    """

    if not os.path.exists(ARQUIVO_CONFIG):
        return CONFIG_PADRAO.copy()

    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            dados = json.load(f)

        config = CONFIG_PADRAO.copy()
        config.update(dados)

        # 🔥 normalização automática
        config["idioma"] = _normalize_idioma(config.get("idioma"))

        return config

    except (json.JSONDecodeError, OSError):
        return CONFIG_PADRAO.copy()


# ---------------------------------------
# SALVAR CONFIGURAÇÕES
# ---------------------------------------
def salvar_config(config: dict):
    """
    Salva configurações no JSON
    - garante padrão correto antes de salvar
    """

    try:
        config = config.copy()

        # 🔥 garante idioma correto
        config["idioma"] = _normalize_idioma(config.get("idioma"))

        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )

    except OSError:
        pass