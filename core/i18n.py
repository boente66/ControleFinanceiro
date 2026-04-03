# core/i18n.py

from core.session import Session

# ======================================================
# TRADUÇÕES BASE (USANDO CÓDIGO DE IDIOMA)
# ======================================================
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


# ======================================================
# CORE
# ======================================================
def t(texto: str, idioma: str = None) -> str:
    """
    Tradução principal

    - Usa idioma atual da Session se não for passado
    - Fallback seguro
    """

    if not texto:
        return texto

    idioma = idioma or Session.get_config("idioma", DEFAULT_LANG)

    try:
        return TRADUCOES.get(idioma, {}).get(texto, texto)
    except Exception:
        return texto


# ======================================================
# VERIFICA SE EXISTE
# ======================================================
def has(texto: str, idioma: str = None) -> bool:
    idioma = idioma or Session.get_config("idioma", DEFAULT_LANG)
    return texto in TRADUCOES.get(idioma, {})


# ======================================================
# REGISTRAR NOVAS TRADUÇÕES
# ======================================================
def register(idioma: str, chave: str, valor: str):
    if idioma not in TRADUCOES:
        TRADUCOES[idioma] = {}

    TRADUCOES[idioma][chave] = valor


# ======================================================
# LISTAR IDIOMAS DISPONÍVEIS
# ======================================================
def idiomas_disponiveis():
    return list(TRADUCOES.keys())