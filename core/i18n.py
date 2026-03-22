# core/i18n.py

TRADUCOES = {
    "Português": {
        "Configurações": "Configurações",
        "Salvar": "Salvar",
        "Idioma": "Idioma",
        "Tema": "Tema",
        "Moeda": "Moeda"
    },
    "Inglês": {
        "Configurações": "Settings",
        "Salvar": "Save",
        "Idioma": "Language",
        "Tema": "Theme",
        "Moeda": "Currency"
    }
}

def t(texto, config):
    idioma = getattr(config, "idioma", "Português")
    return TRADUCOES.get(idioma, {}).get(texto, texto)