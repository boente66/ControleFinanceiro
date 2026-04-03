# =========================================================
# SISTEMA DE TEMAS PROFISSIONAL (SIMPLIFICADO + UX)
# =========================================================

from core.session import Session

# =========================================================
# BASE
# =========================================================
BASE = """
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QToolTip {
    padding: 6px;
    border-radius: 6px;
    color: #fff;
    background-color: rgba(0,0,0,0.75);
}
"""

# =========================================================
# TOKENS
# =========================================================
V = {
    "bg_light": "#f4f6f9",
    "bg_dark": "#0f1720",

    "panel_light": "#ffffff",
    "panel_dark": "#121214",

    "card_light": "#fbfdff",
    "card_dark": "#151515",

    "sidebar_dark_green": "#14532d",

    "border_light": "#e6e9ee",
    "border_dark": "#2a2f3a",

    "text_light": "#111827",
    "text_dark": "#e6eef8",

    "primary_blue": "#2563eb",
    "primary_dark": "#3aa0ff",

    "green": "#16a34a",
    "green_hover": "#15803d",

    "success": "#16a34a",
    "danger": "#dc2626",

    "highlight_light": "#f3f4f6",
    "highlight_dark": "#222831",
}

# =========================================================
# HELPERS
# =========================================================
def _table(tokens):
    return f"""
QTableWidget {{
    background-color: {tokens['card']};
    color: {tokens['text']};
    border-radius: 8px;
}}

QHeaderView::section {{
    background-color: {tokens['highlight']};
    padding: 6px;
}}

QTableWidget::item:selected {{
    background-color: {tokens['primary']};
    color: #fff;
}}
"""

# =========================================================
# 🎨 TEMA CLARO
# =========================================================
def tema_claro():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_light']};
    color: {V['text_light']};
}}

QWidget#sidebar {{
    background-color: #111827;
}}

QPushButton {{
    background-color: {V['primary_blue']};
    color: white;
    padding: 8px;
    border-radius: 8px;
}}

QPushButton:hover {{
    background-color: #1d4ed8;
}}

QLineEdit, QComboBox {{
    background: {V['panel_light']};
    border: 1px solid {V['border_light']};
    padding: 6px;
}}

QProgressBar::chunk {{
    background-color: {V['green']};
}}

{_table({
    "card": V['card_light'],
    "text": V['text_light'],
    "highlight": V['highlight_light'],
    "primary": V['primary_blue']
})}

QLabel#positivo {{ color: {V['success']}; font-weight: bold; }}
QLabel#negativo {{ color: {V['danger']}; font-weight: bold; }}
"""

# =========================================================
# 🌙 TEMA ESCURO
# =========================================================
def tema_escuro():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_dark']};
    color: {V['text_dark']};
}}

QWidget#sidebar {{
    background-color: #1f2330;
}}

QPushButton {{
    background-color: {V['primary_dark']};
    color: white;
    padding: 8px;
    border-radius: 8px;
}}

QPushButton:hover {{
    background-color: #2a6ef6;
}}

QLineEdit, QComboBox {{
    background: {V['panel_dark']};
    border: 1px solid {V['border_dark']};
    padding: 6px;
}}

QProgressBar::chunk {{
    background-color: #0ea5e9;
}}

{_table({
    "card": V['card_dark'],
    "text": V['text_dark'],
    "highlight": V['highlight_dark'],
    "primary": V['primary_dark']
})}

QLabel#positivo {{ color: #22c55e; font-weight: bold; }}
QLabel#negativo {{ color: #ef4444; font-weight: bold; }}
"""

# =========================================================
# 💚 TEMA VERDE (SEU DIFERENCIAL)
# =========================================================
def tema_verde():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_light']};
    color: {V['text_light']};
}}

QWidget#sidebar {{
    background-color: {V['sidebar_dark_green']};
    border-right: 3px solid {V['green']};
}}

QPushButton {{
    background-color: {V['green']};
    color: white;
    padding: 8px;
    border-radius: 8px;
}}

QPushButton:hover {{
    background-color: {V['green_hover']};
}}

QLineEdit, QComboBox {{
    background: white;
    border: 1px solid {V['green']};
    padding: 6px;
}}

QProgressBar::chunk {{
    background-color: {V['green']};
}}

{_table({
    "card": V['card_light'],
    "text": V['text_light'],
    "highlight": V['highlight_light'],
    "primary": V['green']
})}

QLabel#positivo {{ color: {V['green']}; font-weight: bold; }}
QLabel#negativo {{ color: {V['danger']}; font-weight: bold; }}
"""

# =========================================================
# REGISTRO (UX SIMPLES)
# =========================================================
THEMES = {
    "Claro": tema_claro,
    "Escuro": tema_escuro,
    "Verde": tema_verde,
}

DEFAULT_THEME = "Claro"

# =========================================================
# CORE
# =========================================================
def get_theme(nome: str = None) -> str:
    nome = nome or Session.get_config("tema", DEFAULT_THEME)
    builder = THEMES.get(nome, tema_claro)
    return builder()


def apply_theme(app, nome: str = None):
    """
    Aplica tema no app inteiro (QApplication)
    """
    nome = nome or DEFAULT_THEME

    Session.set_config("tema", nome)

    css = get_theme(nome)
    app.setStyleSheet(css)


def current_theme():
    return Session.get_config("tema", DEFAULT_THEME)


def available_themes():
    return list(THEMES.keys())


def register_theme(nome: str, builder):
    if not nome or not callable(builder):
        return

    THEMES[nome] = builder
