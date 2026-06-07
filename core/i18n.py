# core/i18n.py

from core.session import Session

TRADUCOES = {
    "pt": {
        "Configurações": "Configurações",
        "Salvar": "Salvar",
        "Idioma": "Idioma",
        "Tema": "Tema",
        "Moeda": "Moeda"
    },
    "en": {
        "Configurações": "Settings",
        "Salvar": "Save",
        "Idioma": "Language",
        "Tema": "Theme",
        "Moeda": "Currency"
    },
    "es": {
        "Configurações": "Configuraciones",
        "Salvar": "Guardar",
        "Idioma": "Idioma",
        "Tema": "Tema",
        "Moeda": "Moneda"
    }
}

DEFAULT_LANG = "pt"


def _lang_code(idioma: str = None) -> str:
    idioma = idioma or DEFAULT_LANG
    return idioma.replace("-", "_").split("_", 1)[0]


def t(texto: str, idioma: str = None) -> str:
    if not texto:
        return texto

    idioma = _lang_code(
        idioma or Session.get_config("idioma", DEFAULT_LANG)
    )

    return TRADUCOES.get(idioma, {}).get(texto, texto)


def has(texto: str, idioma: str = None) -> bool:
    idioma = _lang_code(
        idioma or Session.get_config("idioma", DEFAULT_LANG)
    )

    return texto in TRADUCOES.get(idioma, {})


def register(idioma: str, chave: str, valor: str):
    idioma = _lang_code(idioma)

    if idioma not in TRADUCOES:
        TRADUCOES[idioma] = {}

    TRADUCOES[idioma][chave] = valor


def get_language_dict(idioma: str) -> dict:
    idioma = _lang_code(idioma)
    return TRADUCOES.get(idioma, {})


def idiomas_disponiveis():
    return list(TRADUCOES.keys())