# core/settings.py

import json
import os

# ---------------------------------------
# ARQUIVO DE CONFIGURAÇÃO
# ---------------------------------------
ARQUIVO_CONFIG = "configuracoes.json"

# ---------------------------------------
# CONFIGURAÇÕES PADRÃO
# ---------------------------------------
CONFIG_PADRAO = {
    "idioma": "Português",
    "tema": "Claro",
    "moeda": "BRL"
}

# ---------------------------------------
# CARREGAR CONFIGURAÇÕES
# ---------------------------------------
def carregar_config() -> dict:
    """
    Carrega configurações do arquivo JSON.
    Retorna sempre um dicionário válido com defaults aplicados.
    """
    if not os.path.exists(ARQUIVO_CONFIG):
        return CONFIG_PADRAO.copy()

    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # garante chaves obrigatórias
        config = CONFIG_PADRAO.copy()
        config.update(dados)

        return config

    except (json.JSONDecodeError, OSError):
        # arquivo corrompido → volta para padrão
        return CONFIG_PADRAO.copy()

# ---------------------------------------
# SALVAR CONFIGURAÇÕES
# ---------------------------------------
def salvar_config(config: dict):
    """
    Salva configurações no arquivo JSON.
    """
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )
    except OSError:
        # erro de escrita → silencioso (não quebra app)
        pass